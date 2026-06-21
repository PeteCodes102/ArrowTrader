# core/ports/controller.py
from typing import Protocol

from core.domain._types import Hotkey


class Controller(Protocol):
    def execute_trade(self, window_title: str, hotkey: Hotkey) -> dict: ...

