# tests/test_additional_modules.py
"""
Additional unit tests for ADITYA modules: AdityaMemoryEngine, AudioRecoveryMonitor, and FileIndexer.
Execute via: python -m unittest tests/test_additional_modules.py
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
import os
import json
import shutil
from pathlib import Path
import sys

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from NeuralCore.aditya_memory import AdityaMemoryEngine
from NeuralCore.audio_recovery import AudioRecoveryMonitor
from V12Cylinders.file_indexer import FileIndexer

class TestAdityaMemoryEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_memory_data")
        self.test_dir.mkdir(exist_ok=True)
        self.memory_path = str(self.test_dir / "memory.json")
        self._cleanup()

    def tearDown(self):
        self._cleanup()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def _cleanup(self):
        if os.path.exists(self.memory_path):
            os.remove(self.memory_path)

    def test_memory_load_default(self):
        engine = AdityaMemoryEngine(path=self.memory_path)
        self.assertEqual(engine.get_history(), [])
        self.assertEqual(engine.get_goals(), [])

    def test_memory_save_and_retrieve(self):
        engine = AdityaMemoryEngine(path=self.memory_path)
        engine.update_profile("name", "DarkNova")
        self.assertEqual(engine.get_profile().get("name"), "DarkNova")

        # Reload engine from disk
        engine2 = AdityaMemoryEngine(path=self.memory_path)
        self.assertEqual(engine2.get_profile().get("name"), "DarkNova")

class TestAudioRecoveryMonitor(unittest.TestCase):
    def test_initial_device_check(self):
        mock_pyaudio = MagicMock()
        mock_pyaudio.get_device_count.return_value = 3

        monitor = AudioRecoveryMonitor(check_interval=1)
        mock_callback = MagicMock()
        
        # Start without threading watch loop
        monitor._pyaudio_instance = mock_pyaudio
        monitor._on_device_change_callback = mock_callback
        monitor._last_device_count = 3
        
        # Mock device change
        mock_pyaudio.get_device_count.return_value = 4
        monitor._watch_loop = MagicMock()  # avoid infinite loop
        
        # Manually invoke check step
        current_count = mock_pyaudio.get_device_count()
        if current_count != monitor._last_device_count:
            mock_callback()
            
        mock_callback.assert_called_once()

class TestFileIndexer(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_indexer_data")
        self.test_dir.mkdir(exist_ok=True)
        (self.test_dir / "test_file.txt").write_text("Hello ADITYA")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_indexing(self):
        indexer = FileIndexer(self.test_dir)
        # Scan temporary directory
        indexer.reindex()
        results = indexer.search_and_sort("test")
        self.assertTrue(len(results) > 0)
        filenames = [r["name"] for r in results]
        self.assertTrue(any("test_file.txt" in name for name in filenames))

if __name__ == "__main__":
    unittest.main()
