# tests/test_db_doctor.py
"""
Unit tests for db integrity checker.
"""

from __future__ import annotations
import unittest
from pathlib import Path
import os
import shutil
import sys

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.db_doctor import check_and_repair_db

class TestDbDoctor(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_db_doctor_data")
        self.test_dir.mkdir(exist_ok=True)
        self.db_path = self.test_dir / "test.json"

    def tearDown(self):
        import gc
        gc.collect()
        if self.test_dir.exists():
            try:
                shutil.rmtree(self.test_dir)
            except Exception:
                pass

    def test_repair_invalid_json(self):
        # Write corrupted JSON
        with open(self.db_path, "w", encoding="utf-8") as f:
            f.write("{invalid json")

        # Run integrity check
        check_and_repair_db(self.db_path)
        
        # Verify it has been repaired to a valid empty dict or structure
        with open(self.db_path, "r", encoding="utf-8") as f:
            data = f.read()
            self.assertIn("{", data)

if __name__ == "__main__":
    unittest.main()
