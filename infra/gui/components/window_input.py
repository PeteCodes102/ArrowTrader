from __future__ import annotations

from typing import Callable

import customtkinter as ctk
import pygetwindow as gw

from infra.gui.theme.styles import COLORS, ENTRY_STYLE, FONTS


class WindowTitlePickerDialog(ctk.CTkToplevel):
    """Modal picker that lists live window titles and returns the selected one."""

    def __init__(
        self,
        parent,
        window_titles: list[str],
        on_select: Callable[[str], None],
    ) -> None:
        super().__init__(parent)
        self._window_titles = window_titles
        self._on_select = on_select
        self._search_var = ctk.StringVar(value="")

        self.title("Select Window")
        self.geometry("520x560")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.transient(parent)
        self.grab_set()

        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self,
            text="Select a live window title",
            font=FONTS["title"],
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 6))

        ctk.CTkLabel(
            self,
            text="Choose the current session window name if it changes by asset.",
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Filter window titles...",
            textvariable=self._search_var,
            **ENTRY_STYLE,
        )
        search_entry.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
        self._search_var.trace_add("write", self._refresh_list)

        self._list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        self._list_frame.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self._list_frame.grid_columnconfigure(0, weight=1)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 16))
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            footer,
            text="Close",
            command=self.destroy,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["button"],
            height=34,
            corner_radius=8,
        ).grid(row=0, column=1, sticky="e")

        self._refresh_list()

    def _refresh_list(self, *_: object) -> None:
        for child in self._list_frame.winfo_children():
            child.destroy()

        query = self._search_var.get().strip().lower()
        matches = [title for title in self._window_titles if query in title.lower()]

        if not matches:
            ctk.CTkLabel(
                self._list_frame,
                text="No matching window titles found.",
                text_color=COLORS["text_dim"],
                font=FONTS["label"],
            ).grid(row=0, column=0, sticky="ew", padx=16, pady=16)
            return

        for row, title in enumerate(matches):
            button = ctk.CTkButton(
                self._list_frame,
                text=title,
                command=lambda value=title: self._select(value),
                fg_color=COLORS["surface_alt"],
                hover_color=COLORS["accent_muted"],
                text_color=COLORS["text"],
                font=FONTS["label"],
                height=34,
                corner_radius=8,
                anchor="w",
            )
            button.grid(row=row, column=0, sticky="ew", padx=10, pady=6)

    def _select(self, window_title: str) -> None:
        self._on_select(window_title)
        self.destroy()


class WindowInputSection(ctk.CTkFrame):
    """
    Card containing the Window Name and Secret entry fields side-by-side.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self,
            text="WINDOW NAME",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(16, 8), pady=(16, 4))

        window_field = ctk.CTkFrame(self, fg_color="transparent")
        window_field.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=(0, 16))
        window_field.grid_columnconfigure(0, weight=1)

        self.window_name_entry = ctk.CTkEntry(
            window_field,
            placeholder_text="e.g. Tradovate - Dark Default or TradingView session title",
            show="",
            **ENTRY_STYLE,
        )
        self.window_name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            window_field,
            text="Windows",
            command=self.open_window_picker,
            width=90,
            height=38,
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_muted"],
            text_color="#0D1117",
            font=FONTS["button"],
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            self,
            text="SECRET",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(8, 16), pady=(16, 4))

        self.secret_entry = ctk.CTkEntry(
            self,
            placeholder_text="Enter secret key",
            show="•",
            **ENTRY_STYLE,
        )
        self.secret_entry.grid(row=1, column=1, sticky="ew", padx=(8, 16), pady=(0, 16))

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def window_name(self) -> str:
        return self.window_name_entry.get()

    @property
    def secret(self) -> str:
        return self.secret_entry.get()

    def set_window_name(self, value: str) -> None:
        self.window_name_entry.delete(0, "end")
        self.window_name_entry.insert(0, value)

    def set_secret(self, value: str) -> None:
        self.secret_entry.delete(0, "end")
        self.secret_entry.insert(0, value)

    def open_window_picker(self) -> None:
        window_titles = self._current_window_titles()
        WindowTitlePickerDialog(self, window_titles, self.set_window_name)

    def _current_window_titles(self) -> list[str]:
        titles = [title.strip() for title in gw.getAllTitles() if title and title.strip()]
        return list(dict.fromkeys(titles))