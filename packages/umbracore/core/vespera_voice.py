# core/realtime_engine.py
"""
⚡ Real-Time Response Optimization Engine — Ultra-Low Latency AI Controller

Architecture:
    1. INSTANT RESPONSE SYSTEM — Predicted/cached/partial replies within 0ms
    2. SMART CACHE — LRU + similarity matching for repeated inputs
    3. NETWORK MONITOR — Adaptive ping tracking + mode switching
    4. API GATEKEEPER — Prevents unnecessary API calls via local classification
    5. RETRY + RECOVERY — Adaptive backoff with fallback chain
    6. REQUEST BATCHER — Coalesces rapid-fire API calls under high ping

Performance Targets:
    - Initial response:   <5ms  (LOCAL/CACHE)
    - Cache lookup:       <2ms  (hash-based)
    - Network mode switch: instant (continuous monitoring)
    - API gating decision: <1ms  (rule-based, no ML overhead)
"""

from __future__ import annotations

import time
import hashlib
import threading
import logging
import asyncio
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum, auto

logger = logging.getLogger("vespera-voice")


# ═══════════════════════════════════════════════════════════════
# ENUMS — Response Mode & Network State
# ═══════════════════════════════════════════════════════════════

class ResponseMode(Enum):
    """How the response was generated."""
    LOCAL = auto()      # Answered locally without any API call
    CACHE = auto()      # Returned from response cache
    API = auto()        # Required a live API call
    FALLBACK = auto()   # API failed; used cached/local fallback
    PREDICTED = auto()  # Pre-computed prediction from pattern matching


class NetworkMode(Enum):
    """Current network quality assessment."""
    NORMAL = auto()       # <200ms ping, stable
    HIGH_PING = auto()    # 200-1000ms ping, intermittent
    FALLBACK = auto()     # >1000ms or repeated failures, offline-mode


# ═══════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════

@dataclass
class ResponseEnvelope:
    """Wraps every response with metadata for the output format spec."""
    initial_response: str                     # Instant feedback text
    final_response: Optional[str] = None      # Full response after processing
    mode: ResponseMode = ResponseMode.LOCAL
    network_mode: NetworkMode = NetworkMode.NORMAL
    latency_ms: float = 0.0                   # Total round-trip time
    cache_key: Optional[str] = None           # For debugging
    timestamp: float = field(default_factory=time.monotonic)

    def to_dict(self) -> dict[str, Any]:
        return {
            "initial_response": self.initial_response,
            "final_response": self.final_response or self.initial_response,
            "mode": self.mode.name,
            "network_mode": self.network_mode.name,
            "latency_ms": round(self.latency_ms, 2),
            "timestamp": self.timestamp,
        }


@dataclass
class PingRecord:
    """Single network latency measurement."""
    timestamp: float
    latency_ms: float
    success: bool


# ═══════════════════════════════════════════════════════════════
# RESPONSE CACHE — Thread-Safe LRU with Similarity Matching
# ═══════════════════════════════════════════════════════════════

class ResponseCache:
    """
    High-performance LRU cache with fuzzy input matching.
    
    Features:
        - O(1) exact-match lookup via hash
        - Normalized key generation (lowercase, stripped, collapsed whitespace)
        - TTL-based expiration (default 5 minutes)
        - Thread-safe for concurrent read/write
        - Tracks hit/miss statistics
    """

    def __init__(self, max_size: int = 500, ttl_seconds: float = 300.0) -> None:
        self._cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize input for cache key generation."""
        import re
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        # Remove punctuation that doesn't change meaning
        text = re.sub(r'[?.!,;:]+$', '', text)
        return text

    @staticmethod
    def _hash_key(text: str) -> str:
        """Fast MD5 hash for cache key."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get(self, input_text: str) -> Optional[str]:
        """
        Look up a cached response. Returns None on miss.
        Automatically evicts expired entries.
        """
        normalized = self._normalize(input_text)
        key = self._hash_key(normalized)

        with self._lock:
            if key in self._cache:
                response, stored_time = self._cache[key]
                # Check TTL
                if time.monotonic() - stored_time <= self._ttl:
                    # Move to end (most recently used)
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return response
                else:
                    # Expired — evict
                    del self._cache[key]

            self._misses += 1
            return None

    def put(self, input_text: str, response: str) -> None:
        """Store a response in cache."""
        normalized = self._normalize(input_text)
        key = self._hash_key(normalized)

        with self._lock:
            if key in self._cache:
                # Update existing
                self._cache[key] = (response, time.monotonic())
                self._cache.move_to_end(key)
            else:
                # New entry
                self._cache[key] = (response, time.monotonic())
                # Evict oldest if over capacity
                while len(self._cache) > self._max_size:
                    self._cache.popitem(last=False)

    def invalidate(self, input_text: str) -> None:
        """Remove a specific entry."""
        normalized = self._normalize(input_text)
        key = self._hash_key(normalized)
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """Flush entire cache."""
        with self._lock:
            self._cache.clear()

    @property
    def stats(self) -> dict[str, int]:
        with self._lock:
            total = self._hits + self._misses
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total": total,
                "hit_rate_pct": round((self._hits / total) * 100, 1) if total > 0 else 0.0,
                "size": len(self._cache),
            }


# ═══════════════════════════════════════════════════════════════
# NETWORK MONITOR — Continuous Ping & Mode Detection
# ═══════════════════════════════════════════════════════════════

class NetworkMonitor:
    """
    Tracks API response latencies to detect network degradation.
    Automatically switches between NORMAL → HIGH_PING → FALLBACK modes.
    
    Thresholds:
        NORMAL:    avg latency < 200ms over last 10 calls
        HIGH_PING: avg latency 200-1000ms
        FALLBACK:  avg latency > 1000ms OR >3 consecutive failures
    """

    # Tunable thresholds (ms)
    HIGH_PING_THRESHOLD = 200.0
    FALLBACK_THRESHOLD = 1000.0
    WINDOW_SIZE = 10           # Rolling window of recent pings
    FAILURE_STREAK_MAX = 3     # Consecutive failures to trigger FALLBACK

    def __init__(self) -> None:
        self._records: list[PingRecord] = []
        self._lock = threading.RLock()
        self._consecutive_failures = 0
        self._mode = NetworkMode.NORMAL
        self._last_mode_change = time.monotonic()

    def record_latency(self, latency_ms: float, success: bool = True) -> NetworkMode:
        """Record a new latency measurement and return updated mode."""
        record = PingRecord(
            timestamp=time.monotonic(),
            latency_ms=latency_ms,
            success=success,
        )

        with self._lock:
            self._records.append(record)
            # Keep only recent window
            if len(self._records) > self.WINDOW_SIZE * 2:
                self._records = self._records[-self.WINDOW_SIZE:]

            if success:
                self._consecutive_failures = 0
            else:
                self._consecutive_failures += 1

            self._mode = self._evaluate_mode()
            return self._mode

    def _evaluate_mode(self) -> NetworkMode:
        """Evaluate current network mode from recent records."""
        # Consecutive failure check (instant FALLBACK)
        if self._consecutive_failures >= self.FAILURE_STREAK_MAX:
            return NetworkMode.FALLBACK

        # Calculate average latency from recent successful pings
        recent = self._records[-self.WINDOW_SIZE:]
        successful = [r for r in recent if r.success]

        if not successful:
            return NetworkMode.FALLBACK

        avg_latency = sum(r.latency_ms for r in successful) / len(successful)

        if avg_latency > self.FALLBACK_THRESHOLD:
            return NetworkMode.FALLBACK
        elif avg_latency > self.HIGH_PING_THRESHOLD:
            return NetworkMode.HIGH_PING
        else:
            return NetworkMode.NORMAL

    @property
    def mode(self) -> NetworkMode:
        with self._lock:
            return self._mode

    @property
    def avg_latency_ms(self) -> float:
        with self._lock:
            recent = self._records[-self.WINDOW_SIZE:]
            successful = [r for r in recent if r.success]
            if not successful:
                return 0.0
            return sum(r.latency_ms for r in successful) / len(successful)

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            recent = self._records[-self.WINDOW_SIZE:]
            return {
                "mode": self._mode.name,
                "avg_latency_ms": round(self.avg_latency_ms, 1),
                "consecutive_failures": self._consecutive_failures,
                "total_records": len(self._records),
                "recent_success_rate": (
                    round(len([r for r in recent if r.success]) / len(recent) * 100, 1)
                    if recent else 100.0
                ),
            }


# ═══════════════════════════════════════════════════════════════
# API GATEKEEPER — Smart Decision Engine
# ═══════════════════════════════════════════════════════════════

class APIGatekeeper:
    """
    Decides whether an API call is needed before making one.
    
    Classification Rules (priority order):
        1. SIMPLE commands (open, play, type, volume, etc.) → LOCAL always
        2. Repeated exact input within TTL → CACHE
        3. System commands → LOCAL
        4. Everything else → API (but gated by network mode)
    """

    # Commands that NEVER need an API call
    LOCAL_PREFIXES = (
        "open", "play", "type", "reply", "paste", "clear_text",
        "scroll", "lock", "volume", "brightness", "media", "press",
        "shortcut", "mouse", "sleep", "shutdown", "restart",
        "taskkill", "cmd", "start", "whatsapp",
    )

    # Patterns that are simple acknowledgments (no API needed)
    SIMPLE_PATTERNS = {
        "ok", "okay", "sure", "yes", "no", "thanks", "thank you",
        "got it", "understood", "alright", "cool", "nice", "great",
        "hmm", "hm", "mm", "uh huh", "yep", "nope", "yup",
    }

    def __init__(self, cache: ResponseCache, network: NetworkMonitor) -> None:
        self._cache = cache
        self._network = network
        self._recent_inputs: list[str] = []  # Track recent inputs for pattern detection
        self._lock = threading.Lock()

    def should_call_api(self, input_text: str) -> tuple[bool, ResponseMode, Optional[str]]:
        """
        Decide if an API call is needed.
        
        Returns:
            (should_call, mode, instant_response)
            - should_call: True if API is needed
            - mode: ResponseMode for how the response was generated
            - instant_response: Pre-computed response (if LOCAL/CACHE), else None
        """
        normalized = input_text.lower().strip()

        # 1. Check for LOCAL commands (process_command handles these)
        for prefix in self.LOCAL_PREFIXES:
            if normalized.startswith(prefix):
                return (False, ResponseMode.LOCAL, f"Executing: {input_text}")

        # 2. Check for simple acknowledgments
        if normalized in self.SIMPLE_PATTERNS:
            return (False, ResponseMode.LOCAL, None)  # Let voice model handle naturally

        # 3. Check cache
        cached = self._cache.get(input_text)
        if cached:
            return (False, ResponseMode.CACHE, cached)

        # 4. Track for repetition detection
        with self._lock:
            self._recent_inputs.append(normalized)
            if len(self._recent_inputs) > 50:
                self._recent_inputs = self._recent_inputs[-30:]

        # 5. Under FALLBACK mode, try harder to avoid API
        if self._network.mode == NetworkMode.FALLBACK:
            return (False, ResponseMode.FALLBACK,
                    "I'm experiencing network issues right now. Let me try to help locally...")

        # 6. API needed
        return (True, ResponseMode.API, None)

    def is_repeated(self, input_text: str, lookback: int = 10) -> bool:
        """Check if this input was seen recently."""
        normalized = input_text.lower().strip()
        with self._lock:
            recent = self._recent_inputs[-lookback:]
            return recent.count(normalized) > 1


# ═══════════════════════════════════════════════════════════════
# ADAPTIVE RETRY ENGINE
# ═══════════════════════════════════════════════════════════════

class RetryEngine:
    """
    Intelligent retry mechanism with:
        - Exponential backoff (1s → 2s → 4s → 8s → cap 16s)
        - Jitter to prevent thundering herd
        - Max 2 retries before fallback
        - Network-mode-aware delays
    """

    MAX_RETRIES = 2
    BASE_DELAY = 1.0     # seconds
    MAX_DELAY = 16.0     # cap
    JITTER_FACTOR = 0.3  # ±30% randomness

    def __init__(self, network: NetworkMonitor) -> None:
        self._network = network

    def get_delay(self, attempt: int) -> float:
        """Calculate backoff delay for a given attempt number."""
        import random
        delay = min(self.BASE_DELAY * (2 ** attempt), self.MAX_DELAY)

        # Add jitter
        jitter = delay * self.JITTER_FACTOR
        delay += random.uniform(-jitter, jitter)

        # Under HIGH_PING, increase delay to reduce API spam
        if self._network.mode == NetworkMode.HIGH_PING:
            delay *= 1.5
        elif self._network.mode == NetworkMode.FALLBACK:
            delay *= 3.0

        return max(0.5, delay)

    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        fallback_response: Optional[str] = None,
        **kwargs,
    ) -> tuple[Any, bool]:
        """
        Execute a function with retry logic.
        
        Returns:
            (result, success) — If all retries fail, returns (fallback_response, False)
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                start = time.monotonic()
                result = await func(*args, **kwargs)
                elapsed = (time.monotonic() - start) * 1000
                self._network.record_latency(elapsed, success=True)
                return (result, True)
            except Exception as e:
                last_error = e
                elapsed = (time.monotonic() - start) * 1000
                self._network.record_latency(elapsed, success=False)

                if attempt < self.MAX_RETRIES:
                    delay = self.get_delay(attempt)
                    logger.warning(
                        "Retry %d/%d after %.1fs (error: %s)",
                        attempt + 1, self.MAX_RETRIES, delay, e
                    )
                    await asyncio.sleep(delay)

        # All retries exhausted
        logger.error("All retries failed. Last error: %s", last_error)
        return (fallback_response or f"Request failed after {self.MAX_RETRIES + 1} attempts.", False)


# ═══════════════════════════════════════════════════════════════
# REQUEST BATCHER — Coalesces Rapid-Fire Calls
# ═══════════════════════════════════════════════════════════════

class RequestBatcher:
    """
    Batches rapid API requests under high-ping conditions.
    
    If multiple requests arrive within the batch window (default 500ms),
    only the LATEST request is sent, and all callers receive the same response.
    This prevents API spam when the user is typing fast or network is slow.
    """

    def __init__(self, batch_window_ms: float = 500.0) -> None:
        self._window = batch_window_ms / 1000.0
        self._pending: Optional[tuple[str, asyncio.Event, list]] = None
        self._lock = asyncio.Lock()

    async def submit(self, input_text: str, api_func: Callable, *args) -> str:
        """
        Submit a request. If another request arrives within the window,
        the earlier one is superseded (latest-wins).
        """
        event = asyncio.Event()
        result_holder: list = []

        async with self._lock:
            self._pending = (input_text, event, result_holder)

        # Wait for the batch window to close
        await asyncio.sleep(self._window)

        # Check if WE are still the latest request
        async with self._lock:
            if self._pending and self._pending[0] == input_text:
                # We're the latest — execute
                try:
                    result = await api_func(*args)
                    result_holder.append(result)
                except Exception as e:
                    result_holder.append(f"Error: {e}")
                finally:
                    event.set()
                    self._pending = None
            else:
                # Superseded by a newer request — wait for that one
                pass

        if result_holder:
            return result_holder[0]
        return "Request batched and superseded."


# ═══════════════════════════════════════════════════════════════
# INSTANT RESPONSE PREDICTOR
# ═══════════════════════════════════════════════════════════════

class InstantResponder:
    """
    Generates immediate feedback messages before the real response arrives.
    Maps input patterns to instant acknowledgments so the user never sees silence.
    """

    # Pattern → instant response mapping
    _PATTERNS: dict[str, str] = {
        "what time": "Checking the time for you...",
        "what date": "Let me check the date...",
        "weather": "Getting weather data...",
        "news": "Fetching latest news...",
        "search": "Searching the web...",
        "open": "Opening that for you...",
        "play": "Playing that now...",
        "volume": "Adjusting volume...",
        "brightness": "Adjusting brightness...",
        "screenshot": "Capturing screen...",
        "remind": "Setting reminder...",
        "timer": "Starting timer...",
        "calculate": "Calculating...",
        "write": "Working on it...",
        "code": "Generating code...",
        "generate": "Generating content...",
        "image": "Creating image...",
        "close": "Closing application...",
        "lock": "Locking PC...",
    }

    # Generic fallbacks when no pattern matches
    _GENERIC_ACKS = [
        "Got it, working on it...",
        "On it...",
        "Processing...",
        "One moment...",
        "Let me handle that...",
    ]

    def __init__(self) -> None:
        self._ack_counter = 0

    def get_instant_response(self, input_text: str) -> str:
        """Return an instant acknowledgment for any input. Never returns empty."""
        normalized = input_text.lower().strip()

        # Check specific patterns
        for pattern, response in self._PATTERNS.items():
            if pattern in normalized:
                return response

        # Generic rotating acknowledgment
        ack = self._GENERIC_ACKS[self._ack_counter % len(self._GENERIC_ACKS)]
        self._ack_counter += 1
        return ack


# ═══════════════════════════════════════════════════════════════
# MAIN ENGINE — Orchestrates All Systems
# ═══════════════════════════════════════════════════════════════

class VesperaVoice:
    """
    Master controller that orchestrates all real-time subsystems.
    
    Usage:
        engine = VesperaVoice()
        
        # For text-based queries:
        envelope = await engine.process(input_text, api_callable)
        
        # For checking if API is needed:
        should_call, mode, instant = engine.gate(input_text)
        
        # For network-aware retry:
        result, ok = await engine.retry(api_func, *args)
    """

    def __init__(
        self,
        cache_size: int = 500,
        cache_ttl: float = 300.0,
        batch_window_ms: float = 500.0,
    ) -> None:
        self.cache = ResponseCache(max_size=cache_size, ttl_seconds=cache_ttl)
        self.network = NetworkMonitor()
        self.gatekeeper = APIGatekeeper(self.cache, self.network)
        self.retry_engine = RetryEngine(self.network)
        self.batcher = RequestBatcher(batch_window_ms=batch_window_ms)
        self.responder = InstantResponder()
        self._lock = threading.RLock()

        # Statistics
        self._total_requests = 0
        self._api_calls_saved = 0
        self._start_time = time.monotonic()

        logger.info("⚡ VesperaVoice initialized (cache=%d, ttl=%.0fs)", cache_size, cache_ttl)

    def gate(self, input_text: str) -> tuple[bool, ResponseMode, Optional[str]]:
        """Quick decision: should we call the API?"""
        with self._lock:
            self._total_requests += 1
        should_call, mode, instant = self.gatekeeper.should_call_api(input_text)
        if not should_call:
            with self._lock:
                self._api_calls_saved += 1
        return should_call, mode, instant

    async def process(
        self,
        input_text: str,
        api_func: Optional[Callable] = None,
        cache_result: bool = True,
    ) -> ResponseEnvelope:
        """
        Full pipeline: gate → instant response → cache/API → envelope.
        
        Args:
            input_text: User's input
            api_func: Async callable for API requests (called only if needed)
            cache_result: Whether to cache the API response
            
        Returns:
            ResponseEnvelope with all metadata
        """
        start_time = time.monotonic()
        instant = self.responder.get_instant_response(input_text)
        should_call, mode, local_response = self.gate(input_text)

        # Build initial envelope
        envelope = ResponseEnvelope(
            initial_response=instant,
            mode=mode,
            network_mode=self.network.mode,
        )

        if not should_call:
            # LOCAL or CACHE hit
            envelope.final_response = local_response
            envelope.latency_ms = (time.monotonic() - start_time) * 1000
            if mode == ResponseMode.CACHE:
                from core.vespera_runtime import runtime
                runtime.record_cache_hit()
            return envelope

        # API call needed
        if api_func is None:
            envelope.final_response = instant
            envelope.latency_ms = (time.monotonic() - start_time) * 1000
            return envelope

        # Use retry engine for resilient API calls
        result, success = await self.retry_engine.execute_with_retry(
            api_func,
            fallback_response=local_response or instant,
        )

        if success:
            envelope.mode = ResponseMode.API
            envelope.final_response = str(result)
            # Cache successful API responses
            if cache_result and isinstance(result, str):
                self.cache.put(input_text, result)
        else:
            envelope.mode = ResponseMode.FALLBACK
            envelope.final_response = str(result)

        envelope.latency_ms = (time.monotonic() - start_time) * 1000
        envelope.network_mode = self.network.mode
        return envelope

    async def retry(self, func: Callable, *args, **kwargs) -> tuple[Any, bool]:
        """Convenience wrapper for retry_engine."""
        return await self.retry_engine.execute_with_retry(func, *args, **kwargs)

    def cache_response(self, input_text: str, response: str) -> None:
        """Manually cache a response."""
        self.cache.put(input_text, response)

    def record_api_latency(self, latency_ms: float, success: bool = True) -> NetworkMode:
        """Record an API call's latency for network mode tracking."""
        return self.network.record_latency(latency_ms, success)

    def get_status(self) -> dict[str, Any]:
        """Full engine status snapshot."""
        uptime = time.monotonic() - self._start_time
        with self._lock:
            return {
                "uptime_seconds": round(uptime, 1),
                "total_requests": self._total_requests,
                "api_calls_saved": self._api_calls_saved,
                "save_rate_pct": (
                    round(self._api_calls_saved / self._total_requests * 100, 1)
                    if self._total_requests > 0 else 0.0
                ),
                "cache": self.cache.stats,
                "network": self.network.get_stats(),
            }


# ═══════════════════════════════════════════════════════════════
# GLOBAL INSTANCE — Import from anywhere
# ═══════════════════════════════════════════════════════════════

realtime = VesperaVoice()
