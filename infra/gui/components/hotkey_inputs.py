import customtkinter as ctk
from infra.gui.theme.styles import COLORS, FONTS, ENTRY_STYLE

# (label_text, accent_color)
_ACTIONS: list[tuple[str, str]] = [
    ("BUY",     COLORS["buy"]),
    ("SELL",    COLORS["sell"]),
    ("EXIT",    COLORS["exit"]),
    ("REVERSE", COLORS["reverse"]),
]

# Horizontal padding per column: (left, right)
_PADX: list[tuple[int, int]] = [(16, 6), (6, 6), (6, 6), (6, 16)]


class HotkeyInputSection(ctk.CTkFrame):
    """
    Card containing four inline hotkey entry boxes:
    Buy | Sell | Exit | Reverse
    """

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self.entries: dict[str, ctk.CTkEntry] = {}
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Section header
        ctk.CTkLabel(
            self,
            text="Hot Keys:",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(10, 6))

        # Coloured column labels + entry boxes
        for col, (name, color) in enumerate(_ACTIONS):
            px = _PADX[col]

            ctk.CTkLabel(
                self,
                text=name,
                font=FONTS["label"],
                text_color=color,
                anchor="w",
            ).grid(row=1, column=col, sticky="w", padx=px, pady=(0, 3))

            entry = ctk.CTkEntry(
                self,
                placeholder_text="ctrl+shift+b or F3",
                **ENTRY_STYLE,
            )
            entry.grid(row=2, column=col, sticky="ew", padx=px, pady=(0, 10))
            self.entries[name.lower()] = entry

    # ── Public API ────────────────────────────────────────────────────────────

    def get_hotkeys(self) -> dict[str, str]:
        """Return current hotkey values keyed by action name."""
        return {key: entry.get() for key, entry in self.entries.items()}
    
    def set_hotkeys(self, hotkeys: dict[str, str]) -> None:
        """Set hotkey entry values from a dict keyed by action name."""
        for key, entry in self.entries.items():
            value = hotkeys.get(key, "")
            entry.delete(0, "end")
            entry.insert(0, value)