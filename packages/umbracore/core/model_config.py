# core/model_config.py
"""
🧠 Intelligent Model Selection Engine — Derived from Live Test Results

Dynamically selects the best WORKING Gemini/Gemma model for each task type.
All failed/quota-exhausted models are excluded automatically.

Model rankings are based on actual test data from gemini_model_test_results.json.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ModelProfile:
    """A single tested model with its performance characteristics."""
    name: str
    response_time_sec: float
    category: str  # "gemini" or "gemma"

    @property
    def short_name(self) -> str:
        return self.name.replace("models/", "")


# ═══════════════════════════════════════════════════════════════
# WORKING MODELS — ordered by response time (fastest first)
# Source: gemini_model_test_results.json (only WORKING ✅)
# ═══════════════════════════════════════════════════════════════

WORKING_MODELS: tuple[ModelProfile, ...] = (
    ModelProfile("models/gemini-2.5-flash-lite",          0.83,   "gemini"),
    ModelProfile("models/gemma-3n-e4b-it",                1.16,   "gemma"),
    ModelProfile("models/gemma-3-27b-it",                 1.19,   "gemma"),
    ModelProfile("models/gemma-3-1b-it",                  1.20,   "gemma"),
    ModelProfile("models/gemma-3n-e2b-it",                1.24,   "gemma"),
    ModelProfile("models/gemma-3-4b-it",                  1.29,   "gemma"),
    ModelProfile("models/gemma-4-26b-a4b-it",             1.95,   "gemma"),
    ModelProfile("models/gemini-robotics-er-1.6-preview",  2.88,  "gemini"),
    ModelProfile("models/gemini-robotics-er-1.5-preview",  3.02,  "gemini"),
    ModelProfile("models/gemma-4-31b-it",                 4.33,   "gemma"),
    ModelProfile("models/gemini-2.5-flash",               8.80,   "gemini"),
    ModelProfile("models/gemma-3-12b-it",                 14.64,  "gemma"),
    ModelProfile("models/gemini-3-flash-preview",         19.30,  "gemini"),
    ModelProfile("models/gemini-flash-lite-latest",       19.02,  "gemini"),
    ModelProfile("models/gemini-flash-latest",            29.64,  "gemini"),
    ModelProfile("models/gemini-3.1-flash-lite-preview",  152.55, "gemini"),
)

# Quick lookup set
WORKING_MODEL_NAMES: set[str] = {m.short_name for m in WORKING_MODELS}


# ═══════════════════════════════════════════════════════════════
# TASK-BASED MODEL SELECTION
# ═══════════════════════════════════════════════════════════════

# 🧠 SMART — Best for heavy reasoning, coding, complex analysis
SMART_MODELS: tuple[str, ...] = (
    "gemma-4-31b-it",          # 31B params, 4.33s — most capable
    "gemma-4-26b-a4b-it",     # 26B MoE, 1.95s — fast + smart
    "gemma-3-27b-it",         # 27B params, 1.19s — excellent balance
    "gemini-2.5-flash",       # Gemini native, 8.80s — reliable
)

# ⚡ FAST — Best for quick responses, simple queries
FAST_MODELS: tuple[str, ...] = (
    "gemini-2.5-flash-lite",   # 0.83s — absolute fastest
    "gemma-3n-e4b-it",         # 1.16s — ultra-light
    "gemma-3-1b-it",           # 1.20s — tiny model
    "gemma-3n-e2b-it",         # 1.24s — nano-class
)

# 💰 CHEAP — Best for background tasks, monitoring, low-priority ops
CHEAP_MODELS: tuple[str, ...] = (
    "gemma-3-1b-it",           # 1B params — smallest footprint
    "gemma-3n-e2b-it",         # Nano 2B — minimal cost
    "gemma-3n-e4b-it",         # Nano 4B — still very cheap
    "gemini-2.5-flash-lite",   # Gemini lite — fast + cheap
)

# ✍️ CONTENT — Best for writing code, emails, essays
CONTENT_MODELS: tuple[str, ...] = (
    "gemini-2.5-flash",        # Best Gemini for generation
    "gemma-4-31b-it",          # Largest Gemma model
    "gemini-2.5-flash-lite",   # Fast fallback
    "gemma-3-4b-it",           # Light fallback
)

# 🤖 AGENT — Best for autonomous background brain
AGENT_MODELS: tuple[str, ...] = (
    "gemini-2.5-flash-lite",   # Ultra-fast for frequent polling
    "gemini-2.5-flash",        # Reliable fallback
    "gemma-3-4b-it",           # Cheap backup
)


# ═══════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════

# Primary models for each task type (first in each list)
SMART_MODEL: str = SMART_MODELS[0]
FAST_MODEL: str = FAST_MODELS[0]
CHEAP_MODEL: str = CHEAP_MODELS[0]
CONTENT_MODEL: str = CONTENT_MODELS[0]
AGENT_MODEL: str = AGENT_MODELS[0]
AGENT_MODEL_FALLBACK: str = AGENT_MODELS[1]


_TASK_MAP: dict[str, tuple[str, ...]] = {
    "smart":    SMART_MODELS,
    "reasoning": SMART_MODELS,
    "coding":   SMART_MODELS,
    "fast":     FAST_MODELS,
    "quick":    FAST_MODELS,
    "cheap":    CHEAP_MODELS,
    "background": CHEAP_MODELS,
    "monitor":  CHEAP_MODELS,
    "content":  CONTENT_MODELS,
    "writing":  CONTENT_MODELS,
    "agent":    AGENT_MODELS,
}


def get_model_for_task(task_type: str) -> str:
    """
    Get the best working model for a given task type.

    Args:
        task_type: One of 'smart', 'fast', 'cheap', 'content', 'agent',
                   'reasoning', 'coding', 'quick', 'background', 'monitor', 'writing'

    Returns:
        Model name string (without 'models/' prefix), ready to use with Gemini API.
    """
    candidates = _TASK_MAP.get(task_type.lower().strip(), FAST_MODELS)
    return candidates[0]


def get_fallback_chain(task_type: str) -> tuple[str, ...]:
    """
    Get the full fallback chain for a task type.
    Try models in order; if one fails, move to the next.
    """
    return _TASK_MAP.get(task_type.lower().strip(), FAST_MODELS)


def is_model_working(model_name: str) -> bool:
    """Check if a model is in the working set."""
    clean = model_name.replace("models/", "")
    return clean in WORKING_MODEL_NAMES


def get_model_profile(model_name: str) -> Optional[ModelProfile]:
    """Get full profile for a model, or None if not found/working."""
    clean = model_name.replace("models/", "")
    for m in WORKING_MODELS:
        if m.short_name == clean:
            return m
    return None
