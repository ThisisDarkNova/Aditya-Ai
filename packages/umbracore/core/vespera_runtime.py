# core/runtime_state.py
"""
Thread-safe centralized runtime state for 24/7 autonomous operation.

Tracks: connection state, adaptive cooldown, health metrics, API usage.
All threads can safely read/write through this single object.
"""

from __future__ import annotations

import time
import threading
import logging
from typing import Any, Optional

logger = logging.getLogger("vespera-runtime")

# Cooldown durations in seconds (escalating tiers)
COOLDOWN_TIERS = [
    0,      # Tier 0: no cooldown
    300,    # Tier 1: 5 minutes
    600,    # Tier 2: 10 minutes
    900,    # Tier 3: 15 minutes
]
MAX_COOLDOWN_TIER = len(COOLDOWN_TIERS) - 1

# Circuit breaker: if this many failures in CIRCUIT_WINDOW → pause
CIRCUIT_MAX_FAILURES = 20
CIRCUIT_WINDOW = 300.0       # 5 minutes
CIRCUIT_PAUSE = 120.0        # 2 minute pause


class VesperaRuntime:
    """
    Single source of truth for the entire runtime.
    Thread-safe via a reentrant lock.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()

        # ── Connection ──
        # ── 6-Stage Lifecycle State Machine ──
        # OFFLINE    = "offline"
        # STARTING   = "starting" (or "connecting", "recovering")
        # SLEEPING   = "sleeping" (standby / clap wait)
        # AWAKE      = "awake"
        # LISTENING  = "listening"
        # PROCESSING = "processing" (or "tool", "speaking", "cooling")
        self.status: str = "offline"           
        self.uptime_start: float = time.monotonic()
        self.total_reconnections: int = 0
        self.consecutive_failures: int = 0

        # ── Adaptive Cooldown ──
        self.cooldown_tier: int = 0            # 0 = none, 1-3 = escalating
        self.cooldown_until: float = 0.0       # monotonic timestamp when cooldown ends

        # ── API Tracking ──
        self.api_calls_session: int = 0
        self.cache_hits_session: int = 0

        # ── Health ──
        self.last_success_time: float = time.monotonic()
        self._failure_timestamps: list[float] = []

    # ── Cooldown Management ──

    def enter_cooldown(self) -> float:
        """
        Escalate cooldown tier after a 429 / rate-limit error.
        Returns the cooldown duration in seconds.
        """
        with self._lock:
            self.cooldown_tier = min(self.cooldown_tier + 1, MAX_COOLDOWN_TIER)
            duration = COOLDOWN_TIERS[self.cooldown_tier]
            self.cooldown_until = time.monotonic() + duration
            self.status = "cooling"
            logger.warning(
                "⏸️  Entering cooldown tier %d (%ds). Resuming at %.0f",
                self.cooldown_tier, duration, self.cooldown_until,
            )
            return duration

    def is_cooling(self) -> bool:
        """Check if we're still in a cooldown period."""
        with self._lock:
            if self.cooldown_tier == 0:
                return False
            if time.monotonic() >= self.cooldown_until:
                # Cooldown expired → transition to recovering
                self.status = "recovering"
                return False
            return True

    def cooldown_remaining(self) -> float:
        """Seconds remaining in current cooldown, or 0."""
        with self._lock:
            if self.cooldown_tier == 0:
                return 0.0
            return max(0.0, self.cooldown_until - time.monotonic())

    # ── Success / Failure Tracking ──

    def record_success(self) -> None:
        """Call after a successful connection session."""
        with self._lock:
            self.consecutive_failures = 0
            self.cooldown_tier = 0
            self.cooldown_until = 0.0
            self.last_success_time = time.monotonic()
            self.api_calls_session += 1
            self.status = "listening"

    def record_failure(self, error: Exception) -> str:
        """
        Classify an error and decide the action.
        Returns: "fast_reconnect" | "cooldown" | "backoff" | "circuit_break"
        """
        with self._lock:
            self.consecutive_failures += 1
            self.total_reconnections += 1
            now = time.monotonic()
            self._failure_timestamps.append(now)

            # Trim old failure timestamps
            cutoff = now - CIRCUIT_WINDOW
            self._failure_timestamps = [t for t in self._failure_timestamps if t > cutoff]

            # Circuit breaker check
            if len(self._failure_timestamps) >= CIRCUIT_MAX_FAILURES:
                self.status = "cooling"
                logger.error(
                    "🔴 Circuit breaker tripped: %d failures in %.0fs. Pausing %.0fs.",
                    len(self._failure_timestamps), CIRCUIT_WINDOW, CIRCUIT_PAUSE,
                )
                self.cooldown_until = now + CIRCUIT_PAUSE
                self._failure_timestamps.clear()
                return "circuit_break"

            # Classify the error
            error_text = _extract_error_text(error)

            if _is_rate_limited(error_text):
                self.enter_cooldown()
                return "cooldown"

            if _is_transient(error_text):
                self.status = "connecting"
                return "fast_reconnect"

            # Unknown error → exponential backoff
            self.status = "connecting"
            return "backoff"

    def record_cache_hit(self) -> None:
        """Increment cache hit counter."""
        with self._lock:
            self.cache_hits_session += 1

    # ── Health ──

    @property
    def is_healthy(self) -> bool:
        """System is healthy if not too many recent failures."""
        with self._lock:
            now = time.monotonic()
            cutoff = now - CIRCUIT_WINDOW
            recent = len([t for t in self._failure_timestamps if t > cutoff])
            return recent < CIRCUIT_MAX_FAILURES

    @property
    def uptime_seconds(self) -> float:
        return time.monotonic() - self.uptime_start

    def should_reconnect(self) -> bool:
        """Returns True if it's safe to attempt reconnection."""
        with self._lock:
            if self.is_cooling():
                return False
            return True

    # ── Snapshot ──

    def get_snapshot(self) -> dict[str, Any]:
        """Thread-safe status snapshot for logging and UI."""
        with self._lock:
            uptime = self.uptime_seconds
            hours = int(uptime // 3600)
            mins = int((uptime % 3600) // 60)
            return {
                "status": self.status,
                "uptime": f"{hours}h {mins}m",
                "reconnections": self.total_reconnections,
                "consecutive_failures": self.consecutive_failures,
                "cooldown_tier": self.cooldown_tier,
                "cooldown_remaining": f"{self.cooldown_remaining():.0f}s",
                "api_calls": self.api_calls_session,
                "cache_hits": self.cache_hits_session,
                "healthy": self.is_healthy,
            }


# ═══════════════════════════════════════════════════════════════
# Error classification helpers
# ═══════════════════════════════════════════════════════════════

def _extract_error_text(error: Exception) -> str:
    """Pull all useful text from an exception for classification."""
    parts = [str(error)]
    for attr in ("message", "details", "code", "status_code"):
        value = getattr(error, attr, None)
        if value is not None:
            parts.append(str(value))
    return " | ".join(p for p in parts if p).lower()


def _is_rate_limited(error_text: str) -> bool:
    """True if the error indicates a rate-limit / quota issue."""
    markers = ("429", "rate limit", "quota", "resource_exhausted", "too many requests")
    return any(m in error_text for m in markers)


def _is_transient(error_text: str) -> bool:
    """True if the error is a transient WebSocket / network issue (fast reconnect)."""
    markers = (
        "1007", "1011", "1006",                    # WebSocket close codes
        "invalid frame", "connection closed",       # WebSocket errors
        "winerror", "broken pipe", "reset by peer", # OS-level
        "invalid argument",                         # Gemini transient
    )
    return any(m in error_text for m in markers)


# ═══════════════════════════════════════════════════════════════
# Global instance — import from anywhere
# ═══════════════════════════════════════════════════════════════

runtime = VesperaRuntime()
