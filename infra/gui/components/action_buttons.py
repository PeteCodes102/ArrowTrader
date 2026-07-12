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
        on_command_set: Callable[[str, Callable | None], None] | None = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs,
        )
        self.buttons: dict[str, ctk.CTkButton] = {}
        self._commands: dict[str, Callable | None] = dict(commands or {})
        self._on_command_set = on_command_set
        self._build(self._commands)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self, commands: dict[str, Callable]) -> None:
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.grid(row=0, column=0, sticky="ew")
        row_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for col, action in enumerate(_ACTIONS):
            px = _PADX[col]
            btn = ctk.CTkButton(
                row_frame,
                text=action.capitalize(),
                command=commands.get(action),
                **ACTION_BUTTONS[action],
            )
            btn.grid(row=0, column=col, sticky="ew", padx=px, pady=0)
            self.buttons[action] = btn

    # ── Public API ────────────────────────────────────────────────────────────

    def set_command(self, action: str, command: Callable) -> None:
        """Bind or replace the callback for a single button after construction."""
        self._commands[action] = command
        self.buttons[action].configure(command=command)
        if self._on_command_set is not None:
            self._on_command_set(action, command)

    def get_commands(self) -> dict[str, Callable | None]:
        """Return current action callback mapping."""
        return dict(self._commands)
