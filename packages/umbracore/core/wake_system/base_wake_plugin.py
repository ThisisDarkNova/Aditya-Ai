# core/wake_system/base_wake_plugin.py
"""
Base Wake Plugin interface. All wake detection methods (claps, hotkeys, wake words)
must inherit from this base class to ensure modularity and extensibility.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable

class BaseWakePlugin(ABC):
    """
    Abstract base class for all Vespera Wake plugins.
    """
    def __init__(self, name: str, on_wake_callback: Callable[[], None]) -> None:
        self.name = name
        self.on_wake_callback = on_wake_callback
        self.is_active = False

    @abstractmethod
    def start(self) -> None:
        """
        Start the wake plugin's listening/monitoring process.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the wake plugin's listening/monitoring process.
        """
        pass

    def process_audio(self, data: bytes) -> None:
        """
        Optional hook for processing real-time raw audio chunks from the mic.
        Override in plugins that require mic streams (claps, wake words).
        """
        pass
