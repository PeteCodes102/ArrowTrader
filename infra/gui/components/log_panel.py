from __future__ import annotations

import customtkinter as ctk
from datetime import datetime

from infra.gui.theme.styles import COLORS, FONTS

_SEARCH_TAG = "search_highlight"
_TIMESTAMP_TAG = "ts"
_ACTION_TAG_PREFIX = "action_"

# (action_key, accent_color)
_ACTION_COLORS: list[tuple[str, str]] = [
    ("buy",     COLORS["buy"]),
    ("sell",    COLORS["sell"]),
    ("exit",    COLORS["exit"]),
    ("reverse", COLORS["reverse"]),
]


class LogPanel(ctk.CTkFrame):
    """
    Scrollable, searchable activity log panel.

    Programmatic API
    ────────────────
    log(message, action=None)
        Append a timestamped line.  Pass action="buy"/"sell"/"exit"/"reverse"
        to colour-code the action label.

    append(text)
        Append raw text without a timestamp.

    set_text(text)
        Replace all content with the given text.

    clear()
        Remove all content.

    Example
    ───────
        panel.log("filled 10 contracts", action="buy")
        panel.log("position closed",     action="exit")
        panel.clear()
    """

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._search_query = ""
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_textbox()

    def _build_toolbar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        bar.grid_columnconfigure(1, weight=1)

        # Section title
        ctk.CTkLabel(
            bar,
            text="ACTIVITY LOG",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
        ).grid(row=0, column=0, sticky="w")

        # Match count (right of search)
        self._match_label = ctk.CTkLabel(
            bar,
            text="",
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
            width=80,
            anchor="e",
        )
        self._match_label.grid(row=0, column=2, sticky="e", padx=(4, 6))

        # Search entry
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)
        ctk.CTkEntry(
            bar,
            placeholder_text="Search log…",
            textvariable=self._search_var,
            height=28,
            width=180,
            corner_radius=6,
            border_width=1,
            border_color=COLORS["border"],
            fg_color=COLORS["surface_alt"],
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_dim"],
            font=FONTS["mono"],
        ).grid(row=0, column=3, sticky="e", padx=(0, 6))

        # Clear button
        ctk.CTkButton(
            bar,
            text="Clear",
            width=54,
            height=28,
            corner_radius=6,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_dim"],
            font=FONTS["section"],
            command=self.clear,
        ).grid(row=0, column=4, sticky="e")

    def _build_textbox(self) -> None:
        self._textbox = ctk.CTkTextbox(
            self,
            fg_color=COLORS["surface_alt"],
            text_color=COLORS["text"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border_subtle"],
            font=FONTS["mono"],
            state="disabled",
            wrap="word",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["text_dim"],
            activate_scrollbars=True,
        )
        self._textbox.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 14))

        # Register tags on the underlying tk.Text widget
        tb = self._textbox._textbox
        tb.tag_configure(
            _SEARCH_TAG,
            background=COLORS["exit"],
            foreground="#0D1117",
        )
        tb.tag_configure(_TIMESTAMP_TAG, foreground=COLORS["text_muted"])
        for action, color in _ACTION_COLORS:
            tb.tag_configure(f"{_ACTION_TAG_PREFIX}{action}", foreground=color)

    # ── Public API ────────────────────────────────────────────────────────────

    def log(self, message: str, action: str | None = None) -> None:
        """
        Append a timestamped log line.

        Parameters
        ----------
        message : str
            The message text to display.
        action : str, optional
            One of "buy", "sell", "exit", "reverse".  When provided the action
            label is rendered in its accent colour before the message.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._tagged_insert(f"[{timestamp}]  ", _TIMESTAMP_TAG)

        if action:
            tag = f"{_ACTION_TAG_PREFIX}{action.lower()}"
            self._tagged_insert(f"{action.upper():<8}", tag)

        self._tagged_insert(f"{message}\n")
        self._textbox.see("end")
        self._reapply_search()

    def append(self, text: str) -> None:
        """Append raw text to the log (no timestamp added)."""
        self._write(text)
        self._reapply_search()

    def set_text(self, text: str) -> None:
        """Replace all log content with the given text."""
        self._textbox.configure(state="normal")
        self._textbox._textbox.delete("1.0", "end")
        self._textbox._textbox.insert("1.0", text)
        self._textbox.configure(state="disabled")
        self._reapply_search()

    def clear(self) -> None:
        """Remove all log content and reset the match counter."""
        self._textbox.configure(state="normal")
        self._textbox._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")
        self._match_label.configure(text="")

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _write(self, text: str) -> None:
        """Insert plain text and scroll to the end."""
        self._textbox.configure(state="normal")
        self._textbox._textbox.insert("end", text)
        self._textbox.configure(state="disabled")
        self._textbox.see("end")

    def _tagged_insert(self, text: str, *tags: str) -> None:
        """Insert text with optional tk tag names (bypasses CTk state guard)."""
        self._textbox.configure(state="normal")
        if tags:
            self._textbox._textbox.insert("end", text, tags)
        else:
            self._textbox._textbox.insert("end", text)
        self._textbox.configure(state="disabled")

    def _on_search_change(self, *_) -> None:
        self._search_query = self._search_var.get()
        self._reapply_search()

    def _reapply_search(self) -> None:
        """Remove existing highlights then re-apply for the current query."""
        tb = self._textbox._textbox
        tb.tag_remove(_SEARCH_TAG, "1.0", "end")

        query = self._search_query.strip()
        if not query:
            self._match_label.configure(text="")
            return

        count = 0
        start = "1.0"
        while True:
            pos = tb.search(query, start, stopindex="end", nocase=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(query)}c"
            tb.tag_add(_SEARCH_TAG, pos, end_pos)
            start = end_pos
            count += 1

        if count:
            label = f"{count} match{'es' if count != 1 else ''}"
        else:
            label = "no match"
        self._match_label.configure(text=label)






