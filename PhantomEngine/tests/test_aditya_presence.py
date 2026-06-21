# tests/test_aditya_presence.py
"""
Unit tests for the ADITYA persona.
"""

from __future__ import annotations
import unittest
from pathlib import Path
import sys

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from NeuralCore.aditya_presence import ADITYA_PERSONA

class TestAdityaPresence(unittest.TestCase):
    def test_persona_integrity(self):
        self.assertIn("ADITYA", ADITYA_PERSONA)
        self.assertIn("Jarvis", ADITYA_PERSONA)
        self.assertIn("Chief of Staff", ADITYA_PERSONA)

if __name__ == "__main__":
    unittest.main()
