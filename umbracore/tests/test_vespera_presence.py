# tests/test_vespera_presence.py
"""
Unit tests for the VESPERA persona.
"""

from __future__ import annotations
import unittest
from pathlib import Path
import sys

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from NeuralCore.vespera_presence import VESPERA_PERSONA

class TestVesperaPresence(unittest.TestCase):
    def test_persona_integrity(self):
        self.assertIn("VESPERA", VESPERA_PERSONA)
        self.assertIn("Jarvis", VESPERA_PERSONA)
        self.assertIn("Chief of Staff", VESPERA_PERSONA)

if __name__ == "__main__":
    unittest.main()
