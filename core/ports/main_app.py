# core/ports/main_app.py
from typing import Protocol


class MainApp(Protocol):
    def log(self, message: str, action: str | None = None) -> None: ...
    def run(self) -> None: ...

    @property
    def window_name(self) -> str: ...

    @property
    def secret(self) -> str: ...

    @property
    def trader_enabled(self) -> bool: ...

    @property
    def hotkeys(self) -> dict[str, str]: ...



