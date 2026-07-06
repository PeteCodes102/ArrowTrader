from __future__ import annotations

import secrets
from typing import Callable

import customtkinter as ctk
import pygetwindow as gw

from infra.gui.theme.styles import COLORS, ENTRY_STYLE, FONTS


class _Tooltip:
    """Simple hover tooltip for any CTk widget."""

    def __init__(self, widget: ctk.CTkBaseClass, text: str) -> None:
        self._widget = widget
        self._text = text
        self._tip: ctk.CTkToplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _: object) -> None:
        x = self._widget.winfo_rootx() + self._widget.winfo_width() + 6
        y = self._widget.winfo_rooty()
        self._tip = ctk.CTkToplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        self._tip.configure(fg_color=COLORS["surface_alt"])
        ctk.CTkLabel(
            self._tip,
            text=self._text,
            font=FONTS["label"],
            text_color=COLORS["text"],
            fg_color=COLORS["surface_alt"],
            corner_radius=6,
            wraplength=300,
            justify="left",
            padx=10,
            pady=8,
        ).pack()

    def _hide(self, _: object) -> None:
        if self._tip:
            self._tip.destroy()
            self._tip = None


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
    Card containing window targeting and API credential/settings inputs.
    """

    def __init__(self, parent, default_api_url: str = "http://127.0.0.1:8000/api/v1", on_save: Callable[[], None] | None = None, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._default_api_url = default_api_url
        self._on_save = on_save
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

        secret_field = ctk.CTkFrame(self, fg_color="transparent")
        secret_field.grid(row=1, column=1, sticky="ew", padx=(8, 16), pady=(0, 16))
        secret_field.grid_columnconfigure(0, weight=1)

        self.secret_entry = ctk.CTkEntry(
            secret_field,
            placeholder_text="Enter or generate a secret",
            show="•",
            **ENTRY_STYLE,
        )
        self.secret_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            secret_field,
            text="Generate",
            command=self._generate_secret,
            width=90,
            height=38,
            corner_radius=8,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["button"],
        ).grid(row=0, column=1, sticky="e", padx=(0, 8))

        ctk.CTkButton(
            secret_field,
            text="Copy",
            command=self._copy_secret,
            width=60,
            height=38,
            corner_radius=8,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["button"],
        ).grid(row=0, column=2, sticky="e")

        # ── Auto-save row ──────────────────────────────────────────────────────
        save_row = ctk.CTkFrame(secret_field, fg_color="transparent")
        save_row.grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

        self._auto_save_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            save_row,
            text="Auto-save on generate",
            variable=self._auto_save_var,
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_muted"],
            border_color=COLORS["border"],
            checkmark_color=COLORS["text"],
            width=20,
            height=20,
        ).pack(side="left")

        info_label = ctk.CTkLabel(
            save_row,
            text="  ⓘ",
            font=FONTS["section"],
            text_color=COLORS["text_muted"],
            cursor="hand2",
        )
        info_label.pack(side="left")
        _Tooltip(
            info_label,
            "If a new secret is generated, it will need to be updated"
            " in your incoming TradingView API requests.",
        )

        # ── Session filter row ───────────────────────────────────────────────
        session_row = ctk.CTkFrame(secret_field, fg_color="transparent")
        session_row.grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))

        self._session_only_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            session_row,
            text="Only Trade During Session?",
            variable=self._session_only_var,
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_muted"],
            border_color=COLORS["border"],
            checkmark_color=COLORS["text"],
            width=20,
            height=20,
        ).pack(side="left")

        session_info = ctk.CTkLabel(
            session_row,
            text="  ⓘ",
            font=FONTS["section"],
            text_color=COLORS["text_muted"],
            cursor="hand2",
        )
        session_info.pack(side="left")
        _Tooltip(
            session_info,
            "Only accept Trades that occur during the times/dates entered. "
            "Time Format HH:MM, Days 123456 1= Sunday 6= Friday",
        )

        session_inputs = ctk.CTkFrame(secret_field, fg_color="transparent")
        session_inputs.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        session_inputs.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            session_inputs,
            text="Start Time",
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 4))

        ctk.CTkLabel(
            session_inputs,
            text="End Time",
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=8, pady=(0, 4))

        ctk.CTkLabel(
            session_inputs,
            text="Allowed Days",
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=2, sticky="w", padx=(8, 0), pady=(0, 4))

        self.session_start_entry = ctk.CTkEntry(
            session_inputs,
            placeholder_text="HH:MM",
            show="",
            **ENTRY_STYLE,
        )
        self.session_start_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        self.session_end_entry = ctk.CTkEntry(
            session_inputs,
            placeholder_text="HH:MM",
            show="",
            **ENTRY_STYLE,
        )
        self.session_end_entry.grid(row=1, column=1, sticky="ew", padx=8)

        self.allowed_days_entry = ctk.CTkEntry(
            session_inputs,
            placeholder_text="123456",
            show="",
            **ENTRY_STYLE,
        )
        self.allowed_days_entry.grid(row=1, column=2, sticky="ew", padx=(8, 0))

        self.set_session_filter(False, "09:30", "16:00", "123456")

        ctk.CTkLabel(
            self,
            text="API URL",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=(16, 16), pady=(0, 4))

        api_url_field = ctk.CTkFrame(self, fg_color="transparent")
        api_url_field.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(16, 16), pady=(0, 16))
        api_url_field.grid_columnconfigure(0, weight=1)

        self.api_url_entry = ctk.CTkEntry(
            api_url_field,
            placeholder_text="http://127.0.0.1:8000/api/v1",
            show="",
            **ENTRY_STYLE,
        )
        self.api_url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            api_url_field,
            text="Copy",
            command=self._copy_api_url,
            width=60,
            height=38,
            corner_radius=8,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["button"],
        ).grid(row=0, column=1, sticky="e")

        self.set_api_url(self._default_api_url)

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def window_name(self) -> str:
        return self.window_name_entry.get()

    @property
    def secret(self) -> str:
        return self.secret_entry.get()

    @property
    def api_url(self) -> str:
        return self.api_url_entry.get()

    @property
    def session_only(self) -> bool:
        return bool(self._session_only_var.get())

    @property
    def session_start_time(self) -> str:
        return self.session_start_entry.get().strip()

    @property
    def session_end_time(self) -> str:
        return self.session_end_entry.get().strip()

    @property
    def session_allowed_days(self) -> str:
        return self.allowed_days_entry.get().strip()

    def set_window_name(self, value: str) -> None:
        self.window_name_entry.delete(0, "end")
        self.window_name_entry.insert(0, value)

    def set_secret(self, value: str) -> None:
        self.secret_entry.delete(0, "end")
        self.secret_entry.insert(0, value)

    def _generate_secret(self) -> None:
        self.set_secret(secrets.token_urlsafe(32))
        if self._auto_save_var.get() and self._on_save is not None:
            self._on_save()

    def _copy_secret(self) -> None:
        value = self.secret_entry.get()
        if value:
            self.clipboard_clear()
            self.clipboard_append(value)

    def _copy_api_url(self) -> None:
        value = self.api_url_entry.get()
        if value:
            self.clipboard_clear()
            self.clipboard_append(value)

    def set_api_url(self, value: str) -> None:
        self.api_url_entry.delete(0, "end")
        self.api_url_entry.insert(0, value)

    def set_session_filter(
        self,
        enabled: bool,
        start_time: str,
        end_time: str,
        allowed_days: str,
    ) -> None:
        self._session_only_var.set(bool(enabled))
        self.session_start_entry.delete(0, "end")
        self.session_start_entry.insert(0, start_time)
        self.session_end_entry.delete(0, "end")
        self.session_end_entry.insert(0, end_time)
        self.allowed_days_entry.delete(0, "end")
        self.allowed_days_entry.insert(0, allowed_days)

    def open_window_picker(self) -> None:
        window_titles = self._current_window_titles()
        WindowTitlePickerDialog(self, window_titles, self.set_window_name)

    def _current_window_titles(self) -> list[str]:
        titles = [title.strip() for title in gw.getAllTitles() if title and title.strip()]
        return list(dict.fromkeys(titles))