from __future__ import annotations

import customtkinter as ctk

from infra.gui.theme.styles import COLORS, FONTS


class TraderPowerSection(ctk.CTkFrame):
    def __init__(self, parent, command=None, initial_state: bool = True, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._command = command
        self._switch_var = ctk.StringVar(value="on" if initial_state else "off")
        self._build()
        self._apply_state(initial_state)

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        copy_frame = ctk.CTkFrame(self, fg_color="transparent")
        copy_frame.grid(row=0, column=0, sticky="w", padx=16, pady=14)

        ctk.CTkLabel(
            copy_frame,
            text="TRADER POWER",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            copy_frame,
            text="Controls whether the API accepts inbound orders.",
            font=FONTS["label"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.grid(row=0, column=1, sticky="e", padx=16, pady=14)

        self.status_label = ctk.CTkLabel(
            control_frame,
            text="",
            font=FONTS["section"],
            width=72,
            corner_radius=8,
            padx=10,
            pady=6,
        )
        self.status_label.pack(side="left", padx=(0, 12))

        self.switch = ctk.CTkSwitch(
            control_frame,
            text="",
            variable=self._switch_var,
            onvalue="on",
            offvalue="off",
            command=self._handle_toggle,
            progress_color=COLORS["buy"],
            button_color=COLORS["text"],
            button_hover_color=COLORS["text_dim"],
            fg_color=COLORS["border"],
            width=54,
        )
        self.switch.pack(side="left")

    def _handle_toggle(self) -> None:
        enabled = self.enabled
        self._apply_state(enabled)
        if self._command is not None:
            self._command(enabled)

    def _apply_state(self, enabled: bool) -> None:
        if enabled:
            self.status_label.configure(
                text="ON",
                fg_color=COLORS["buy_muted"],
                text_color=COLORS["buy"],
            )
            self.switch.select()
            return

        self.status_label.configure(
            text="OFF",
            fg_color=COLORS["sell_muted"],
            text_color=COLORS["sell"],
        )
        self.switch.deselect()

    @property
    def enabled(self) -> bool:
        return self._switch_var.get() == "on"

    def set_enabled(self, enabled: bool) -> None:
        self._apply_state(enabled)
