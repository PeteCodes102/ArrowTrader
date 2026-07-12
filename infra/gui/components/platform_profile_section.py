from __future__ import annotations

import customtkinter as ctk
from typing import Callable

from infra.gui.theme.styles import COLORS, FONTS, ENTRY_STYLE


class PlatformProfileSection(ctk.CTkFrame):
    """
    Card for selecting, loading, and saving platform presets.

    - Dropdown: choose an existing platform preset
    - Entry: type a new platform name
    - Button: save current values into the selected preset
    - Button: save current values as a brand new preset
    """

    def __init__(
        self,
        parent,
        platform_names: list[str],
        on_select: Callable[[str], None] | None = None,
        on_save_current: Callable[[], None] | None = None,
        on_save_new: Callable[[str], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._on_select = on_select
        self._on_save_current = on_save_current
        self._on_save_new = on_save_new
        self._suspend_callback = False
        self._platform_var = ctk.StringVar(value="")
        self._new_platform_entry: ctk.CTkEntry | None = None
        self._platform_menu: ctk.CTkOptionMenu | None = None
        self._build(platform_names)

    def _build(self, platform_names: list[str]) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            self,
            text="Platform:",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(10, 5))

        ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS["border_subtle"],
            corner_radius=0,
        ).grid(row=0, column=0, columnspan=4, sticky="ew", padx=14, pady=(0, 0))

        ctk.CTkLabel(
            self,
            text="SELECT",
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=(14, 8), pady=(0, 2))

        self._platform_menu = ctk.CTkOptionMenu(
            self,
            values=platform_names or [""],
            variable=self._platform_var,
            command=self._handle_select,
            fg_color=COLORS["surface_alt"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_muted"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["surface_alt"],
            dropdown_text_color=COLORS["text"],
            font=FONTS["label"],
            corner_radius=7,
        )
        self._platform_menu.grid(row=1, column=1, sticky="ew", padx=(8, 8), pady=(0, 2))

        ctk.CTkLabel(
            self,
            text="NEW NAME",
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=1, column=2, sticky="w", padx=(8, 8), pady=(0, 2))

        self._new_platform_entry = ctk.CTkEntry(
            self,
            placeholder_text="create a platform name",
            **ENTRY_STYLE,
        )
        self._new_platform_entry.grid(row=1, column=3, sticky="ew", padx=(8, 14), pady=(0, 2))

        save_button = ctk.CTkButton(
            self,
            text="Save Selected",
            command=self._handle_save_current,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["button"],
            height=32,
            corner_radius=7,
        )
        save_button.grid(row=2, column=1, sticky="ew", padx=(8, 8), pady=(0, 10))

        save_new_button = ctk.CTkButton(
            self,
            text="Save As New",
            command=self._handle_save_new,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_muted"],
            text_color=COLORS["text"],
            font=FONTS["button"],
            height=32,
            corner_radius=7,
        )
        save_new_button.grid(row=2, column=3, sticky="ew", padx=(8, 14), pady=(0, 10))

        if platform_names:
            self.set_selected_platform(platform_names[0], notify=False)

    def _handle_select(self, value: str) -> None:
        if self._suspend_callback:
            return
        if self._on_select is not None and value:
            self._on_select(value)

    def _handle_save_current(self) -> None:
        if self._on_save_current is not None:
            self._on_save_current()

    def _handle_save_new(self) -> None:
        if self._on_save_new is not None:
            self._on_save_new(self.new_platform_name)

    @property
    def selected_platform(self) -> str:
        return self._platform_var.get().strip()

    @property
    def new_platform_name(self) -> str:
        if self._new_platform_entry is None:
            return ""
        return self._new_platform_entry.get().strip()

    def set_platforms(self, platform_names: list[str], selected: str | None = None) -> None:
        if self._platform_menu is None:
            return

        values = platform_names or [""]
        self._platform_menu.configure(values=values)

        if selected and selected in values:
            self.set_selected_platform(selected, notify=False)
        elif self.selected_platform not in values:
            self.set_selected_platform(values[0], notify=False)

    def set_selected_platform(self, platform_name: str, notify: bool = False) -> None:
        if self._platform_menu is None:
            return
        self._suspend_callback = not notify
        try:
            self._platform_var.set(platform_name)
            self._platform_menu.set(platform_name)
        finally:
            self._suspend_callback = False

    def set_new_platform_name(self, platform_name: str) -> None:
        if self._new_platform_entry is None:
            return
        self._new_platform_entry.delete(0, "end")
        self._new_platform_entry.insert(0, platform_name)
