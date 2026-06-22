# tests/test_event_bus.py
"""
Unit tests for the event logging bus.
"""

from __future__ import annotations
import unittest
from pathlib import Path
import sys

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.event_bus import EventBus

class TestEventBus(unittest.TestCase):
    def test_publish_and_subscribe(self):
        bus = EventBus()
        events = []

        def callback(event_data):
            events.append(event_data)

        bus.subscribe("test_event", callback)
        bus.publish("test_event", {"payload": 123})

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["payload"], 123)

if __name__ == "__main__":
    unittest.main()
