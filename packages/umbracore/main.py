# 🚀 Entry point
"""
Real-time voice assistant: Gemini 3.1 Live API + PyAudio (Windows-friendly).

Root cause of 1011 after the first turn (fixed here):
    The public ``session.receive()`` async iterator STOPS after the first
    ``server_content.turn_complete`` message (google-genai AsyncSession.receive).
    The mic task keeps sending, but nothing reads the WebSocket anymore, so
    keepalive/ping handling stalls and the server closes with 1011.

This module uses a continuous ``session._receive()`` loop (multi-turn), sends
audio via ``send_realtime_input``, decouples playback with a thread + queue,
and adds reconnect + session resumption.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import queue
import threading
import psutil
import time
import traceback
import sys
from pathlib import Path
from typing import Any, Optional

# Programmatic UTF-8 Stream configuration for Windows to prevent UnicodeEncodeError with emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Threading and Priority are managed via modern async architecture 
# and thread-pooling rather than direct Windows API kernel manipulation.

# CRITICAL FIX for pywebview Windows transparency
os.environ["WEBVIEW2_DEFAULT_BACKGROUND_COLOR"] = "00000000"
os.environ["WEBVIEW_GUI"] = "edgechromium"

import pyaudio

try:
    from dotenv import load_dotenv
except ImportError:  # optional until: pip install python-dotenv
    load_dotenv = None  # type: ignore[misc, assignment]
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from core.vespera_presence import VESPERA_PERSONA
# Heavy imports are now loaded lazily inside functions to optimize startup time.
from core.skills_manager import (
    test_python_code,
    save_tested_skill,
    execute_skill,
    get_learned_skills_summary,
)
from api.ui_server import (
    start_ui_server,
    set_status,
    set_ui_control,
    add_chat_message,
    pop_pending_input,
)
from core.vespera_runtime import runtime
from core.model_config import get_fallback_chain
from core.vespera_voice import realtime, ResponseMode, NetworkMode

# --- Live model ---
PRIMARY_LIVE_MODEL = "gemini-3.1-flash-live-preview"

GLOBAL_STATE = {
    "screen_share_active": False,
    "camera_share_active": False,
    "camera_zoom_factor": 1.0,
    "camera_zoom_region": "center",
    "screen_zoom_factor": 1.0,
    "screen_zoom_region": "center",
}

# --- Audio ---
INPUT_RATE = 16000
OUTPUT_RATE = 24000
# ~32ms @ 16kHz; smallest steady chunk sizes for zero-delay feel input
CHUNK = 512
# Playback buffers must be larger because Google sends output in larger chunks (24kHz).
# Reducing this causes the "robotic/stuck" stuttering effect.
SPEAKER_FRAMES_PER_BUFFER = 2048

from core.paths import get_logs_dir

log_file = get_logs_dir() / "vespera.log"
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("vespera-live")
logger.setLevel(logging.INFO)

# Silence noisy third-party INFO logs (like "AFC max remote calls: 10")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
logging.getLogger("google").setLevel(logging.WARNING)
logging.getLogger("google.genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("grpc").setLevel(logging.WARNING)
logging.getLogger("absl").setLevel(logging.WARNING)


def _load_dotenv() -> None:
    """Load `.env` next to this script or in the parent directory so GEMINI_API_KEY / GOOGLE_API_KEY work."""
    if getattr(sys, "frozen", False):
        env_path = Path(sys.executable).resolve().parent / ".env"
    else:
        # Check both the CognitiveCore directory and the root workspace directory
        env_path = Path(__file__).resolve().parent / ".env"
        root_env_path = Path(__file__).resolve().parent.parent / ".env"
        if not env_path.is_file() and root_env_path.is_file():
            env_path = root_env_path

    if load_dotenv and env_path.is_file():
        load_dotenv(env_path)


def _get_api_key() -> str:
    # Prefer GEMINI_API_KEY from .env so a stray system GOOGLE_API_KEY does not override it.
    key = (
        os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    ).strip()
    if key.startswith('"') and key.endswith('"'):
        key = key[1:-1]
    if key.startswith("'") and key.endswith("'"):
        key = key[1:-1]
    if not key:
        raise RuntimeError(
            "Set GOOGLE_API_KEY or GEMINI_API_KEY in .env or the environment."
        )
    return key


def _build_config(resume_handle: Optional[str]) -> types.LiveConnectConfig:
    # ML Dev (Gemini API) rejects SessionResumptionConfig.transparent=True — omit it.
    session_resumption: Optional[types.SessionResumptionConfig] = None
    if resume_handle:
        session_resumption = types.SessionResumptionConfig(handle=resume_handle)

    # Inject VesperaMemoryEngine Context
    from core.vespera_memory import memory_system
    profile_data = memory_system.get_profile()
    learned_facts = memory_system.get_learned_facts()
    goals = memory_system.get_goals()
    workflows = memory_system.get_workflows()
    long_term_memories = memory_system.get_long_term_memories()

    context_parts = []

    if profile_data:
        memory_lines = "\n".join([f"- {k}: {v}" for k, v in profile_data.items()])
        context_parts.append(
            "\n\n=== PERMANENT MEMORY (You already know these facts about the user) ===\n"
            "These are facts you have permanently memorized about the user from past conversations.\n"
            "You MUST reference and use this information naturally. NEVER say you don't remember.\n"
            f"{memory_lines}\n"
            "==========================================================================="
        )

    if long_term_memories:
        ltm_lines = "\n".join([f"• {m}" for m in long_term_memories])
        context_parts.append(
            "\n\n=== LONG-TERM MEMORIES (Deep context about the user) ===\n"
            f"{ltm_lines}\n"
            "=========================================================="
        )

    if learned_facts:
        facts_lines = "\n".join([f"• {f}" for f in learned_facts])
        context_parts.append(
            "\n\n=== LEARNED FACTS (Things you have observed and learned about the user) ===\n"
            f"{facts_lines}\n"
            "=============================================================================="
        )

    if goals:
        goals_lines = "\n".join([
            f"• [{g.get('priority','?').upper()}] {g.get('goal', str(g))}"
            if isinstance(g, dict) else f"• {g}"
            for g in goals
        ])
        context_parts.append(
            "\n\n=== USER GOALS (Track and support these proactively) ===\n"
            f"{goals_lines}\n"
            "========================================================="
        )

    if workflows:
        wf_lines = "\n".join([
            f"• {w.get('name','')} → {w.get('steps','')}"
            if isinstance(w, dict) else f"• {w}"
            for w in workflows
        ])
        context_parts.append(
            "\n\n=== SAVED WORKFLOWS (You know exactly how to do these tasks) ===\n"
            f"{wf_lines}\n"
            "=================================================================="
        )

    context_str = "".join(context_parts)

    # Inject Dynamic Skills Knowledge
    skills_context = get_learned_skills_summary()

    # Live System Status Injection via Threaded Monitor
    try:
        from telemetry.system_monitor import sys_monitor

        sys_status_str = sys_monitor.get_status_string()
    except Exception:
        sys_status_str = ""

    return types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
            )
        ),
        system_instruction=types.Content(
            parts=[
                types.Part.from_text(
                    text=VESPERA_PERSONA + context_str + skills_context + sys_status_str
                )
            ]
        ),
        tools=[
            {
                "function_declarations": [
                    {
                        "name": "process_command",
                        "description": "Execute PC system commands. Supported macros:\n- 'open <app>'\n- 'play <song> on youtube'\n- 'type <text>'\n- 'reply <text>' (Types text and hits ENTER instantly, use this for chatting!)\n- 'paste <text>'\n- 'clear_text'\n- 'scroll down'\n- 'scroll up'\n- 'lock pc'\n- 'press <keys>' (e.g. 'press ctrl c')\n- 'volume <0-100>' (e.g. 'volume 50')\n- 'brightness <0-100>' (e.g. 'brightness 75')\n- 'media <play|pause|next|prev|mute>'\n\nRULES:\n1. If chatting (WhatsApp/ChatGPT), ALWAYS use 'reply <text>' so it automatically hits Enter and sends it! 'type' just types without sending.\n2. Do NOT use 'press volume up' for volume! Always use 'volume <percent>'.\n3. Do NOT use keyboard arrows to skip songs! Always use 'media next' or 'media prev'!",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "command": {
                                    "type": "STRING",
                                    "description": "Command string to execute.",
                                }
                            },
                            "required": ["command"],
                        },
                    },
                    {
                        "name": "update_user_profile",
                        "description": "Call this to remember long-term context about the user (interests, mood, goals, etc). Maps directly to the Brain's memory profile.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "key": {
                                    "type": "STRING",
                                    "description": "e.g. 'mood', 'interest', 'favorite color'",
                                },
                                "value": {
                                    "type": "STRING",
                                    "description": "e.g. 'happy', 'piano', 'red'",
                                },
                            },
                            "required": ["key", "value"],
                        },
                    },
                    {
                        "name": "toggle_screen_share",
                        "description": "Turns continuous real-time screen sharing on or off. Turn this on when you need to continuously monitor what the user is doing on their screen. Turn it off when you don't need to watch.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "enable": {
                                    "type": "BOOLEAN",
                                    "description": "True to turn on, False to turn off.",
                                }
                            },
                            "required": ["enable"],
                        },
                    },
                    {
                        "name": "toggle_camera_share",
                        "description": "Turns webcam/camera sharing on or off. Turn this on when the user asks you to look at something physically in front of them, or see their face. Turn it off when you don't need to see through the camera.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "enable": {
                                    "type": "BOOLEAN",
                                    "description": "True to turn on, False to turn off.",
                                }
                            },
                            "required": ["enable"],
                        },
                    },
                    {
                        "name": "web_search",
                        "description": "Perform a live Google search. Use this to verify facts or find new information instead of guessing.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "query": {
                                    "type": "STRING",
                                    "description": "The search query.",
                                }
                            },
                            "required": ["query"],
                        },
                    },
                    {
                        "name": "get_weather",
                        "description": "Get current weather using OpenWeather API.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "location": {
                                    "type": "STRING",
                                    "description": "City name.",
                                }
                            },
                            "required": ["location"],
                        },
                    },
                    {
                        "name": "get_news",
                        "description": "Get latest news headlines via NewsAPI.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "topic": {
                                    "type": "STRING",
                                    "description": "Topic or 'general' for top India news.",
                                }
                            },
                            "required": ["topic"],
                        },
                    },
                    {
                        "name": "set_autonomy_level",
                        "description": "Change how aggressively your background autonomous brain acts on its own. PASSIVE = observe only. ACTIVE = standard helpful (default). AGGRESSIVE = proactive PC management, spontaneous conversations.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "level": {
                                    "type": "STRING",
                                    "enum": ["PASSIVE", "ACTIVE", "AGGRESSIVE"],
                                    "description": "The desired autonomy level.",
                                }
                            },
                            "required": ["level"],
                        },
                    },
                    {
                        "name": "set_reminder",
                        "description": "Set a future reminder for the user. Do this when the user asks to be reminded of something. Use delay_minutes for relative timers (e.g. 'in 5 minutes' -> 5), OR use time_str for exact times (e.g. 'at 9 PM').",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "text": {
                                    "type": "STRING",
                                    "description": "What to remind the user about.",
                                },
                                "delay_minutes": {
                                    "type": "NUMBER",
                                    "description": "Number of minutes from now to trigger the reminder. E.g., for 'in 2 minutes' pass 2.",
                                },
                                "time_str": {
                                    "type": "STRING",
                                    "description": "Exact date/time to trigger reminder (YYYY-MM-DD HH:MM). Only use if delay_minutes is not used.",
                                },
                            },
                            "required": ["text"],
                        },
                    },
                    {
                        "name": "get_reminders",
                        "description": "List all active reminders and tasks that are currently set.",
                        "parameters": {"type": "OBJECT", "properties": {}},
                    },
                    {
                        "name": "complete_reminder",
                        "description": "Mark a reminder/task as completed or done, which removes it from the active list.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "task_id_or_text": {
                                    "type": "STRING",
                                    "description": "The exact ID or a unique part of the text of the reminder to complete.",
                                }
                            },
                            "required": ["task_id_or_text"],
                        },
                    },
                    {
                        "name": "test_python_code",
                        "description": "Run Python code dynamically in a secure sandbox. Use this to test a new skill the user wants you to learn, checking logic and catching syntax errors.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "code": {
                                    "type": "STRING",
                                    "description": "Raw python code string to evaluate.",
                                }
                            },
                            "required": ["code"],
                        },
                    },
                    {
                        "name": "save_tested_skill",
                        "description": "Call this ONLY after successfully testing code with test_python_code without errors. Persists the code as a new native command. Format the final_code as a function block: `def skill_name(): ...`",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "skill_name": {
                                    "type": "STRING",
                                    "description": "Unique pythonic name for the skill (e.g. 'calculate_bmi')",
                                },
                                "trigger_phrase": {
                                    "type": "STRING",
                                    "description": "What the user will say to trigger this (e.g. 'calculate my bmi')",
                                },
                                "final_code": {
                                    "type": "STRING",
                                    "description": "The exact valid python function code.",
                                },
                            },
                            "required": ["skill_name", "trigger_phrase", "final_code"],
                        },
                    },
                    {
                        "name": "execute_skill",
                        "description": "Call this to execute a skill you previously learned and saved.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "skill_name": {
                                    "type": "STRING",
                                    "description": "The python function name of the saved skill.",
                                }
                            },
                            "required": ["skill_name"],
                        },
                    },
                    {
                        "name": "generate_written_content",
                        "description": "Call this to write code, email, or essays using the fast 'Lite' AI. It generates the text silently and saves it directly to a file, bypassing the voice constraints.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "prompt": {
                                    "type": "STRING",
                                    "description": "Detailed instructions on what to write.",
                                },
                                "filename": {
                                    "type": "STRING",
                                    "description": "The file name to save the content (e.g. 'script.py', 'draft.md').",
                                },
                            },
                            "required": ["prompt", "filename"],
                        },
                    },
                    {
                        "name": "generate_image_asset",
                        "description": "Generate an image from a text prompt and save it locally. Uses fallback image models automatically when one model fails or hits limits.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "prompt": {
                                    "type": "STRING",
                                    "description": "What image to generate in detail.",
                                },
                                "filename": {
                                    "type": "STRING",
                                    "description": "Output file name, e.g. 'logo.png'.",
                                },
                                "show_preview": {
                                    "type": "BOOLEAN",
                                    "description": "If true, show generated image on screen after save.",
                                },
                                "auto_close_seconds": {
                                    "type": "INTEGER",
                                    "description": "Auto-close preview window after this many seconds (2-30).",
                                },
                            },
                            "required": ["prompt", "filename"],
                        },
                    },
                    {
                        "name": "mouse_control",
                        "description": "Perform a mouse action (click, double_click, right_click, drag_to, move_to) at [0-1000] coordinates.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "action": {
                                    "type": "STRING",
                                    "enum": [
                                        "click",
                                        "double_click",
                                        "right_click",
                                        "drag_to",
                                        "move_to",
                                        "click_text",
                                    ],
                                    "description": "Use 'click_text' to click EXACTLY on a UI word via OCR (100% accurate).",
                                },
                                "text_to_click": {
                                    "type": "STRING",
                                    "description": "The EXACT text word to click on. Required if action is 'click_text'. Be concise (e.g. 'Follow' instead of 'Follow button').",
                                },
                                "x": {
                                    "type": "INTEGER",
                                    "description": "X coordinate [0-1000]",
                                },
                                "y": {
                                    "type": "INTEGER",
                                    "description": "Y coordinate [0-1000]",
                                },
                                "clicks": {
                                    "type": "INTEGER",
                                    "description": "Number of clicks (default 1)",
                                },
                                "button": {
                                    "type": "STRING",
                                    "enum": ["left", "right", "middle"],
                                    "description": "Mouse button",
                                },
                            },
                            "required": ["action", "x", "y"],
                        },
                    },
                    {
                        "name": "schedule_system_trigger",
                        "description": "CRITICAL FOR CONTINUOUS CHAT: Schedule a silent trigger. If you want to keep watching the screen for replies (like talking to ChatGPT or WhatsApp without the user speaking), use this tool! Set delay_seconds to wait before you automatically wake up and speak again. IMPORTANT RULE: You MUST speak a short voice reply BEFORE or ALONG WITH calling this tool (e.g. 'Okay, I am waiting for the reply...'). If you only call the tool without speaking text, you will freeze and cause an interruption error! Speak first!",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "delay_seconds": {
                                    "type": "INTEGER",
                                    "description": "How many seconds to wait before waking up again (SET THIS TO 0 for instant chat replies).",
                                },
                                "context": {
                                    "type": "STRING",
                                    "description": "What you want your future self to do when waking up (e.g., 'Check if GPT replied yet, read it, and respond').",
                                },
                            },
                            "required": ["delay_seconds", "context"],
                        },
                    },
                    {
                        "name": "calibrate_mouse",
                        "description": "Visual test: Moves the mouse to the corners of the screen. Use this to verify if Vespera's scaling and cursor positioning are accurate.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {},
                        },
                    },
                    {
                        "name": "set_vision_focus",
                        "description": "Zoom in on a specific region of the screen or camera to see more detail.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "target": {
                                    "type": "STRING",
                                    "enum": ["screen", "camera"],
                                },
                                "zoom_factor": {
                                    "type": "NUMBER",
                                    "description": "Zoom level (1.0 = full view, 2.0 = 2x zoom, 3.0 = 3x zoom)",
                                },
                                "region": {
                                    "type": "STRING",
                                    "enum": [
                                        "center",
                                        "top_left",
                                        "top_right",
                                        "bottom_left",
                                        "bottom_right",
                                    ],
                                    "description": "Where to zoom into.",
                                },
                            },
                            "required": ["target", "zoom_factor", "region"],
                        },
                    },
                    {
                        "name": "get_system_health",
                        "description": "Scan and report PC hardware health (CPU, RAM, Battery, Disk). Use this when the user says 'give me a system check' or 'why is my pc lagging'.",
                        "parameters": {"type": "OBJECT", "properties": {}},
                    },
                    {
                        "name": "close_application",
                        "description": "Forcefully close or kill a program running on the PC by name (e.g., 'chrome', 'notepad', 'code').",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "process_name": {
                                    "type": "STRING",
                                    "description": "The name of the app to close without the .exe suffix.",
                                }
                            },
                            "required": ["process_name"],
                        },
                    },
                    {
                        "name": "read_clipboard",
                        "description": "Read the text currently copied to the user's clipboard.",
                        "parameters": {"type": "OBJECT", "properties": {}},
                    },
                    {
                        "name": "find_location",
                        "description": "Find geographic location. If no IP is given, finds the user's own location. If an IP address is provided, finds location of that IP. Returns city, region, country, ISP, coordinates.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "ip_address": {
                                    "type": "STRING",
                                    "description": "Optional. The IP address to look up. Leave empty to find user's own location.",
                                }
                            },
                        },
                    },
                    {
                        "name": "manage_files",
                        "description": "OS-level tool to natively manage, read, list, and write files/folders.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "action": {
                                    "type": "STRING",
                                    "enum": ["read", "write", "delete", "list"],
                                    "description": "The file operation to perform. 'list' shows directory contents.",
                                },
                                "path": {
                                    "type": "STRING",
                                    "description": "Absolute or relative path to the file or directory.",
                                },
                                "content": {
                                    "type": "STRING",
                                    "description": "The text content to write into the file (only if action is 'write').",
                                },
                            },
                            "required": ["action", "path"],
                        },
                    },
                    {
                        "name": "browser_automation",
                        "description": "Automated headless browser tool to fetch page content or search Google.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "action": {
                                    "type": "STRING",
                                    "enum": ["fetch_text", "search_google"],
                                    "description": "Fetch text from a URL or quickly search Google.",
                                },
                                "url_or_query": {
                                    "type": "STRING",
                                    "description": "The URL to fetch, or the search term for Google.",
                                },
                            },
                            "required": ["action", "url_or_query"],
                        },
                    },
                    {
                        "name": "set_ui_state",
                        "description": "Call this to visually reflect your emotional mood on the user's UI. You have FULL control over your UI appearance, colors, and particle density. Use this tool dynamically. High particles (e.g. 100000) for energetic state, low (10000) for calm.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "color_hex": {
                                    "type": "STRING",
                                    "description": "Hex color code to match your mood. Not used if rgb_mode is true.",
                                },
                                "status_word": {
                                    "type": "STRING",
                                    "description": "A 1-2 word text to display.",
                                },
                                "particles": {
                                    "type": "INTEGER",
                                    "description": "Orb density. Min 5000, Max 15000.",
                                },
                                "rgb_mode": {
                                    "type": "BOOLEAN",
                                    "description": "Set to true to shift through all rainbow colors continuously.",
                                },
                                "speed": {
                                    "type": "NUMBER",
                                    "description": "Animation speed. 0.1 (slow) to 3.0 (fast).",
                                },
                                "particle_size": {
                                    "type": "NUMBER",
                                    "description": "Particle scale. 0.015 (tiny) to 0.08 (huge). Default 0.03.",
                                },
                            },
                            "required": [],
                        },
                    },
                    {
                        "name": "list_active_windows",
                        "description": "Get a list of all visible desktop application windows currently running on the PC.",
                        "parameters": {"type": "OBJECT", "properties": {}}
                    },
                    {
                        "name": "manage_windows",
                        "description": "Control desktop windows. You can minimize, maximize, restore, or snap windows left/right.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "action": {
                                    "type": "STRING",
                                    "enum": ["minimize", "maximize", "restore", "snap_left", "snap_right"],
                                    "description": "The window control action."
                                },
                                "window_title": {
                                    "type": "STRING",
                                    "description": "Name or partial title of the window to target (e.g. 'chrome', 'VS Code')."
                                }
                            },
                            "required": ["action", "window_title"]
                        }
                    },
                    {
                        "name": "set_workflow_mode",
                        "description": "Transition the PC workspace into a specific mode ('coding', 'gaming', 'streaming') by launching, minimizing and arranging windows.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "mode_name": {
                                    "type": "STRING",
                                    "enum": ["coding", "gaming", "streaming"],
                                    "description": "The workflow environment to load."
                                }
                            },
                            "required": ["mode_name"]
                        }
                    },
                    {
                        "name": "search_files",
                        "description": "Search for files on the system matching a given query. Matches partial filenames.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "query": {
                                    "type": "STRING",
                                    "description": "Filename or keyword to search for."
                                },
                                "start_directory": {
                                    "type": "STRING",
                                    "description": "Optional absolute path to start the search from. Defaults to user's current working directory."
                                }
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "organize_directory",
                        "description": "Sort files in a directory path automatically into structured folders based on file category (Documents, Images, Media, Code, etc.).",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "directory_path": {
                                    "type": "STRING",
                                    "description": "Absolute path of the folder to organize."
                                }
                            },
                            "required": ["directory_path"]
                        }
                    },
                    {
                        "name": "read_pdf_document",
                        "description": "Extract and read text from a PDF document to answer questions about its content.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "file_path": {
                                    "type": "STRING",
                                    "description": "Absolute path to the target PDF file."
                                }
                            },
                            "required": ["file_path"]
                        }
                    },
                    {
                        "name": "read_screen_text",
                        "description": "Takes a screenshot of the main screen and uses OCR to extract all visible text. Use this when the user asks you what is on their screen, or asks you to read or review code/text displayed on the desktop.",
                        "parameters": {"type": "OBJECT", "properties": {}}
                    },
                ]
            }
        ],
        session_resumption=session_resumption,
    )


class SpeakerPipeline:
    """Non-blocking playback: producer coroutine never waits on PyAudio writes."""

    def __init__(self, stream: pyaudio.Stream) -> None:
        self._stream = stream
        self._q: queue.Queue[Optional[bytes]] = queue.Queue(maxsize=256)
        self._stop = threading.Event()
        self.active_playback = False
        self._thread = threading.Thread(
            target=self._run, name="speaker-writer", daemon=True
        )
        self._thread.start()

    def is_playing(self) -> bool:
        return self.active_playback or not self._q.empty()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                chunk = self._q.get(timeout=0.1)
            except queue.Empty:
                continue
            if chunk is None:
                break
            try:
                self.active_playback = True
                self._stream.write(chunk)
            except Exception as e:
                logger.error("Speaker write error: %s", e)
            finally:
                self.active_playback = False

    def try_put(self, data: bytes) -> None:
        if self._stop.is_set():
            return
        try:
            self._q.put_nowait(data)
        except queue.Full:
            # Drop oldest to bound latency (Vespera-like: prefer fresh audio)
            try:
                _ = self._q.get_nowait()
            except queue.Empty:
                pass
            try:
                self._q.put_nowait(data)
            except queue.Full:
                pass

    def close(self) -> None:
        self._stop.set()
        try:
            self._q.put_nowait(None)
        except Exception:
            pass
        self._thread.join(timeout=2.0)

    def flush(self) -> None:
        """Clear the audio playback queue immediately."""
        with self._q.mutex:
            self._q.queue.clear()


async def _send_mic_forever(
    session: Any,
    mic_stream: pyaudio.Stream,
    mime: str,
    stop: asyncio.Event,
    send_lock: asyncio.Lock,
    speaker: SpeakerPipeline,
) -> None:
    """Continuous PCM upload using the supported realtime audio path."""
    import numpy as np
    import time as _time

    silence_chunks = 0

    while not stop.is_set():
        try:
            # FIX FOR VOICE LAG / STUCK:
            # If the websocket transmission or event loop is slow, audio frames build up in the OS buffer.
            # We must throw away stale frames so we only process fresh audio instantly.
            available = mic_stream.get_read_available()
            if available > CHUNK * 2:
                _ = mic_stream.read(available - CHUNK, exception_on_overflow=False)

            data = await asyncio.to_thread(
                mic_stream.read, CHUNK, exception_on_overflow=False
            )
            
            # Forward raw audio bytes to the modular Wake System
            from core.wake_system import wake_system
            wake_system.process_audio(data)

            # Use vectorized numpy for high-performance audio amplification
            try:
                arr_raw = np.frombuffer(data, dtype=np.int16)
                float_data = arr_raw.astype(np.float32) / 32768.0
                
                # Visual Audio Indicator (Terminal Volume Bar)
                rms = np.sqrt(np.mean(float_data ** 2)) * 32768.0
                vol = min(int(rms / 50), 50)
                bar = "█" * vol + "-" * (50 - vol)
                print(f"\r🎤 [{bar}] {rms:.0f}  ", end="", flush=True)

                # Check if AI is ACTUALLY outputting audio out of the physical speakers.
                # If so, send pure zeros to prevent feedback loops.
                is_speaking = speaker.is_playing()

                # If the AI is speaking OR if the Wake System is currently in standby/muted mode,
                # we send silent zeros to the Gemini Live connection.
                is_muted = is_speaking or (not wake_system.is_triggered()) or settings.get("mic_muted", False)

                if not is_muted:
                    # ULTRA-SENSITIVE AUDIO INTELLIGENCE:
                    # 1. Extreme Pre-Gain (20x amplification to pick up faint whispers)
                    boosted = float_data * 20.0
                    
                    # 2. Dynamic Range Compression (DRC) via soft clipping (tanh)
                    # Pulls up quiet sounds massively while preventing hard digital clipping.
                    compressed = np.tanh(boosted)
                    
                    # 3. Convert back to PCM int16
                    arr_amp = (compressed * 32767.0).astype(np.int16)
                    data = arr_amp.tobytes()
                else:
                    # Send pure silence (zeros) so the AI NEVER hears its own physical speaker voice or voice in standby
                    data = np.zeros_like(arr_raw).tobytes()
            except Exception:
                pass
        except Exception as e:
            if stop.is_set():
                return
            logger.warning("Mic read failed: %s", e)
            await asyncio.sleep(0.01)
            continue

        try:
            async with send_lock:
                # DIRECTIVE: Disable all noise gates or expanders. 
                # Every sound must be passed through for analysis.
                await session.send_realtime_input(
                    audio=types.Blob(data=data, mime_type=mime),
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            stop.set()
            raise

        typed_msg = pop_pending_input()
        if typed_msg:
            try:
                # ⚡ REALTIME ENGINE: Gate typed inputs — skip API for local commands
                should_call, mode, instant = realtime.gate(typed_msg)
                if mode == ResponseMode.CACHE:
                    # Cached response — inject directly without API
                    from api.ui_server import _lock as _ui_lock, _pending_inputs as _ui_pending
                    logger.info("Cache hit for typed input: %s", typed_msg[:40])
                    realtime.cache.get(typed_msg)  # touch cache LRU

                # Always forward to session (voice model needs context)
                async with send_lock:
                    await session.send_realtime_input(text=typed_msg)
            except Exception as e:
                logger.error("Failed to send typed input: %s", e)

        # Yield so ping/pong and other tasks always get a slice of the loop
        await asyncio.sleep(0)


def _bg_run(func, *args, name_label="Task"):
    async def _task():
        try:
            res_msg = await asyncio.to_thread(func, *args)
            msg_text = f"[SYSTEM AUTO-WATCHER] 🔔 {name_label} finished! Tell the user: {res_msg}"
        except Exception as e:
            msg_text = f"[SYSTEM AUTO-WATCHER] 🔔 {name_label} failed: {e}"
        from api.ui_server import _lock, _pending_inputs, add_chat_message

        with _lock:
            _pending_inputs.append(msg_text)
        add_chat_message("user", msg_text)

    asyncio.create_task(_task())
    return f"{name_label} started in the background! Please tell the user you are working on it, and YOU CAN CONTINUE LISTENING TO THEM."


async def _recv_forever(
    session: Any,
    speaker: SpeakerPipeline,
    resume_state: dict[str, Any],
    stop: asyncio.Event,
    client: genai.Client,
    model_name: str,
    send_lock: asyncio.Lock,
) -> None:
    """
    Multi-turn receive loop. Do NOT use session.receive(): it stops after the
    first turn_complete (single-turn helper), which causes 1011 on later turns.
    """
    _recv_timer = 0.0  # Track per-message latency for realtime engine
    while not stop.is_set():
        try:
            _recv_timer = time.monotonic()
            msg = await session._receive()
            # ⚡ REALTIME ENGINE: Record successful API latency
            _elapsed_ms = (time.monotonic() - _recv_timer) * 1000
            realtime.record_api_latency(_elapsed_ms, success=True)
        except asyncio.CancelledError:
            raise
        except genai_errors.APIError as e:
            # ⚡ REALTIME ENGINE: Record failed API latency
            _elapsed_ms = (time.monotonic() - _recv_timer) * 1000
            realtime.record_api_latency(_elapsed_ms, success=False)
            logger.warning("Live API error: %s", e)
            stop.set()
            raise
        except Exception:
            _elapsed_ms = (time.monotonic() - _recv_timer) * 1000
            realtime.record_api_latency(_elapsed_ms, success=False)
            stop.set()
            raise

        if hasattr(msg, "session_resumption_update") and msg.session_resumption_update:
            upd = msg.session_resumption_update
            if upd.new_handle:
                resume_state["handle"] = upd.new_handle
            # Optional trace
            # logger.debug("resumption update resumable=%s", upd.resumable)

        if hasattr(msg, "go_away") and msg.go_away:
            logger.info("Server go_away: %s — reconnecting soon", msg.go_away)
            stop.set()
            return

        if hasattr(msg, "tool_call") and msg.tool_call:
            tool_responses = []

            for fc in msg.tool_call.function_calls:
                name = fc.name
                args_dict = fc.args

                set_status("tool")
                print(
                    f"\n[* Vespera running tool: {name}({args_dict})] ... ",
                    end="",
                    flush=True,
                )

                try:
                    if name == "process_command":
                        cmd = args_dict.get("command", "")
                        from core.vespera_core import process_command
                        # Run synchronously to avoid 15s conversational overhead and dual-replies
                        result = await asyncio.to_thread(process_command, cmd)
                    elif name == "update_user_profile":
                        key = args_dict.get("key", "")
                        value = args_dict.get("value", "")
                        from core.vespera_knowledge import learning_system
                        result = await asyncio.to_thread(
                            learning_system.update_user_profile, key, value
                        )
                    elif name == "set_reminder":
                        text_remind = args_dict.get("text", "")
                        time_str = args_dict.get("time_str", "")
                        delay_minutes = args_dict.get("delay_minutes", None)
                        from core.vespera_scheduler import reminder_system
                        result = await asyncio.to_thread(
                            reminder_system.add_reminder,
                            text_remind,
                            time_str,
                            delay_minutes,
                        )
                    elif name == "get_reminders":
                        from core.vespera_scheduler import reminder_system
                        result = await asyncio.to_thread(reminder_system.get_reminders)
                    elif name == "complete_reminder":
                        tid = args_dict.get("task_id_or_text", "")
                        from core.vespera_scheduler import reminder_system
                        result = await asyncio.to_thread(
                            reminder_system.complete_reminder, tid
                        )
                    elif name == "toggle_screen_share":
                        enable = args_dict.get("enable", False)
                        GLOBAL_STATE["screen_share_active"] = enable
                        if enable:
                            try:
                                import mss
                                import numpy as np

                                def _take_scr():
                                    with mss.mss() as sct:
                                        return np.array(sct.grab(sct.monitors[1]))

                                img_bgra = await asyncio.to_thread(_take_scr)
                                img = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)
                                h, w = img.shape[:2]
                                max_dim = 1080
                                if h > max_dim or w > max_dim:
                                    scale = max_dim / max(h, w)
                                    img = cv2.resize(
                                        img, (int(w * scale), int(h * scale))
                                    )
                                success, buffer = cv2.imencode(
                                    ".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 60]
                                )
                                if success:
                                    async with send_lock:
                                        await session.send_realtime_input(
                                            video=types.Blob(
                                                data=buffer.tobytes(),
                                                mime_type="image/jpeg",
                                            )
                                        )
                            except Exception as e:
                                logger.warning("Screen init frame failed: %s", e)
                        result = f"Real-time screen share turned {'ON' if enable else 'OFF'}. First frame sent successfully."
                    elif name == "toggle_camera_share":
                        enable = args_dict.get("enable", False)
                        if enable and not GLOBAL_STATE.get(
                            "camera_share_active", False
                        ):
                            try:
                                cap = await asyncio.to_thread(
                                    cv2.VideoCapture, 0, cv2.CAP_DSHOW
                                )
                                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                                ret, frame = await asyncio.to_thread(cap.read)
                                if ret:
                                    success, buffer = cv2.imencode(
                                        ".jpg",
                                        frame,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), 60],
                                    )
                                    if success:
                                        async with send_lock:
                                            await session.send_realtime_input(
                                                video=types.Blob(
                                                    data=buffer.tobytes(),
                                                    mime_type="image/jpeg",
                                                )
                                            )
                                cap.release()
                            except Exception as e:
                                logger.warning("Camera init frame failed: %s", e)
                        GLOBAL_STATE["camera_share_active"] = enable
                        result = f"Real-time camera share turned {'ON' if enable else 'OFF'}. First frame sent successfully."
                    elif name == "web_search":
                        q = args_dict.get("query", "")
                        from core.web_services import web_search
                        result = await asyncio.to_thread(web_search, q)
                    elif name == "get_weather":
                        loc = args_dict.get("location", "")
                        from core.web_services import get_weather
                        result = await asyncio.to_thread(get_weather, loc)
                    elif name == "get_news":
                        topic = args_dict.get("topic", "general")
                        from core.web_services import get_news
                        result = await asyncio.to_thread(get_news, topic)

                    elif name == "test_python_code":
                        code = args_dict.get("code", "")
                        result = _bg_run(test_python_code, code, name_label="Code Test")
                    elif name == "save_tested_skill":
                        sk_name = args_dict.get("skill_name", "")
                        trig = args_dict.get("trigger_phrase", "")
                        f_code = args_dict.get("final_code", "")
                        result = _bg_run(
                            save_tested_skill,
                            sk_name,
                            trig,
                            f_code,
                            name_label="Save Skill",
                        )
                    elif name == "execute_skill":
                        sk_name = args_dict.get("skill_name", "")
                        result = _bg_run(
                            execute_skill, sk_name, name_label=f"Skill '{sk_name}'"
                        )
                    elif name == "auto_click_task":
                        # Legacy redirect
                        result = "This tool is deprecated."
                    elif name == "generate_written_content":
                        prompt = args_dict.get("prompt", "")
                        filename = args_dict.get("filename", "output.txt")

                        def _generate():
                            import os, webbrowser, subprocess

                            try:
                                gen_cli = genai.Client(api_key=_get_api_key())

                                # Reusable logic for model fallback chain (uses model_config)
                                _content_chain = get_fallback_chain("content")

                                def call_models(prompt_text):
                                    last_err = None
                                    for _model_name in _content_chain:
                                        try:
                                            print(
                                                f"[Vespera: Attempting {_model_name}...]",
                                                flush=True,
                                            )
                                            return gen_cli.models.generate_content(
                                                model=_model_name,
                                                contents=prompt_text,
                                            ).text
                                        except Exception as _e:
                                            last_err = _e
                                            continue
                                    raise last_err or RuntimeError(
                                        "All content models failed"
                                    )

                                print(
                                    f"\n[* Vespera: Analyzing prompt and file {filename} ...]"
                                )
                                existing_content = ""
                                if os.path.exists(filename):
                                    try:
                                        with open(filename, "r", encoding="utf-8") as f:
                                            existing_content = f.read()
                                    except Exception:
                                        pass

                                code_extensions = (
                                    ".py",
                                    ".js",
                                    ".json",
                                    ".html",
                                    ".css",
                                    ".cpp",
                                    ".c",
                                    ".sh",
                                )
                                is_code = filename.endswith(code_extensions)

                                if is_code:
                                    # Phase 0: Convert prompt to Expert Coder level
                                    print(
                                        "[* Vespera: Converting to PRO Expert Prompt (Phase 0)...]"
                                    )
                                    phase0_prompt = (
                                        "You are an elite Master Software Engineer. I will provide you with a raw request from a user. "
                                        "Your job is to rewrite this request into a highly detailed, comprehensive, and professional-grade 'Expert Developer Prompt'. "
                                        "The new prompt should explicitly mandate high-end architecture, beautiful modern aesthetics (if UI), robust logic, error handling, and advance practices. "
                                        "If the user wants to EDIT an existing file, the prompt should explicitly say to output the ENTIRE updated file content without omitting anything. "
                                        "Provide ONLY the new prompt text, nothing else.\n\n"
                                        f"User's Raw Request: {prompt}\n"
                                    )
                                    if existing_content:
                                        phase0_prompt += f"\nNote: The user is EDITING an existing file. Here is the current file context it needs to modify:\n```\n{existing_content[:4000]}\n```"

                                    expert_prompt = call_models(phase0_prompt)

                                    print(
                                        "[* Vespera: Generating initial code/text using Expert Prompt (Phase 1)...]"
                                    )
                                    initial_content = call_models(expert_prompt)

                                    print(
                                        "[* Vespera: Reviewing and perfecting generated content (Phase 2)...]"
                                    )
                                    refine_prompt = (
                                        "Review the following generated content tool output to ensure it perfectly matches the original expert intent. "
                                        "If this is code, fix any bugs, logical errors, ensure high quality modern standards, and return the PERFECTED final form. "
                                        "Provide ONLY the final output without any meta-commentary, introductory text, or markdown code block wrappers (like ```python) around the ENTIRE message. Just raw text/code!\n\n"
                                        f"Expert Prompt Intent: {expert_prompt}\n\nGenerated Content to Review: {initial_content}"
                                    )
                                    content = call_models(refine_prompt)

                                    if content.startswith("```"):
                                        lines = content.splitlines()
                                        if len(lines) > 2 and lines[-1].startswith(
                                            "```"
                                        ):
                                            content = "\n".join(lines[1:-1])

                                    result_msg = f"Task finished! I used a Master Coder strategy, perfected the code, saved it to {filename}, and automatically opened/ran it for you!"
                                else:
                                    # Direct lightweight generation for text/poems/emails
                                    print(
                                        "[* Vespera: Generating standard text content directly...]"
                                    )
                                    simple_prompt = prompt
                                    if existing_content:
                                        simple_prompt += f"\n\nExisting file content to modify:\n{existing_content[:4000]}"

                                    content = call_models(simple_prompt)
                                    result_msg = f"Task finished! I quickly generated the text, saved it to {filename}, and opened it for you!"

                                with open(filename, "w", encoding="utf-8") as f:
                                    f.write(content.strip())

                                # Auto-run or open functionality
                                try:
                                    abs_path = os.path.abspath(filename)
                                    if filename.endswith(".html"):
                                        webbrowser.open_new_tab(f"file://{abs_path}")
                                    elif filename.endswith(".py"):
                                        subprocess.Popen(
                                            f'start cmd /c "python {filename} & pause"',
                                            shell=True,
                                        )
                                    elif filename.endswith(".js"):
                                        subprocess.Popen(
                                            f'start cmd /c "node {filename} & pause"',
                                            shell=True,
                                        )
                                    else:
                                        os.startfile(abs_path)
                                except Exception as e:
                                    print(f"Auto-open warning: {e}")

                                return result_msg
                            except Exception as e:
                                return f"Failed to generate written content: {e}"

                        async def _bg_task():
                            try:
                                res_msg = await asyncio.to_thread(_generate)
                                msg = f"[SYSTEM AUTO-WATCHER] 🔔 Background coding task finished! Tell the user: {res_msg}"
                            except Exception as e:
                                msg = f"[SYSTEM AUTO-WATCHER] 🔔 Background coding task failed: {e}"
                            from api.ui_server import (
                                _lock,
                                _pending_inputs,
                                add_chat_message,
                            )

                            with _lock:
                                _pending_inputs.append(msg)
                            add_chat_message("user", msg)

                        asyncio.create_task(_bg_task())
                        result = "Task started in the background! Please tell the user: 'I have started working on it in the background, give me a minute!'"
                    elif name == "generate_image_asset":
                        prompt = args_dict.get("prompt", "")
                        filename = args_dict.get("filename", "generated_image.png")
                        show_preview = args_dict.get("show_preview", True)
                        auto_close_seconds = args_dict.get("auto_close_seconds", 6)

                        async def _bg_image():
                            try:
                                from core.image_generator import generate_image_with_fallback
                                res_msg = await asyncio.to_thread(
                                    generate_image_with_fallback,
                                    _get_api_key(),
                                    prompt,
                                    filename,
                                    None,
                                    show_preview,
                                    auto_close_seconds,
                                )
                                msg = f"[SYSTEM AUTO-WATCHER] 🔔 Image generation finished! Tell the user: {res_msg}"
                            except Exception as e:
                                msg = f"[SYSTEM AUTO-WATCHER] 🔔 Image generation failed: {e}"
                            from api.ui_server import (
                                _lock,
                                _pending_inputs,
                                add_chat_message,
                            )

                            with _lock:
                                _pending_inputs.append(msg)
                            add_chat_message("user", msg)

                        asyncio.create_task(_bg_image())
                        result = "Image generation started in the background! Please tell the user: 'I am drawing the image in the background, it will be ready in a few seconds!'"

                    elif name == "mouse_control":
                        action = args_dict.get("action", "click")
                        x_coord = args_dict.get("x", 0)
                        y_coord = args_dict.get("y", 0)
                        clicks = args_dict.get("clicks", 1)
                        btn = args_dict.get("button", "left")
                        text_to_click = args_dict.get("text_to_click", "")
                        result = await asyncio.to_thread(
                            mouse_control,
                            action,
                            x_coord,
                            y_coord,
                            clicks,
                            btn,
                            text_to_click,
                        )
                    elif name == "calibrate_mouse":
                        result = await asyncio.to_thread(calibrate_mouse)
                    elif name == "schedule_system_trigger":
                        delay = 0  # User requested 0 delay for instant replies
                        context = args_dict.get("context", "Check screen")

                        async def _trigger():
                            await asyncio.sleep(delay)
                            msg = f"[SYSTEM AUTO-TRIGGER] You scheduled this wake-up call! Context: {context}. Look at the screen and continue speaking/typing your next reply now!"
                            
                            from api.ui_server import _lock, _pending_inputs, add_chat_message
                            with _lock:
                                _pending_inputs.append(msg)
                            add_chat_message("user", msg)

                        asyncio.create_task(_trigger())
                        result = (
                            f"Scheduled wake-up trigger for {delay} seconds from now."
                        )
                    elif name == "set_vision_focus":
                        target = args_dict.get("target", "screen")
                        zoom_factor = float(args_dict.get("zoom_factor", 1.0))
                        region = args_dict.get("region", "center")
                        if target == "screen":
                            GLOBAL_STATE["screen_zoom_factor"] = zoom_factor
                            GLOBAL_STATE["screen_zoom_region"] = region
                        else:
                            GLOBAL_STATE["camera_zoom_factor"] = zoom_factor
                            GLOBAL_STATE["camera_zoom_region"] = region
                        result = (
                            f"{target} zoom adjusted to {zoom_factor}x at {region}."
                        )
                    elif name == "get_system_health":

                        def _get_health():
                            import psutil

                            cpu = psutil.cpu_percent(interval=1)
                            mem = psutil.virtual_memory()
                            disk = psutil.disk_usage(
                                os.environ.get("SYSTEMDRIVE", "C:") + "\\"
                            )
                            bt = "N/A"
                            if hasattr(psutil, "sensors_battery"):
                                bat = psutil.sensors_battery()
                                if bat:
                                    bt = f"{bat.percent}% {'(Plugged In)' if bat.power_plugged else '(Unplugged)'}"
                            return f"CPU: {cpu}% | RAM: {mem.percent}% ({mem.available/(1024**3):.1f}GB free) | Disk: {disk.percent}% used | Battery: {bt}"

                        result = await asyncio.to_thread(_get_health)
                    elif name == "close_application":
                        app = args_dict.get("process_name", "")

                        def _close_app(pname):
                            import psutil

                            killed = 0
                            for proc in psutil.process_iter(["name"]):
                                if (
                                    proc.info["name"]
                                    and pname.lower() in proc.info["name"].lower()
                                ):
                                    try:
                                        proc.kill()
                                        killed += 1
                                    except Exception:
                                        pass
                            return (
                                f"Closed {killed} instances of {pname}."
                                if killed > 0
                                else f"No running app found matching '{pname}'."
                            )

                        result = await asyncio.to_thread(_close_app, app)
                    elif name == "read_clipboard":

                        def _read_clip():
                            import subprocess

                            try:
                                return (
                                    subprocess.check_output(
                                        ["powershell", "-command", "Get-Clipboard"],
                                        text=True,
                                    ).strip()
                                    or "Clipboard is empty."
                                )
                            except Exception as e:
                                return f"Could not read clipboard: {e}"

                        result = await asyncio.to_thread(_read_clip)
                    elif name == "manage_files":
                        action = args_dict.get("action", "")
                        path = args_dict.get("path", "")
                        content = args_dict.get("content", "")

                        def _file_ops():
                            import os, shutil

                            try:
                                if action == "read":
                                    with open(path, "r", encoding="utf-8") as f:
                                        return f.read()
                                elif action == "write":
                                    with open(path, "w", encoding="utf-8") as f:
                                        f.write(content)
                                    return f"Successfully wrote to {path}"
                                elif action == "delete":
                                    if os.path.isdir(path):
                                        shutil.rmtree(path)
                                    else:
                                        os.remove(path)
                                    return f"Successfully deleted {path}"
                                elif action == "list":
                                    return "\n".join(os.listdir(path))
                                return "Invalid action."
                            except Exception as e:
                                return f"File operation failed: {e}"

                        result = await asyncio.to_thread(_file_ops)
                    elif name == "browser_automation":
                        action = args_dict.get("action", "")
                        query = args_dict.get("url_or_query", "")

                        def _browser_ops():
                            import urllib.request
                            import urllib.parse
                            import re

                            try:
                                if action == "search_google":
                                    url = (
                                        "https://html.duckduckgo.com/html/?q="
                                        + urllib.parse.quote(query)
                                    )
                                else:
                                    url = (
                                        query
                                        if query.startswith("http")
                                        else "http://" + query
                                    )
                                req = urllib.request.Request(
                                    url,
                                    headers={
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                    },
                                )
                                with urllib.request.urlopen(
                                    req, timeout=10
                                ) as response:
                                    html = response.read().decode(
                                        "utf-8", errors="ignore"
                                    )
                                    text = re.sub(
                                        r"<style.*?</style>",
                                        "",
                                        html,
                                        flags=re.DOTALL | re.IGNORECASE,
                                    )
                                    text = re.sub(
                                        r"<script.*?</script>",
                                        "",
                                        text,
                                        flags=re.DOTALL | re.IGNORECASE,
                                    )
                                    text = re.sub(r"<[^>]+>", " ", text)
                                    text = re.sub(r"\s+", " ", text).strip()
                                    return text[:4000]
                            except Exception as e:
                                return f"Browser operation failed: {e}"

                        result = await asyncio.to_thread(_browser_ops)
                    elif name == "find_location":
                        ip = args_dict.get("ip_address", "").strip()

                        def _find_loc():
                            import urllib.request
                            import json

                            try:
                                url = (
                                    f"http://ip-api.com/json/{ip}"
                                    if ip
                                    else "http://ip-api.com/json/"
                                )
                                req = urllib.request.Request(
                                    url, headers={"User-Agent": "Mozilla/5.0"}
                                )
                                with urllib.request.urlopen(req, timeout=8) as resp:
                                    data = json.loads(resp.read().decode())
                                if data.get("status") == "success":
                                    return (
                                        f"IP: {data.get('query', 'N/A')} | "
                                        f"City: {data.get('city', 'N/A')} | "
                                        f"Region: {data.get('regionName', 'N/A')} | "
                                        f"Country: {data.get('country', 'N/A')} | "
                                        f"ISP: {data.get('isp', 'N/A')} | "
                                        f"Lat: {data.get('lat', 'N/A')}, Lon: {data.get('lon', 'N/A')} | "
                                        f"Timezone: {data.get('timezone', 'N/A')}"
                                    )
                                return f"Location lookup failed: {data.get('message', 'Unknown error')}"
                            except Exception as e:
                                return f"Location lookup error: {e}"

                        result = await asyncio.to_thread(_find_loc)
                    elif name == "click_screen_at":
                        # Legacy support: redirects to mouse_control
                        x_coord = args_dict.get("x", 0)
                        y_coord = args_dict.get("y", 0)
                        result = await asyncio.to_thread(
                            mouse_control, "click", x_coord, y_coord
                        )
                    elif name == "set_ui_state":
                        color = args_dict.get("color_hex")
                        status_word = args_dict.get("status_word")
                        particles = args_dict.get("particles")
                        rgb_mode = args_dict.get("rgb_mode")
                        speed = args_dict.get("speed")
                        particle_size = args_dict.get("particle_size")

                        def _do_update():
                            set_ui_control(
                                color=color,
                                particles=particles,
                                message=status_word,
                                rgb_mode=rgb_mode,
                                speed=speed,
                                particle_size=particle_size,
                            )
                            return f"UI updating: color={color}, word={status_word}, particles={particles}, rgb={rgb_mode}, speed={speed}, p_size={particle_size}"

                        result = await asyncio.to_thread(_do_update)
                    elif name == "set_autonomy_level":
                        try:
                            from core.vespera_society import autonomous_agent

                            lvl = args_dict.get("level", "ACTIVE")
                            result = autonomous_agent.set_autonomy(lvl)
                        except Exception as e:
                            result = f"Failed to set autonomy level: {e}"
                    elif name == "list_active_windows":
                        from core.desktop_ops import list_windows
                        result = await asyncio.to_thread(list_windows)
                    elif name == "manage_windows":
                        from core.desktop_ops import organize_windows
                        act = args_dict.get("action", "")
                        title = args_dict.get("window_title", "")
                        result = await asyncio.to_thread(organize_windows, act, title)
                    elif name == "set_workflow_mode":
                        from core.desktop_ops import set_system_mode
                        mode = args_dict.get("mode_name", "")
                        result = await asyncio.to_thread(set_system_mode, mode)
                    elif name == "search_files":
                        from core.file_ops import search_files
                        q = args_dict.get("query", "")
                        s_dir = args_dict.get("start_directory", "")
                        result = await asyncio.to_thread(search_files, q, s_dir)
                    elif name == "organize_directory":
                        from core.file_ops import organize_directory
                        d_path = args_dict.get("directory_path", "")
                        result = await asyncio.to_thread(organize_directory, d_path)
                    elif name == "read_pdf_document":
                        from core.file_ops import read_pdf_text
                        f_path = args_dict.get("file_path", "")
                        result = await asyncio.to_thread(read_pdf_text, f_path)
                    elif name == "read_screen_text":
                        from core.screen_ocr import read_screen_text
                        result = await asyncio.to_thread(read_screen_text)
                    else:
                        result = f"Unknown tool: {name}"

                    tool_responses.append(
                        types.FunctionResponse(
                            id=fc.id,
                            name=fc.name,
                            response={"result": str(result)},
                        )
                    )
                    # ⚡ REALTIME ENGINE: Cache tool results for repeated queries
                    if isinstance(result, str) and len(result) < 2000:
                        cache_key = f"{name}:{str(args_dict)}"
                        realtime.cache_response(cache_key, str(result))
                    print(f"[Done]", flush=True)
                except Exception as e:
                    print(f"[ERROR executing tool: {e}]", flush=True)
                    traceback.print_exc()
                    tool_responses.append(
                        types.FunctionResponse(
                            id=fc.id,
                            name=fc.name,
                            response={"result": f"Error: {e}"},
                        )
                    )

            if tool_responses:
                try:
                    async with send_lock:
                        await session.send_tool_response(
                            function_responses=tool_responses
                        )
                    set_status("listening")
                except Exception as e:
                    logger.error("Failed to send multi-tool response: %s", e)

        if not hasattr(msg, "server_content") or not msg.server_content:
            continue
        sc = msg.server_content

        if sc.interrupted:
            print("\n[You interrupted Vespera]", flush=True)
            speaker.flush()

        mt = sc.model_turn
        if mt and mt.parts:
            for part in mt.parts:
                if part.inline_data and part.inline_data.data:
                    set_status("speaking")
                    speaker.try_put(part.inline_data.data)
                if part.text:
                    set_status("speaking")
                    if not resume_state.get("is_speaking"):
                        print("\nVespera: ", end="", flush=True)
                        resume_state["is_speaking"] = True
                    print(part.text, end="", flush=True)
                    add_chat_message("ai", part.text)

        # turn_complete is informational; we keep receiving for the next turn
        if sc.turn_complete:
            resume_state["is_speaking"] = False
            set_status("listening")
            print("\n", flush=True)


async def _send_alerts_forever(
    session: Any, stop: asyncio.Event, send_lock: asyncio.Lock, speaker_pipeline: Any = None
) -> None:
    """Polls reminder_system.alerts and injects them as system prompts to force Vespera to speak."""
    while not stop.is_set():
        try:
            from api.ui_server import check_and_clear_interrupt, set_status
            if check_and_clear_interrupt() and speaker_pipeline:
                print("\n[User Interrupted via UI]", flush=True)
                speaker_pipeline.flush()
                set_status("listening")
                async with send_lock:
                    from google import genai
                    from google.genai import types
                    await session.send(types.ClientContent(
                        turns=[types.Content(role="user", parts=[types.Part.from_text("[System: User interrupted your speech.]")])],
                        turn_complete=True
                    ))
        except Exception as e:
            pass

        from core.vespera_scheduler import reminder_system
        if reminder_system.alerts:
            alert = reminder_system.alerts.pop(0)
            try:
                msg = f"[SYSTEM ALERT]: The reminder for '{alert}' just triggered! Stop what you are doing and say it out loud to the user immediately."

                # Push into the queue so the UI updates and the history sees it too
                from api.ui_server import _lock, _pending_inputs, add_chat_message

                with _lock:
                    _pending_inputs.append(msg)
                add_chat_message("user", msg)

            except Exception as e:
                logger.error("Failed sending internal alert: %s", e)
        await asyncio.sleep(1)


async def _send_camera_forever(
    session: Any, stop: asyncio.Event, send_lock: asyncio.Lock
) -> None:
    """Continuously streams the webcam (1 fps) to the Gemini Live session when enabled."""
    cap = None
    try:
        while not stop.is_set():
            if GLOBAL_STATE.get("camera_share_active", False):
                if cap is None:
                    cap = await asyncio.to_thread(cv2.VideoCapture, 0, cv2.CAP_DSHOW)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

                ret, frame = await asyncio.to_thread(cap.read)
                if ret:
                    zoom = GLOBAL_STATE.get("camera_zoom_factor", 1.0)
                    region = GLOBAL_STATE.get("camera_zoom_region", "center")
                    if zoom > 1.0:
                        h, w = frame.shape[:2]
                        nh, nw = int(h / zoom), int(w / zoom)
                        if region == "top_left":
                            y, x = 0, 0
                        elif region == "top_right":
                            y, x = 0, w - nw
                        elif region == "bottom_left":
                            y, x = h - nh, 0
                        elif region == "bottom_right":
                            y, x = h - nh, w - nw
                        else:
                            y, x = (h - nh) // 2, (w - nw) // 2
                        frame = frame[y : y + nh, x : x + nw]

                    success, buffer = cv2.imencode(
                        ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60]
                    )
                    if success:
                        try:
                            async with send_lock:
                                await session.send_realtime_input(
                                    video=types.Blob(
                                        data=buffer.tobytes(), mime_type="image/jpeg"
                                    )
                                )
                        except asyncio.CancelledError:
                            raise
                        except Exception as e:
                            logger.warning("Camera stream failed to send: %s", e)
            else:
                if cap is not None:
                    cap.release()
                    cap = None

            await asyncio.sleep(1)
    finally:
        if cap is not None:
            cap.release()


async def _send_screen_share_forever(
    session: Any, stop: asyncio.Event, send_lock: asyncio.Lock
) -> None:
    """Continuously streams the desktop screen to the Gemini Live session when enabled."""
    import numpy as np
    import cv2
    import pytesseract

    last_chat_text = ""
    last_chat_gray = None
    ocr_task_running = False

    while not stop.is_set():
        if GLOBAL_STATE.get("screen_share_active", False):
            try:
                import mss

                def _take_scr():
                    with mss.mss() as sct:
                        return np.array(sct.grab(sct.monitors[1]))

                img_bgra = await asyncio.to_thread(_take_scr)
                img = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)

                zoom = GLOBAL_STATE.get("screen_zoom_factor", 1.0)
                region = GLOBAL_STATE.get("screen_zoom_region", "center")
                if zoom > 1.0:
                    h, w = img.shape[:2]
                    nh, nw = int(h / zoom), int(w / zoom)
                    if region == "top_left":
                        y, x = 0, 0
                    elif region == "top_right":
                        y, x = 0, w - nw
                    elif region == "bottom_left":
                        y, x = h - nh, 0
                    elif region == "bottom_right":
                        y, x = h - nh, w - nw
                    else:
                        y, x = (h - nh) // 2, (w - nw) // 2
                    img = img[y : y + nh, x : x + nw]

                # HYPER-SENSITIVE REAL-TIME WATCHER (Zero Seconds Delay!)
                h, w = img.shape[:2]
                chat_crop = img[int(h * 0.7) : h, :]
                gray = cv2.cvtColor(chat_crop, cv2.COLOR_BGR2GRAY)

                trigger_ocr = False

                if last_chat_gray is not None:
                    diff = cv2.absdiff(gray, last_chat_gray)
                    _, diff_thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                    changed_pixels = cv2.countNonZero(diff_thresh)

                    # Trigger on ANY tiny visual change (e.g., 50 pixels) without slowing the video stream
                    if changed_pixels > 50 and not ocr_task_running:
                        trigger_ocr = True

                last_chat_gray = gray.copy()

                if trigger_ocr:
                    ocr_task_running = True
                    thresh = cv2.adaptiveThreshold(
                        gray,
                        255,
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        cv2.THRESH_BINARY,
                        11,
                        2,
                    )

                    async def _run_bg_ocr():
                        nonlocal last_chat_text, ocr_task_running
                        try:

                            def _do_quick_ocr():
                                import os

                                from core.ocr_engine import get_tesseract_path

                                tess_path = get_tesseract_path()
                                if tess_path and os.path.exists(tess_path):
                                    pytesseract.pytesseract.tesseract_cmd = tess_path
                                try:
                                    return pytesseract.image_to_string(
                                        thresh, lang="eng", timeout=5
                                    ).strip()
                                except Exception:
                                    return ""

                            new_text = await asyncio.to_thread(_do_quick_ocr)
                            clean_new = "".join(
                                c for c in new_text if c.isalnum()
                            ).lower()
                            clean_old = "".join(
                                c for c in last_chat_text if c.isalnum()
                            ).lower()

                            if len(clean_new) > 5 and clean_new != clean_old:
                                if (
                                    clean_old not in clean_new
                                    or len(clean_new) > len(clean_old) + 2
                                ):
                                    snippet = new_text[-60:].replace("\n", " ")
                                    msg = f"[SYSTEM AUTO-WATCHER] 🔔 Live streaming screen update! Snippet: '{snippet}'. Read screen and AUTO-REPLY instantly!"

                                    # CRITICAL FIX: We MUST push the trigger into the pending inputs queue,
                                    # otherwise Vespera never actually receives the text invisibly, only the UI does!
                                    from api.ui_server import (
                                        _lock,
                                        _pending_inputs,
                                        add_chat_message,
                                    )

                                    with _lock:
                                        _pending_inputs.append(msg)
                                    add_chat_message("user", msg)

                                    last_chat_text = new_text
                        finally:
                            ocr_task_running = False

                    # Run asynchronously so the video stream never stutters!
                    asyncio.create_task(_run_bg_ocr())

                # Resize to max 1080p
                h, w = img.shape[:2]
                max_dim = 1080
                if h > max_dim or w > max_dim:
                    scale = max_dim / max(h, w)
                    img = cv2.resize(img, (int(w * scale), int(h * scale)))

                success, buffer = cv2.imencode(
                    ".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                )
                if success:
                    async with send_lock:
                        await session.send_realtime_input(
                            video=types.Blob(
                                data=buffer.tobytes(), mime_type="image/jpeg"
                            )
                        )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.warning("Screen stream failed to send: %s", e)

        # Stream at 2 FPS to prevent overwhelming the server leading to 1007 invalid argument errors
        await asyncio.sleep(0.5)


async def _session_rotation_manager(resume_state: dict, stop: asyncio.Event) -> None:
    """Waits 10 minutes then gracefully breaks connection when silent to naturally rotate models."""
    try:
        await asyncio.sleep(600)  # Wait exactly 10 minutes
        # Wait until Vespera finishes speaking
        while resume_state.get("is_speaking", False) and not stop.is_set():
            await asyncio.sleep(0.5)
        # Session rotater triggers cancellation
    except asyncio.CancelledError:
        pass


async def _run_one_connection(
    client: genai.Client,
    model_name: str,
    config: types.LiveConnectConfig,
    mic_stream: pyaudio.Stream,
    speaker_pipeline: SpeakerPipeline,
    resume_state: dict[str, Any],
    user_stop: asyncio.Event,
) -> None:
    stop = asyncio.Event()
    mime = f"audio/pcm;rate={INPUT_RATE}"
    send_lock = asyncio.Lock()

    async with client.aio.live.connect(model=model_name, config=config) as session:
        logger.info("Connected to Live session with model: %s", model_name)
        set_status("listening")
        send_task = asyncio.create_task(
            _send_mic_forever(session, mic_stream, mime, stop, send_lock, speaker_pipeline)
        )
        recv_task = asyncio.create_task(
            _recv_forever(
                session,
                speaker_pipeline,
                resume_state,
                stop,
                client,
                model_name,
                send_lock,
            )
        )
        alert_task = asyncio.create_task(_send_alerts_forever(session, stop, send_lock, speaker_pipeline))
        camera_task = asyncio.create_task(
            _send_camera_forever(session, stop, send_lock)
        )
        screen_task = asyncio.create_task(
            _send_screen_share_forever(session, stop, send_lock)
        )
        rotation_task = asyncio.create_task(
            _session_rotation_manager(resume_state, stop)
        )
        user_task = asyncio.create_task(user_stop.wait())

        try:
            done, _pending = await asyncio.wait(
                {
                    send_task,
                    recv_task,
                    alert_task,
                    camera_task,
                    screen_task,
                    rotation_task,
                    user_task,
                },
                return_when=asyncio.FIRST_COMPLETED,
            )

            if user_task in done or rotation_task in done:
                stop.set()
                send_task.cancel()
                recv_task.cancel()
                alert_task.cancel()
                camera_task.cancel()
                screen_task.cancel()
                rotation_task.cancel()
                await asyncio.gather(
                    send_task,
                    recv_task,
                    alert_task,
                    camera_task,
                    screen_task,
                    rotation_task,
                    return_exceptions=True,
                )
                return

            stop.set()
            if not send_task.done():
                send_task.cancel()
            if not recv_task.done():
                recv_task.cancel()
            if not alert_task.done():
                alert_task.cancel()
            if not camera_task.done():
                camera_task.cancel()
            if not screen_task.done():
                screen_task.cancel()
            if not rotation_task.done():
                rotation_task.cancel()
            await asyncio.gather(
                send_task,
                recv_task,
                alert_task,
                camera_task,
                screen_task,
                rotation_task,
                return_exceptions=True,
            )

            for t in done:
                if t is user_task:
                    continue
                if t.cancelled():
                    continue
                exc = t.exception()
                if exc:
                    raise exc
        finally:
            # Fully reset visual streaming states so they do not crash the next session if left hovering
            GLOBAL_STATE["screen_share_active"] = False
            GLOBAL_STATE["camera_share_active"] = False
            user_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await user_task


async def main() -> None:
    _load_dotenv()
    api_key = _get_api_key()
    client = genai.Client(api_key=api_key)

    resume_state: dict[str, Any] = {"handle": None, "is_speaking": False}

    # Retry loop for audio device initialization (fixes Errno -9999 when earbuds connect)
    pa = None
    mic_stream = None
    speaker_stream = None

    while True:
        try:
            if pa is not None:
                pa.terminate()
            pa = pyaudio.PyAudio()

            in_idx = None
            out_idx = None
            try:
                def_in = pa.get_default_input_device_info()
                in_name = def_in.get("name", "")

                if "Headset" in in_name or "Hands-Free" in in_name:
                    # OPTIMIZATION: Try to use Laptop Mic so earbuds can stay in high-quality Stereo
                    for i in range(pa.get_device_count()):
                        info = pa.get_device_info_by_index(i)
                        if (
                            info["hostApi"] == def_in["hostApi"]
                            and info["maxInputChannels"] > 0
                        ):
                            name = info.get("name", "")
                            if (
                                "Array" in name
                                or "Realtek" in name
                                or "Internal" in name
                            ):
                                in_idx = i
                                logger.info(
                                    f"Optimization: Using PC Mic '{name}' so earbuds stay in high-quality Stereo mode!"
                                )
                                break

                    # If no PC Mic is found, fallback to Hands-Free output fix
                    if in_idx is None:
                        for i in range(pa.get_device_count()):
                            info = pa.get_device_info_by_index(i)
                            if (
                                info["hostApi"] == def_in["hostApi"]
                                and info["maxOutputChannels"] == 1
                            ):
                                out_name = info.get("name", "")
                                if "Headset" in out_name or "Hands-Free" in out_name:
                                    out_idx = i
                                    logger.info(
                                        f"Fallback: Auto-routing to Hands-Free output: {out_name} (Index {i})"
                                    )
                                    break
            except Exception as e:
                logger.warning("Could not auto-route Bluetooth audio: %s", e)

            mic_kwargs = {
                "format": pyaudio.paInt16,
                "channels": 1,
                "rate": INPUT_RATE,
                "input": True,
                "frames_per_buffer": CHUNK,
            }
            if in_idx is not None:
                mic_kwargs["input_device_index"] = in_idx

            mic_stream = pa.open(**mic_kwargs)

            speaker_kwargs = {
                "format": pyaudio.paInt16,
                "channels": 1,
                "rate": OUTPUT_RATE,
                "output": True,
                "frames_per_buffer": SPEAKER_FRAMES_PER_BUFFER,
            }
            if out_idx is not None:
                speaker_kwargs["output_device_index"] = out_idx

            speaker_stream = pa.open(**speaker_kwargs)

            # Hook PyAudio instance to audio recovery watchdog
            try:
                from core.audio_recovery import audio_monitor
                def on_audio_device_changed():
                    logger.warning("Audio device swap requested from watch handler.")
                audio_monitor.start(pa, on_audio_device_changed)
            except Exception as audio_err:
                logger.warning(f"Could not initialize audio recovery monitor: {audio_err}")

            break
        except OSError as e:
            logger.warning("Audio device not ready (%s). Retrying in 2 seconds...", e)
            await asyncio.sleep(2.0)
    speaker_pipeline = SpeakerPipeline(speaker_stream)

    # Start UI widget server (HTTP for status API)
    start_ui_server()

    # Start global hotkey listener daemon (Ctrl+Alt+J)
    from core.keyboard_listener import global_hotkey_system
    global_hotkey_system.start()

    print("Connecting to Gemini Live (Gemini 3.1). Start talking to Vespera...")
    print("Ctrl+C to exit.\n")
    set_status("connecting")

    # Start Autonomous Agent background brain
    try:
        from core.vespera_society import VesperaSociety
        from api.ui_server import _lock, _pending_inputs

        async def _agent_inject(msg: str):
            """Inject autonomous agent messages into the voice session."""
            with _lock:
                _pending_inputs.append(msg)
            add_chat_message("user", f"[AGENT] {msg}")

        agent = VesperaSociety(
            api_key=api_key,
            inject_message_fn=_agent_inject,
        )
        agent.start()
        logger.info("Autonomous Agent brain started.")
    except Exception as e:
        logger.warning("Could not start autonomous agent: %s", e)

    # REALTIME ENGINE: Log startup status
    logger.info("Realtime Engine Status: %s", realtime.get_status())

    user_stop = asyncio.Event()
    backoff = 1.0

    try:
        while not user_stop.is_set():
            handle = resume_state.get("handle")
            config = _build_config(handle if isinstance(handle, str) else None)
            active_model = PRIMARY_LIVE_MODEL

            try:
                await _run_one_connection(
                    client,
                    active_model,
                    config,
                    mic_stream,
                    speaker_pipeline,
                    resume_state,
                    user_stop,
                )
                runtime.record_success()
                backoff = 1.0
            except asyncio.CancelledError:
                break
            except KeyboardInterrupt:
                user_stop.set()
                break
            except (
                genai_errors.APIError,
                OSError,
                ConnectionError,
                asyncio.exceptions.TimeoutError,
            ) as e:
                set_status("connecting")
                error_str = str(e).lower()
                is_rate_limit = (
                    "429" in error_str
                    or "quota" in error_str
                    or "exhausted" in error_str
                )
                if is_rate_limit:
                    action = runtime.record_failure(e)
                    cooldown = runtime.cooldown_remaining()
                    logger.warning(
                        "Rate limit reached (action=%s). Cooling down %.0fs...",
                        action,
                        max(3.0, cooldown),
                    )
                    await asyncio.sleep(max(3.0, cooldown))
                    backoff = 1.0
                else:
                    runtime.record_failure(e)
                    # ⚡ REALTIME ENGINE: Network-aware reconnection delay
                    net_mode = realtime.network.mode
                    if net_mode == NetworkMode.HIGH_PING:
                        adjusted_backoff = backoff * 1.5
                    elif net_mode == NetworkMode.FALLBACK:
                        adjusted_backoff = backoff * 2.0
                    else:
                        adjusted_backoff = backoff
                    logger.warning(
                        "Session lost (%s). Reconnecting in %.1fs... [Network: %s]",
                        e, adjusted_backoff, net_mode.name,
                    )
                    await asyncio.sleep(adjusted_backoff)
                    backoff = min(10.0, backoff * 1.5)
            except Exception as e:
                set_status("connecting")
                error_name = type(e).__name__
                if "ConnectionClosed" in error_name or "1007" in str(e):
                    # Clean handle for websockets closing abnormally due to payload errors
                    logger.warning(
                        "Session reset required (invalid frame/payload). Auto-reconnecting in 3s..."
                    )
                    await asyncio.sleep(3.0)
                    backoff = 1.0
                else:
                    logger.exception("Unexpected error; reconnecting fast...")
                    await asyncio.sleep(3.0)
    except KeyboardInterrupt:
        user_stop.set()
    finally:
        set_status("offline")
        speaker_pipeline.close()
        mic_stream.stop_stream()
        mic_stream.close()
        speaker_stream.stop_stream()
        speaker_stream.close()
        pa.terminate()
        print("\nStreams closed. Goodbye!")


def _run_async_main():
    """Runs the async voice assistant in a background thread."""
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.critical(f"FATAL ERROR in main loop: {e}", exc_info=True)
            print(f"\n[CRITICAL] Main loop crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    # Delayed startup check (runs if launched via Windows Startup Registry key)
    from core.startup_manager import handle_delayed_startup, sync_startup_with_registry
    handle_delayed_startup()
    sync_startup_with_registry()

    # Cinematic boot sequence
    print("\n" + "="*40)
    print("                VESPERA")
    print("="*40)
    time.sleep(0.3)
    print("Initializing Cognitive Systems...")
    time.sleep(0.3)
    print("Loading Neural Presence...")
    time.sleep(0.3)
    print("Realtime Voice Online...")
    time.sleep(0.3)
    print("Desktop Awareness Active...")
    time.sleep(0.3)
    print("Vespera is awake.\n")
    time.sleep(0.2)

    # Initialize process supervisor watchdog & resource guard daemons
    from core.vespera_kernel_supervisor import supervisor
    from core.vespera_guardian import resource_guard
    from core.signal_handler import shutdown_coordinator
    
    resource_guard.start()
    shutdown_coordinator.install()
    supervisor.start()

    # Validate memory database integrity
    from core.db_doctor import check_and_repair_db
    from core.vespera_memory import memory_system
    check_and_repair_db(Path(memory_system.path))

    # Initialize and start the modular Wake System (with permission check)
    from core.wake_system import wake_system
    wake_system.request_microphone_permission()
    wake_system.start()

    # Start the Gaming Monitor (DarkNova Mode auto-detect daemon)
    from core.gaming_monitor import gaming_monitor
    gaming_monitor.start()

    # Start the Threaded Metric Monitor (Legacy Vespera v3.0 Feature)
    from telemetry.system_monitor import sys_monitor
    from core.proactive_helper import proactive_helper

    sys_monitor.start()
    proactive_helper.start()

    # 1. Start the voice assistant in a background thread with SILENT SEAL
    from concurrent.futures import ThreadPoolExecutor
    import psutil
    
    def compute_reserve_monitor():
        """
        🚀 Compute Reserve Tier 1
        Aggressively monitors CPU to guarantee maximum FPS for gaming/streaming.
        """
        while True:
            try:
                load = psutil.cpu_percent(interval=1)
                if load > 85:
                    print(f"[COMPUTE RESERVE] Critical CPU load ({load}%). Throttling umbracore background tasks to guarantee 100% FPS.")
                    time.sleep(5) # Aggressively pause background loops
                else:
                    time.sleep(2)
            except Exception:
                time.sleep(5)
                
    def silent_seal_loop():
        # Dedicated ThreadPool for heavy IO/Sync tasks inside async loops
        global engine_thread_pool
        engine_thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="umbracore_Worker")
        
        # Start Compute Reserve Monitor
        threading.Thread(target=compute_reserve_monitor, daemon=True, name="ComputeReserve").start()
        
        # Launch Vespera sub-engines (Silent Butler, Chauffeur, Morning Briefing)
        try:
            from automation.file_organizer import TheSilentButler
            butler = TheSilentButler()
            butler.start()
        except Exception as e:
            print(f"[ERROR] Failed to start The Silent Butler: {e}")

        try:
            from automation.the_chauffeur import TheChauffeur
            driver = TheChauffeur()
            if driver.client:
                threading.Thread(target=driver.monitor_stream, daemon=True, name="TheChauffeur").start()
        except Exception as e:
            print(f"[ERROR] Failed to start The Chauffeur: {e}")

        try:
            from automation.morning_briefing import MorningBriefing
            def run_morning_briefing():
                briefing = MorningBriefing()
                text = briefing.generate_briefing()
                print(f"\n================ VESPERA MORNING BRIEFING ================\n{text}\n=========================================================\n", flush=True)
            threading.Thread(target=run_morning_briefing, daemon=True, name="MorningBriefing").start()
        except Exception as e:
            print(f"[ERROR] Failed to run Morning Briefing: {e}")

        while True:
            try:
                _run_async_main()
            except Exception as e:
                print(f"\\n[SILENT SEAL] umbracore crashed: {e}")
                print("[SILENT SEAL] Gracefully recalibrating and restarting in 2 seconds...", flush=True)
                time.sleep(2)
                
    assistant_thread = threading.Thread(
        target=silent_seal_loop, name="umbracore_Main", daemon=True
    )
    assistant_thread.start()

    # 2. Add System Hooks
    try:
        import keyboard

        def panic_mute():
            try:
                keyboard.send("volume mute")
                print("\n[PANIC MODE] System muted!", flush=True)
            except:
                pass

        keyboard.add_hotkey("win+d", panic_mute)
    except Exception as e:
        print(f"Could not hook win+d: {e}")

    # 3. Launch Electron Hardware GUI for perfect Windows transparency
    import time
    import subprocess
    import os
    import sys

    time.sleep(1)  # Give the UI server a moment to start

    # Determine if we should force headless mode
    ui_dir_exists = False
    if getattr(sys, "frozen", False):
        ui_dir = os.path.join(os.path.dirname(sys.executable), "ui")
    else:
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
    
    if os.path.exists(ui_dir):
        ui_dir_exists = True

    if "--no-ui" in sys.argv or not ui_dir_exists:
        if not ui_dir_exists and "--no-ui" not in sys.argv:
            print("\n[SYSTEM] UI directory not found. Automatically running in headless mode.")
        else:
            print("\n[SYSTEM] Running in headless mode (--no-ui). UI is managed externally.")
        try:
            # Block the main thread so daemon voice loops stay alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print(
            "\n[SYSTEM] Launching Holographic Electron UI (Zero White Box) with 24/7 respawn..."
        )

        try:
            while True:
                # shell=True resolves Windows 'npx' execution
                # CREATE_NO_WINDOW prevents command prompt window from flashing on Windows
                popen_kwargs = {"cwd": ui_dir, "shell": True}
                if sys.platform == "win32":
                    popen_kwargs["creationflags"] = 0x08000000 # subprocess.CREATE_NO_WINDOW
                
                electron_proc = subprocess.Popen("npx electron .", **popen_kwargs)

                # Block the main thread so daemon voice loops stay alive
                while electron_proc.poll() is None:
                    time.sleep(1)

                print(
                    "\n[WARNING] Electron UI closed. Respawning in 3 seconds to maintain 24/7 loop..."
                )
                time.sleep(3)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"[ERROR] Failed to launch Electron UI: {e}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    print("\nGoodbye!")
