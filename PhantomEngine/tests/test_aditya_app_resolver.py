# tests/test_aditya_app_resolver.py
"""
Unit test for app resolver module.
"""

from __future__ import annotations
import unittest
from pathlib import Path
import sys

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from V12Cylinders.aditya_app_resolver import AppResolver

class TestAdityaAppResolver(unittest.TestCase):
    def test_fuzzy_app_match(self):
        resolver = AppResolver()
        # Mock index
        resolver.apps = [
            {"name": "Google Chrome", "path": "chrome.exe", "aliases": ["google chrome", "chrome"]},
            {"name": "Visual Studio Code", "path": "code.exe", "aliases": ["visual studio code", "code"]}
        ]
        
        match = resolver.resolve_app("chrome")
        self.assertEqual(match["name"], "Google Chrome")
        
        match_none = resolver.resolve_app("nonexistentappname")
        self.assertIsNone(match_none)

if __name__ == "__main__":
    unittest.main()
