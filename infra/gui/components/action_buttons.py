from __future__ import annotations

import customtkinter as ctk
from typing import Callable
from infra.gui.theme.styles import COLORS, ACTION_BUTTONS

_ACTIONS: list[str] = ["buy", "sell", "exit", "reverse"]

# Horizontal padding per column: (left, right)
_PADX: list[tuple[int, int]] = [(0, 5), (5, 5), (5, 5), (5, 0)]


class ActionButtonSection(ctk.CTkFrame):
    """
    Transparent row of four action buttons:
    [ BUY ] [ SELL ] [ EXIT ] [ REVERSE ]

    Pass a commands dict to wire up callbacks at construction time, or call
    set_command(action, callback) afterwards.

    Example
    ───────
        section = ActionButtonSection(parent, commands={
            "buy":     lambda: trader.execute("buy"),
            "sell":    lambda: trader.execute("sell"),
            "exit":    lambda: trader.execute("exit"),
            "reverse": lambda: trader.execute("reverse"),
        })
    """

    def __init__(
        self,
        parent,
        commands: dict[str, Callable] | None = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs,
        )
        self.buttons: dict[str, ctk.CTkButton] = {}
        self._build(commands or {})

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self, commands: dict[str, Callable]) -> None:
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for col, action in enumerate(_ACTIONS):
            px = _PADX[col]
            btn = ctk.CTkButton(
                self,
                text=action.upper(),
                command=commands.get(action),
                **ACTION_BUTTONS[action],
            )
            btn.grid(row=0, column=col, sticky="ew", padx=px, pady=0)
            self.buttons[action] = btn

    # ── Public API ────────────────────────────────────────────────────────────

    def set_command(self, action: str, command: Callable) -> None:
        """Bind or replace the callback for a single button after construction."""
        self.buttons[action].configure(command=command)
