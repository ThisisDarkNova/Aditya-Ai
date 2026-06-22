# core/event_bus.py
"""
Thread-safe event bus for logging, telemetry, and background communications.
"""

import logging
import threading
from typing import Callable, Dict, List, Any

logger = logging.getLogger("vespera-eventbus")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[🚌 EventBus] %(asctime)s - %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Any], None]]] = {}
        self._lock = threading.Lock()

    def subscribe(self, topic: str, listener: Callable[[Any], None]):
        with self._lock:
            if topic not in self._listeners:
                self._listeners[topic] = []
            self._listeners[topic].append(listener)

    def publish(self, topic: str, data: Any):
        logger.info(f"Event: {topic} | Data: {data}")
        with self._lock:
            listeners = list(self._listeners.get(topic, []))
        
        for listener in listeners:
            try:
                listener(data)
            except Exception as e:
                logger.error(f"Error calling listener on topic {topic}: {e}")

# Global EventBus instance
event_bus = EventBus()
