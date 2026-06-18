# modules/config_validator.py
"""
Validates settings payloads, ensuring values are typed correctly and nested structures
are completely secure before writing.
"""

from typing import Any, Dict
import logging

logger = logging.getLogger("aditya-safety")
logger.setLevel(logging.INFO)

# A schema mapping keys to expected python types or nested checks
SETTINGS_SCHEMA = {
    "startup_enabled": bool,
    "startup_delay_seconds": int,
    "start_minimized": bool,
    "launch_directly_voice": bool,
    "restore_last_session": bool,
    "wake_word_enabled": bool,
    "wake_word": str,
    "hotkey_enabled": bool,
    "hotkey_sequence": str,
    "mic_permission_granted": bool,
    "model_name": str,
    "temperature": (float, int),
    "api_key": str,
    "memory_enabled": bool,
    "memory_depth": int,
    "agent_swarm_enabled": bool,
    "max_agent_loops": int,
    "allow_macros": bool,
    "auto_backup": bool,
    "theme": str,
    "font_size": int,
    "reduce_motion": bool,
    "high_contrast": bool,
    "debug_mode": bool,
    "port": int,
    "clap_sensitivity": (float, int),
    "launch_on_startup": bool,
    "notifications_enabled": bool,
    "mic_muted": bool,
    "vision_active": bool
}

def validate_settings_dict(settings_data: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a dictionary of settings against the standard system schema.
    If a key is missing, type-mismatched, or corrupted, it falls back to the default.
    Returns a cleaned, fully-typed dictionary.
    """
    validated = {}
    for key, expected_type in SETTINGS_SCHEMA.items():
        if key not in settings_data:
            # Fall back to default
            validated[key] = defaults.get(key)
            continue
            
        value = settings_data[key]
        
        # Validate simple types
        if not isinstance(value, expected_type):
            logger.warning(f"Type mismatch for setting '{key}': expected {expected_type}, got {type(value)}. Resetting to default.")
            validated[key] = defaults.get(key)
        else:
            # Type is correct, check value constraints
            if key == "startup_delay_seconds":
                validated[key] = max(10, min(120, int(value)))
            elif key == "temperature":
                validated[key] = max(0.0, min(2.0, float(value)))
            elif key == "memory_depth":
                validated[key] = max(1, min(1000, int(value)))
            elif key == "max_agent_loops":
                validated[key] = max(1, min(100, int(value)))
            else:
                validated[key] = value

    # Specially validate nested structure "gaming_mode"
    if "gaming_mode" in settings_data and isinstance(settings_data["gaming_mode"], dict):
        validated_gaming = {}
        defaults_gaming = defaults.get("gaming_mode", {})
        gaming_payload = settings_data["gaming_mode"]
        
        for k in ["enabled", "auto_detect_games", "suppress_notifications", "valorant_priority"]:
            val = gaming_payload.get(k)
            if isinstance(val, bool):
                validated_gaming[k] = val
            else:
                validated_gaming[k] = defaults_gaming.get(k, True)
        validated["gaming_mode"] = validated_gaming
    else:
        validated["gaming_mode"] = defaults.get("gaming_mode")

    return validated
