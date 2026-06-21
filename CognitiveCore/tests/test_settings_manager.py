import os
import json
import pytest
from modules.settings_manager import SettingsManager

def test_settings_get_set(tmp_path):
    config_file = tmp_path / "settings.json"
    manager = SettingsManager(config_file)
    
    # Assert defaults or empty
    assert manager.get("temperature") == 0.7 # standard default
    
    # Set custom value
    manager.set("temperature", 0.9)
    assert manager.get("temperature") == 0.9
    
    # Check writing to file
    with open(config_file, "r") as f:
        data = json.load(f)
    assert data["temperature"] == 0.9
    
    # Test setting bounds/validation
    manager.set("font_size", 16)
    assert manager.get("font_size") == 16
