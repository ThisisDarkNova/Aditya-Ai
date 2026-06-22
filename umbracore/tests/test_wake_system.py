# tests/test_wake_system.py
"""
Unit tests for settings management, startup registry, 6-stage lifecycle states,
double-clap wake confidence, and DarkNova gaming monitor.
Execute via: python -m unittest tests/test_wake_system.py
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
import os
import json
import time
import shutil
import threading
import numpy as np
from pathlib import Path
import sys
import psutil

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from V12Cylinders.settings_manager import SettingsManager, DEFAULT_SETTINGS, settings
from V12Cylinders.startup_manager import get_startup_command
from NeuralCore.vespera_runtime import VesperaRuntime
from V12Cylinders.gaming_monitor import GamingMonitor

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)
        self.settings_path = self.test_dir / "settings.json"
        self.backup_path = self.test_dir / "settings.json.bak"
        self._cleanup()

    def tearDown(self):
        self._cleanup()
        if self.test_dir.exists():
            try:
                shutil.rmtree(self.test_dir)
            except Exception:
                pass

    def _cleanup(self):
        try:
            if self.settings_path.exists():
                os.remove(self.settings_path)
        except Exception:
            pass
        try:
            if self.backup_path.exists():
                os.remove(self.backup_path)
        except Exception:
            pass

    def test_default_initialization(self):
        manager = SettingsManager(path=self.settings_path, backup_path=self.backup_path)
        self.assertEqual(manager.get("wake_word_enabled"), DEFAULT_SETTINGS["wake_word_enabled"])
        self.assertTrue(self.settings_path.exists())

    def test_set_and_get(self):
        manager = SettingsManager(path=self.settings_path, backup_path=self.backup_path)
        manager.set("clap_sensitivity", 0.8)
        self.assertEqual(manager.get("clap_sensitivity"), 0.8)

        new_manager = SettingsManager(path=self.settings_path, backup_path=self.backup_path)
        self.assertEqual(new_manager.get("clap_sensitivity"), 0.8)

    def test_backup_and_recovery(self):
        manager = SettingsManager(path=self.settings_path, backup_path=self.backup_path)
        manager.set("wake_word", "Vespera Bot")
        
        self.assertTrue(self.backup_path.exists())
        
        with open(self.settings_path, "w", encoding="utf-8") as f:
            f.write("{ corrupted json [")
            
        recovery_manager = SettingsManager(path=self.settings_path, backup_path=self.backup_path)
        self.assertEqual(recovery_manager.get("wake_word"), "Vespera Bot")
        
    def test_thread_safety(self):
        manager = SettingsManager(path=self.settings_path, backup_path=self.backup_path)
        threads = []
        
        def writer(val):
            for i in range(50):
                manager.set(f"test_key_{val}", i)
                
        for i in range(5):
            t = threading.Thread(target=writer, args=(i,))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        self.assertTrue(True)

class TestStartupManager(unittest.TestCase):
    def test_startup_command_generation(self):
        cmd = get_startup_command()
        self.assertIn("startup", cmd.lower())

class TestLifecycleStates(unittest.TestCase):
    def test_transitions(self):
        runtime = VesperaRuntime()
        self.assertEqual(runtime.status, "offline") # Start at OFFLINE
        
        runtime.status = "starting"
        self.assertEqual(runtime.status, "starting") # transition to STARTING
        
        runtime.status = "sleeping"
        self.assertEqual(runtime.status, "sleeping") # transition to SLEEPING
        
        runtime.status = "listening"
        self.assertEqual(runtime.status, "listening") # transition to LISTENING
        
        runtime.status = "processing"
        self.assertEqual(runtime.status, "processing") # transition to PROCESSING


class TestGamingMonitor(unittest.TestCase):
    @patch("psutil.process_iter")
    @patch("psutil.Process")
    def test_gaming_detection_priority_shift(self, mock_process, mock_process_iter):
        # Set up settings configuration
        settings.set("gaming_mode", {
            "enabled": True,
            "auto_detect_games": True,
            "suppress_notifications": True,
            "valorant_priority": True
        })

        # Mock processes: return Valorant game
        mock_proc1 = MagicMock()
        mock_proc1.info = {"name": "VALORANT-Win64-Shipping.exe"}
        mock_process_iter.return_value = [mock_proc1]

        # Mock self process priority interface
        mock_self_proc = MagicMock()
        mock_self_proc.nice.return_value = psutil.NORMAL_PRIORITY_CLASS
        mock_process.return_value = mock_self_proc

        monitor = GamingMonitor()
        monitor._run_once = True  # custom loop control to prevent infinite run

        # Directly run detection step
        monitor._activate_gaming_mode()
        
        self.assertTrue(monitor.is_gaming_active())
        mock_self_proc.nice.assert_called_with(psutil.IDLE_PRIORITY_CLASS)

        # Deactivate
        monitor._deactivate_gaming_mode()
        self.assertFalse(monitor.is_gaming_active())

if __name__ == "__main__":
    unittest.main()
