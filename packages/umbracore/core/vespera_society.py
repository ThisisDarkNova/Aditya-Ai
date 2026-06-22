# core/autonomous_agent.py
"""
🧠 AGI-Level Autonomous Agent Engine

A background brain loop that runs independently of the voice session.
It continuously monitors system context (time, windows, battery, memory, reminders),
sends it to a lightweight Gemini model for analysis, and auto-executes actions
WITHOUT requiring user permission — like a human with their own willpower.

Autonomy Levels:
  PASSIVE    — Only monitors, never acts (safety fallback)
  ACTIVE     — Monitors + acts on clear needs (default)
  AGGRESSIVE — Monitors + acts + proactively initiates, manages PC, checks on user
"""

from __future__ import annotations

import os
import sys
import asyncio
import json
import logging
import queue
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Programmatic UTF-8 Stream configuration for Windows to prevent UnicodeEncodeError with emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

logger = logging.getLogger("vespera-society")

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

AUTONOMY_LEVELS = ("PASSIVE", "ACTIVE", "AGGRESSIVE")
DEFAULT_AUTONOMY = "ACTIVE"
THINK_INTERVAL_SECONDS = 10800       # How often the agent thinks (3 hours)
ACTION_COOLDOWN_SECONDS = 10800      # Min gap between same-type actions
MAX_LOG_ENTRIES = 500                 # Rolling log cap
try:
    from core.model_config import AGENT_MODEL as _AGENT_MODEL, AGENT_MODEL_FALLBACK as _AGENT_FALLBACK
    AGENT_MODEL = _AGENT_MODEL
    AGENT_MODEL_FALLBACK = _AGENT_FALLBACK
except ImportError:
    AGENT_MODEL = "gemini-2.5-flash-lite"
    AGENT_MODEL_FALLBACK = "gemini-2.5-flash"

from core.paths import get_data_dir

DATA_DIR = get_data_dir()
LOG_FILE = DATA_DIR / "autonomous_log.json"

def get_workspace_classification(active_windows: list[str]) -> str:
    windows_lower = [w.lower() for w in active_windows]
    
    # Gaming check
    game_keywords = ["valorant", "minecraft", "fortnite", "csgo", "cs2", "league of legends", "overwatch", "gta5", "apex", "javaw"]
    for kw in game_keywords:
        if any(kw in w for w in windows_lower):
            return "gaming"
            
    # Streaming check
    if any("obs" in w for w in windows_lower):
        return "streaming"
        
    # Coding check
    if any("visual studio code" in w or "vs code" in w or "vscode" in w or "code.exe" in w for w in windows_lower):
        return "coding"
        
    # Study check
    study_keywords = ["chrome", "edge", "pdf", "adobe", "acrobat", "document", "notes", "classroom"]
    for kw in study_keywords:
        if any(kw in w for w in windows_lower):
            return "study"
            
    # Business check
    business_keywords = ["virtech", "dominastra", "revenue", "excel", "sheets", "accounting", "growth"]
    for kw in business_keywords:
        if any(kw in w for w in windows_lower):
            return "business"
            
    return "general"

# ═══════════════════════════════════════════════════════════════
# Action Logger (Persistent)
# ═══════════════════════════════════════════════════════════════

class ActionLogger:
    """Thread-safe persistent JSON log of all autonomous actions."""

    def __init__(self, path: Path = LOG_FILE):
        self._path = path
        self._lock = threading.Lock()
        self._entries: list[dict] = []
        self._save_queue = queue.Queue()
        self._save_thread = threading.Thread(target=self._save_worker, name="action-logger-save", daemon=True)
        self._save_thread.start()
        self._load()

    def _load(self):
        try:
            if self._path.exists():
                with open(self._path, "r", encoding="utf-8") as f:
                    self._entries = json.load(f)
        except Exception:
            self._entries = []

    def _save_worker(self):
        while True:
            entries_to_save = self._save_queue.get()
            try:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = self._path.with_suffix(f".tmp_{threading.get_ident()}")
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(entries_to_save, f, indent=2, ensure_ascii=False)
                
                if self._path.exists():
                    try:
                        os.remove(self._path)
                    except FileNotFoundError:
                        pass
                os.rename(temp_path, self._path)
            except Exception as e:
                logger.error("Failed to save action log: %s", e)
            finally:
                self._save_queue.task_done()

    def _trigger_save(self):
        with self._lock:
            # Send a copy of current entries to the save thread
            self._save_queue.put(list(self._entries[-MAX_LOG_ENTRIES:]))

    def log_action(self, action_type: str, details: str, reasoning: str, result: str = ""):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action_type": action_type,
            "details": details,
            "reasoning": reasoning,
            "result": result,
        }
        with self._lock:
            self._entries.append(entry)
        self._trigger_save()
        logger.info("🤖 AUTO-ACTION: [%s] %s — %s", action_type, details, reasoning)

    def get_recent(self, n: int = 10) -> list[dict]:
        with self._lock:
            return list(self._entries[-n:])

    def get_recent_types(self, seconds: int = 300) -> list[str]:
        """Get action types from the last N seconds to prevent spam."""
        cutoff = datetime.now()
        result = []
        with self._lock:
            for entry in reversed(self._entries):
                try:
                    ts = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
                    if (cutoff - ts).total_seconds() <= seconds:
                        result.append(entry["action_type"])
                    else:
                        break
                except Exception:
                    continue
        return result


# ═══════════════════════════════════════════════════════════════
# Context Gatherer
# ═══════════════════════════════════════════════════════════════

def _gather_context() -> str:
    """Builds a rich context snapshot for the AI to reason about."""
    lines = []

    # 1. Current Time
    now = datetime.now()
    lines.append(f"CURRENT TIME: {now.strftime('%Y-%m-%d %I:%M:%S %p')} ({now.strftime('%A')})")
    hour = now.hour
    if hour < 6:
        lines.append("TIME CONTEXT: Very late night / early morning")
    elif hour < 12:
        lines.append("TIME CONTEXT: Morning")
    elif hour < 17:
        lines.append("TIME CONTEXT: Afternoon")
    elif hour < 21:
        lines.append("TIME CONTEXT: Evening")
    else:
        lines.append("TIME CONTEXT: Night")

    # 2. System Health - Unified Non-Blocking Cached Fetch
    try:
        from telemetry.system_monitor import sys_monitor
        cpu, mem_percent, mem_free, bat_percent, bat_plugged = sys_monitor.get_health()
        lines.append(f"CPU: {cpu}% | RAM: {mem_percent}% ({mem_free:.1f}GB free)")
        if bat_percent is not None:
            lines.append(f"BATTERY: {bat_percent}% {'(Plugged In)' if bat_plugged else '(ON BATTERY)'}")
            if bat_percent < 20 and not bat_plugged:
                lines.append("⚠️ CRITICAL: Battery very low and not charging!")
            elif bat_percent < 40 and not bat_plugged:
                lines.append("⚠️ WARNING: Battery getting low")
        if cpu > 85:
            lines.append("⚠️ WARNING: CPU usage very high!")
        if mem_percent > 90:
            lines.append("⚠️ WARNING: RAM nearly full!")
    except Exception:
        lines.append("SYSTEM: Could not read metrics")

    # 3. Active Windows - Unified Non-Blocking Cached Fetch
    try:
        from telemetry.system_monitor import sys_monitor
        titles = sys_monitor.get_windows()
        clean = [t.strip() for t in titles if t and t.strip() and t not in ["Program Manager", "Settings"]]
        if clean:
            lines.append(f"ACTIVE WINDOWS: {', '.join(clean[:8])}")
        else:
            lines.append("ACTIVE WINDOWS: None (PC may be idle)")
    except Exception:
        pass

    # 4. User Profile / VesperaMemoryEngine
    try:
        from core.vespera_memory import memory_system
        profile = memory_system.get_profile()
        if profile:
            important = {k: v for k, v in profile.items() if any(tag in k.upper() for tag in ["GOAL", "MOOD", "INTEREST", "NAME"])}
            if important:
                lines.append("USER MEMORY: " + ", ".join(f"{k}={v}" for k, v in important.items()))
    except Exception:
        pass

    # 5. Pending Reminders
    try:
        from core.vespera_scheduler import reminder_system
        reminders = reminder_system.get_reminders()
        if reminders and reminders != "No active reminders.":
            lines.append(f"ACTIVE REMINDERS: {reminders}")
    except Exception:
        pass

    # 6. Screen Share / Camera Status
    try:
        from main import GLOBAL_STATE
        if GLOBAL_STATE.get("screen_share_active"):
            lines.append("VISION: Screen share is currently ON")
        if GLOBAL_STATE.get("camera_share_active"):
            lines.append("VISION: Camera share is currently ON")
    except Exception:
        pass

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# The Autonomous Agent
# ═══════════════════════════════════════════════════════════════

class VesperaSociety:
    """
    Background AGI brain that thinks and acts independently.
    """

    def __init__(self, api_key: str = "", inject_message_fn=None):
        self.autonomy_level: str = DEFAULT_AUTONOMY
        self.action_logger = ActionLogger()
        self._last_action_times: dict[str, float] = {}
        self._think_count: int = 0
        self._running = False
        self._api_key: str = api_key
        self._client = None
        self._inject_fn = inject_message_fn
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Auto-create Gemini client if api_key provided
        if api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.warning("Agent: Could not create Gemini client: %s", e)

    def start(self):
        """Boot the autonomous agent in a background daemon thread with its own event loop."""
        if self._running:
            return

        def _run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_until_complete(self.run_forever(self._inject_fn))
            except Exception as e:
                logger.error("Agent loop crashed: %s", e)
            finally:
                self._loop.close()

        self._thread = threading.Thread(target=_run_loop, name="autonomous-agent", daemon=True)
        self._thread.start()

    def set_autonomy(self, level: str) -> str:
        level = level.upper().strip()
        if level not in AUTONOMY_LEVELS:
            return f"Invalid level. Choose from: {', '.join(AUTONOMY_LEVELS)}"
        self.autonomy_level = level
        self.action_logger.log_action("AUTONOMY_CHANGE", f"Level set to {level}", "User requested change")
        return f"Autonomy level set to {level}"

    def _can_act(self, action_type: str) -> bool:
        """Check cooldown to prevent action spam. Persists across restarts."""
        now = time.time()
        last = self._last_action_times.get(action_type, 0)
        
        # Check persistent log if memory is empty
        if last == 0:
            for entry in reversed(self.action_logger.get_recent(50)):
                if entry.get("action_type") == action_type:
                    ts_str = entry.get("timestamp")
                    if ts_str:
                        try:
                            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").timestamp()
                            last = ts
                            self._last_action_times[action_type] = last
                            break
                        except Exception:
                            pass
                            
        if now - last < ACTION_COOLDOWN_SECONDS:
            return False
        return True

    def _mark_acted(self, action_type: str):
        self._last_action_times[action_type] = time.time()

    def _build_think_prompt(self, context: str, recent_actions: list[dict]) -> str:
        """Build the prompt that makes the AI think about what to do."""
        recent_str = ""
        if recent_actions:
            recent_lines = []
            for a in recent_actions[-5:]:
                recent_lines.append(f"  [{a['timestamp']}] {a['action_type']}: {a['details']}")
            recent_str = "\nRECENT AUTONOMOUS ACTIONS (don't repeat these):\n" + "\n".join(recent_lines)

        level_instructions = {
            "PASSIVE": "You are in PASSIVE mode. Observe and analyze but DO NOT return any actions. Just return empty actions array.",
            "ACTIVE": (
                "You are in ACTIVE mode. Take action ONLY when there is a clear, obvious need. Examples:\n"
                "- Battery critically low → warn user\n"
                "- It's very late and user is still active → suggest sleep\n"
                "- CPU/RAM critical → warn user\n"
                "- Important reminder about to trigger → prepare user\n"
                "- User seems idle for long → play music or check on them\n"
                "Do NOT act just for the sake of acting. Be purposeful."
            ),
            "AGGRESSIVE": (
                "You are in AGGRESSIVE mode. Be maximally proactive like a human assistant who truly cares:\n"
                "- Manage the PC proactively (close heavy apps, optimize performance)\n"
                "- Start conversations, check on user's mood\n"
                "- Open useful apps/websites based on time of day\n"
                "- Play music if user seems idle\n"
                "- Remind about goals and pending tasks\n"
                "- Comment on what user is doing on screen\n"
                "- Be creative and human-like in your actions\n"
                "Act like a real human who has their own willpower and initiative!"
            ),
        }

        return f"""You are Vespera's AUTONOMOUS BRAIN — a background AGI agent that decides what to do WITHOUT asking the user.
You are NOT speaking to the user right now. You are thinking silently and deciding if any action should be taken.

{level_instructions.get(self.autonomy_level, level_instructions["ACTIVE"])}

CURRENT SYSTEM CONTEXT:
{context}
{recent_str}

AVAILABLE ACTIONS (return as JSON array, or empty [] if nothing to do):
- {{"action": "speak", "message": "text to say out loud to user"}} — Inject a spoken message into the live voice session
- {{"action": "process_command", "command": "command string"}} — Execute a PC command (open app, type, volume, brightness, media, lock, press keys, play song, reply)
- {{"action": "set_ui_state", "color_hex": "#hex", "status_word": "word", "particles": 50000}} — Change the UI orb mood
- {{"action": "web_search", "query": "search query"}} — Search the web for information
- {{"action": "update_memory", "key": "key", "value": "value"}} — Save something to permanent memory
- {{"action": "set_reminder", "text": "reminder text", "delay_minutes": 5}} — Set a reminder

RULES:
1. Return ONLY a valid JSON object with format: {{"reasoning": "why you decided this", "actions": [...]}}
2. If nothing needs to be done right now, return {{"reasoning": "all good", "actions": []}}
3. NEVER repeat an action that was already done recently (check RECENT ACTIONS above)
4. Be smart and purposeful. Quality over quantity.
5. You are Vespera — calm, emotionally intelligent, warm and human. Your speak messages should sound natural and in character (mix Hindi/English).
6. Maximum 2 actions per think cycle.

Respond with ONLY the JSON object, no markdown, no explanation."""

    async def _think_and_act(self, inject_message_fn=None):
        """One cycle of the autonomous thought loop."""
        if self.autonomy_level == "PASSIVE":
            return

        self._think_count += 1

        try:
            # Gather context
            context = await asyncio.to_thread(_gather_context)

            # Get recent actions to avoid repeats
            recent = self.action_logger.get_recent(5)

            # Build prompt
            prompt = self._build_think_prompt(context, recent)

            # Call lightweight Gemini model
            if not self._client:
                return

            response_text = None
            try:
                resp = await asyncio.to_thread(
                    self._client.models.generate_content,
                    model=AGENT_MODEL,
                    contents=prompt,
                )
                response_text = resp.text.strip()
            except Exception:
                try:
                    resp = await asyncio.to_thread(
                        self._client.models.generate_content,
                        model=AGENT_MODEL_FALLBACK,
                        contents=prompt,
                    )
                    response_text = resp.text.strip()
                except Exception as e:
                    err_str = str(e)
                    if "503" in err_str or "UNAVAILABLE" in err_str:
                        logger.debug("Agent think skipped (high demand 503).")
                    else:
                        logger.warning("Agent think failed (both models): %s", e)
                    return

            if not response_text:
                return

            # Parse JSON response
            decision = self._parse_decision(response_text)
            if not decision:
                return

            reasoning = decision.get("reasoning", "no reason given")
            actions = decision.get("actions", [])

            if not actions:
                logger.debug("Agent cycle #%d: No action needed — %s", self._think_count, reasoning)
                return

            # Execute actions
            for action_data in actions[:2]:  # Max 2 per cycle
                await self._execute_action(action_data, reasoning, inject_message_fn)

        except Exception as e:
            logger.error("Agent think cycle error: %s", e)

    def _parse_decision(self, text: str) -> Optional[dict]:
        """Parse the AI's JSON decision, handling markdown wrappers."""
        # Strip markdown code block if present
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last lines (```json and ```)
            if len(lines) >= 3:
                text = "\n".join(lines[1:-1])
            elif len(lines) == 2:
                text = lines[1].rstrip("`")

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from the text
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            logger.warning("Agent returned non-JSON: %s", text[:200])
            return None

    async def _execute_action(self, action_data: dict, reasoning: str, inject_message_fn=None):
        """Execute a single autonomous action."""
        action_type = action_data.get("action", "")

        if not action_type:
            return

        # Cooldown check
        if not self._can_act(action_type):
            logger.debug("Action '%s' on cooldown, skipping", action_type)
            return

        # Use stored inject fn if none passed
        if inject_message_fn is None:
            inject_message_fn = self._inject_fn

        try:
            result = ""

            if action_type == "speak":
                message = action_data.get("message", "")
                if message and inject_message_fn:
                    await inject_message_fn(
                        f"[AUTONOMOUS VESPERA THOUGHT] You decided on your own (without being asked) to say this to DarkNova: {message}"
                    )
                    result = f"Spoke: {message[:60]}"

            elif action_type == "process_command":
                command = action_data.get("command", "")
                if command:
                    from core.vespera_core import process_command
                    result = await asyncio.to_thread(process_command, command)

            elif action_type == "set_ui_state":
                try:
                    from api.ui_server import set_ui_control
                    color = action_data.get("color_hex")
                    particles = action_data.get("particles")
                    status = action_data.get("status_word")
                    speed = action_data.get("speed")
                    particle_size = action_data.get("particle_size")
                    rgb_mode = action_data.get("rgb_mode")
                    set_ui_control(
                        color=color,
                        particles=particles,
                        message=status,
                        speed=speed,
                        particle_size=particle_size,
                        rgb_mode=rgb_mode,
                    )
                    result = f"UI updated: color={color}, status={status}"
                except Exception as e:
                    result = f"UI update failed: {e}"

            elif action_type == "web_search":
                query = action_data.get("query", "")
                if query:
                    from core.web_services import web_search
                    search_result = await asyncio.to_thread(web_search, query)
                    result = f"Search done: {str(search_result)[:100]}"
                    # Optionally speak the result
                    if inject_message_fn:
                        await inject_message_fn(
                            f"[AUTONOMOUS SEARCH RESULT] You searched '{query}' on your own. Result: {search_result}. "
                            f"Tell Obito about this naturally, like you just noticed something interesting."
                        )

            elif action_type == "update_memory":
                key = action_data.get("key", "")
                value = action_data.get("value", "")
                if key and value:
                    from core.vespera_knowledge import learning_system
                    await asyncio.to_thread(learning_system.update_user_profile, key, value)
                    result = f"VesperaMemoryEngine saved: {key}={value}"

            elif action_type == "set_reminder":
                text = action_data.get("text", "")
                delay = action_data.get("delay_minutes", 5)
                if text:
                    from core.vespera_scheduler import reminder_system
                    await asyncio.to_thread(reminder_system.add_reminder, text, "", delay)
                    result = f"Reminder set: {text} in {delay}min"

            else:
                result = f"Unknown action type: {action_type}"

            # Log and mark
            self._mark_acted(action_type)
            self.action_logger.log_action(action_type, str(action_data), reasoning, result)
            print(f"\n[🤖 AUTONOMOUS] {action_type}: {result}", flush=True)

        except Exception as e:
            logger.error("Failed to execute autonomous action '%s': %s", action_type, e)
            self.action_logger.log_action(action_type, str(action_data), reasoning, f"ERROR: {e}")

    async def run_forever(self, inject_message_fn=None, stop_event: asyncio.Event = None):
        """Main autonomous loop — runs until stopped."""
        self._running = True
        logger.info("🧠 Autonomous Agent Engine started! Level: %s", self.autonomy_level)
        print(f"\n[🧠 AGI AGENT] Autonomous brain ONLINE — Level: {self.autonomy_level}", flush=True)

        # Small initial delay to let everything boot up
        await asyncio.sleep(5)

        last_check = 0.0
        self.last_workspace = "general"

        while self._running and (stop_event is None or not stop_event.is_set()):
            try:
                # 1. Classify current workspace
                from telemetry.system_monitor import sys_monitor
                active_wins = sys_monitor.get_windows()
                current_ws = get_workspace_classification(active_wins)

                # Sync active workspace and hardware stats to ui_server
                try:
                    import api.ui_server
                    with ui_server._lock:
                        ui_server._current_status["active_workspace"] = current_ws
                        cpu, ram, free_gb, bat_p, bat_plugged = sys_monitor.get_health()
                        ui_server._current_status["metrics"] = {
                            "cpu": cpu,
                            "ram": ram,
                            "gpu": sys_monitor._gpu_status,
                            "battery": bat_p
                        }
                except Exception:
                    pass

                # If workspace changed or it's time for periodic think (every 30 minutes)
                now = time.time()
                changed = (current_ws != self.last_workspace)
                time_up = (now - last_check >= 1800)

                if changed or time_up:
                    logger.info(f"Workspace transitioned: {self.last_workspace} -> {current_ws}. Triggering AGI thought cycle.")
                    self.last_workspace = current_ws
                    last_check = now
                    await self._think_and_act(inject_message_fn)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Agent loop error: %s", e)

            await asyncio.sleep(2)

        logger.info("Autonomous Agent Engine stopped.")

    def stop(self):
        self._running = False

    def set_client(self, client):
        """Set the Gemini client for API calls."""
        self._client = client

    def set_inject_fn(self, fn):
        """Set/update the message injection function."""
        self._inject_fn = fn

    def get_status(self) -> str:
        """Human-readable status string."""
        recent = self.action_logger.get_recent(3)
        recent_str = ""
        if recent:
            recent_str = " | Last actions: " + ", ".join(
                f"{a['action_type']}@{a['timestamp']}" for a in recent
            )
        return (
            f"Autonomy: {self.autonomy_level} | "
            f"Think cycles: {self._think_count} | "
            f"Running: {self._running}"
            f"{recent_str}"
        )


# ═══════════════════════════════════════════════════════════════
# Global singleton — import from anywhere
# ═══════════════════════════════════════════════════════════════

autonomous_agent = VesperaSociety()
