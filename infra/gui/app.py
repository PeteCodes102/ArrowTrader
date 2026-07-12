import threading
import subprocess
import sys
from pathlib import Path
from typing import Callable

import customtkinter as ctk
from infra.gui.theme.styles import COLORS, FONTS, apply_theme, available_theme_names
from infra.gui.components import (
    PlatformProfileSection,
    WindowTargetSection,
    WindowInputSection,
    HotkeyInputSection,
    TraderPowerSection,
    ActionButtonSection,
    LogPanel,
)
from infra.gui.platform_profiles import PlatformProfileStore

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ArrowTraderApp(ctk.CTk):
    """
    Root application window.

    Layout
    ──────
    ┌──────────────────────────────────────────────┐
    │  ◈  ARROW TRADER                             │  ← header
    ├──────────────────────────────────────────────┤
    │  WINDOW NAME           SECRET                │  ← WindowInputSection
    │  [_______________]     [_______________]     │
    ├──────────────────────────────────────────────┤
    │  HOTKEYS                                     │  ← HotkeyInputSection
    │  BUY    SELL    EXIT    REVERSE              │
    │  [___]  [___]  [___]   [______]              │
    ├──────────────────────────────────────────────┤
    │  [ BUY ]  [ SELL ]  [ EXIT ]  [ REVERSE ]   │  ← ActionButtonSection
    ├──────────────────────────────────────────────┤
    │  ACTIVITY LOG           [search…]   [Clear]  │  ← LogPanel
    │  ┌──────────────────────────────────────┐   │
    │  │ [12:00:01]  BUY     filled 10 lots   │   │
    │  │ [12:00:05]  SELL    closed position  │   │
    │  └──────────────────────────────────────┘   │
    └──────────────────────────────────────────────┘
    """

    def __init__(self, default_api_url: str = "http://127.0.0.1:8000/api/v1"):
        super().__init__()
        self.platform_store = PlatformProfileStore()
        self._default_api_url = default_api_url
        self._active_theme_name = apply_theme("Default")
        self._theme_var = ctk.StringVar(value=self._active_theme_name)
        self._action_commands: dict[str, Callable | None] = {}
        self._setup()
        self._build()

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup(self) -> None:
        self.title("Arrow Trader")
        self.geometry("980x920")
        self.minsize(760, 700)
        self.configure(fg_color=COLORS["bg"])

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # log panel stretches

        # ── Header bar ────────────────────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 0))

        ctk.CTkLabel(
            header_frame,
            text="Arrow Trader:",
            font=FONTS["title"],
            text_color=COLORS["text"],
        ).pack(side="left")

        # ── Divider ───────────────────────────────────────────────────────────
        ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS["border"],
            corner_radius=0,
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(12, 0))

        # ── Top split (Controller + Settings) ─────────────────────────────────
        top_split = ctk.CTkFrame(self, fg_color="transparent")
        top_split.grid(row=2, column=0, sticky="ew", padx=20, pady=(12, 0))
        top_split.grid_columnconfigure((0, 1), weight=1)

        left_panel = ctk.CTkFrame(
            top_split,
            fg_color=COLORS["surface"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_panel.grid_columnconfigure(0, weight=1)

        right_panel = ctk.CTkFrame(
            top_split,
            fg_color=COLORS["surface"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left_panel,
            text="Window/Hotkeys:",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            right_panel,
            text="Settings:",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 6))

        # ── Controller panel (top-left) ───────────────────────────────────────
        self.platform_selector = PlatformProfileSection(
            left_panel,
            platform_names=self.platform_store.platform_names(),
            on_select=self.load_platform_profile,
            on_save_current=self.save_selected_platform_profile,
            on_save_new=self.save_platform_profile_as_new,
        )
        self.platform_selector.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.window_target = WindowTargetSection(left_panel)
        self.window_target.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.hotkey_inputs = HotkeyInputSection(left_panel)
        self.hotkey_inputs.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.action_buttons = ActionButtonSection(
            left_panel,
            commands=self._action_commands,
            on_command_set=self._remember_action_command,
        )
        self.action_buttons.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 8))

        ctk.CTkButton(
            left_panel,
            text="Test API",
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["button"],
            height=32,
            corner_radius=7,
            command=self._launch_test_api_cli,
        ).grid(row=5, column=0, sticky="ew", padx=8, pady=(0, 10))

        # ── Settings panel (top-right) ────────────────────────────────────────
        self.trader_power = TraderPowerSection(right_panel, command=self._on_trader_power_changed)
        self.trader_power.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.window_input = WindowInputSection(
            right_panel,
            default_api_url=self._default_api_url,
            on_save=self.save_selected_platform_profile,
        )
        self.window_input.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 10))

        theme_block = ctk.CTkFrame(
            right_panel,
            fg_color=COLORS["surface"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border_subtle"],
        )
        theme_block.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 10))
        theme_block.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            theme_block,
            text="Theme:",
            font=FONTS["section"],
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))

        self._theme_var.set(self._active_theme_name)
        for row, label in enumerate(available_theme_names(), start=1):
            ctk.CTkRadioButton(
                theme_block,
                text=label,
                value=label,
                variable=self._theme_var,
                command=self._on_theme_changed,
                font=FONTS["label"],
                text_color=COLORS["text"],
                border_color=COLORS["border"],
                fg_color=COLORS["accent"],
            ).grid(row=row, column=0, sticky="w", padx=12, pady=(0, 2))

        # ── Activity log (bottom full-width panel) ────────────────────────────
        self.log_panel = LogPanel(self)
        self.log_panel.grid(row=3, column=0, sticky="nsew", padx=20, pady=(8, 20))

        if self.platform_selector.selected_platform:
            self.load_platform_profile(self.platform_selector.selected_platform, announce=False)

    # ── Public helpers ────────────────────────────────────────────────────────

    @property
    def window_name(self) -> str:
        return self.window_target.window_name

    @property
    def secret(self) -> str:
        return self.window_input.secret

    @property
    def api_url(self) -> str:
        return self.window_input.api_url

    @property
    def session_only(self) -> bool:
        return self.window_input.session_only

    @property
    def session_start_time(self) -> str:
        return self.window_input.session_start_time

    @property
    def session_end_time(self) -> str:
        return self.window_input.session_end_time

    @property
    def session_allowed_days(self) -> str:
        return self.window_input.session_allowed_days

    @property
    def trader_enabled(self) -> bool:
        return self.trader_power.enabled

    @property
    def hotkeys(self) -> dict[str, str]:
        return self.hotkey_inputs.get_hotkeys()

    def log(self, message: str, action: str | None = None) -> None:
        if threading.current_thread() is threading.main_thread():
            self.log_panel.log(message, action=action)
        else:
            self.after(0, lambda: self.log_panel.log(message, action=action))

    def _on_trader_power_changed(self, enabled: bool) -> None:
        state = "ON" if enabled else "OFF"
        self.log(f"Trader power switched {state}.")

    def _on_theme_changed(self) -> None:
        selected = self._theme_var.get().strip()
        self._apply_theme(selected)

    def _launch_test_api_cli(self) -> None:
        target_url = self.api_url.strip()
        secret = self.secret.strip()
        if not target_url:
            self.log("Set API URL before launching Test API.")
            return

        project_root = Path(__file__).resolve().parents[2]
        script_path = project_root / "trade_relay_cli.py"
        if not script_path.exists():
            self.log(f"Test API script not found: {script_path}")
            return

        cmd = [sys.executable, str(script_path), "--url", target_url]
        if secret:
            cmd.extend(["--secret", secret])

        creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        try:
            subprocess.Popen(
                cmd,
                cwd=str(project_root),
                creationflags=creation_flags,
            )
            self.log("Opened Test API relay terminal.")
        except Exception as exc:
            self.log(f"Failed to launch Test API relay: {exc}")

    def _remember_action_command(self, action: str, command: Callable | None) -> None:
        self._action_commands[action] = command

    def _capture_ui_state(self) -> dict[str, object]:
        self._action_commands = self.action_buttons.get_commands()
        log_text = ""
        if hasattr(self, "log_panel") and hasattr(self.log_panel, "_textbox"):
            log_text = self.log_panel._textbox._textbox.get("1.0", "end-1c")

        return {
            "window_name": self.window_name,
            "secret": self.secret,
            "api_url": self.api_url,
            "session_only": self.session_only,
            "session_start_time": self.session_start_time,
            "session_end_time": self.session_end_time,
            "session_allowed_days": self.session_allowed_days,
            "hotkeys": self.hotkeys,
            "trader_enabled": self.trader_enabled,
            "selected_platform": self.platform_selector.selected_platform,
            "new_platform_name": self.platform_selector.new_platform_name,
            "log_text": log_text,
        }

    def _restore_ui_state(self, state: dict[str, object]) -> None:
        self.window_target.set_window_name(str(state.get("window_name", "")))
        self.window_input.set_secret(str(state.get("secret", "")))
        self.window_input.set_api_url(str(state.get("api_url", self._default_api_url)))
        self.window_input.set_session_filter(
            bool(state.get("session_only", False)),
            str(state.get("session_start_time", "09:30")),
            str(state.get("session_end_time", "16:00")),
            str(state.get("session_allowed_days", "123456")),
        )
        hotkeys = state.get("hotkeys", {})
        if isinstance(hotkeys, dict):
            self.hotkey_inputs.set_hotkeys(hotkeys)

        selected_platform = str(state.get("selected_platform", "")).strip()
        if selected_platform:
            self.platform_selector.set_selected_platform(selected_platform, notify=False)
        self.platform_selector.set_new_platform_name(str(state.get("new_platform_name", "")))

        self.trader_power.set_enabled(bool(state.get("trader_enabled", True)))

        log_text = str(state.get("log_text", ""))
        if log_text:
            self.log_panel.set_text(log_text)

    def _apply_theme(self, theme_name: str) -> None:
        selected_theme = apply_theme(theme_name)
        if selected_theme == self._active_theme_name:
            return

        state = self._capture_ui_state()
        self._active_theme_name = selected_theme
        self._theme_var.set(selected_theme)
        ctk.set_appearance_mode("light" if selected_theme == "Orange & White" else "dark")
        self.configure(fg_color=COLORS["bg"])

        for child in self.winfo_children():
            child.destroy()

        self._build()
        self._restore_ui_state(state)
        self.log(f"Theme changed: {selected_theme}")

    def load_platform_profile(self, platform_name: str, announce: bool = True) -> None:
        try:
            profile = self.platform_store.get_profile(platform_name)
        except KeyError:
            self.log(f"Unknown platform profile: {platform_name}")
            return

        self.platform_selector.set_selected_platform(platform_name, notify=False)
        self.window_target.set_window_name(str(profile.get("window_name", "")))
        self.window_input.set_secret(str(profile.get("secret", "")))
        self.window_input.set_api_url(str(profile.get("api_url", self._default_api_url)))
        session_filter = profile.get("session_filter", {})
        if not isinstance(session_filter, dict):
            session_filter = {}
        self.window_input.set_session_filter(
            bool(session_filter.get("enabled", False)),
            str(session_filter.get("start_time", "09:30")),
            str(session_filter.get("end_time", "16:00")),
            str(session_filter.get("allowed_days", "123456")),
        )
        self.hotkey_inputs.set_hotkeys(dict(profile.get("hotkeys", {})))

        if announce:
            self.log(f"Loaded platform profile: {platform_name}")

    def save_selected_platform_profile(self) -> None:
        platform_name = self.platform_selector.selected_platform
        if not platform_name:
            self.log("Select a platform before saving.")
            return

        self.platform_store.save_profile(
            platform_name,
            self.window_name,
            self.secret,
            self.api_url,
            self.session_only,
            self.session_start_time,
            self.session_end_time,
            self.session_allowed_days,
            self.hotkeys,
        )
        self.platform_selector.set_platforms(self.platform_store.platform_names(), selected=platform_name)
        self.log(f"Updated platform profile: {platform_name}")

    def save_platform_profile_as_new(self, platform_name: str) -> None:
        platform_name = platform_name.strip()
        if not platform_name:
            self.log("Enter a new platform name before saving.")
            return

        try:
            self.platform_store.add_profile(
                platform_name,
                self.window_name,
                self.secret,
                self.api_url,
                self.session_only,
                self.session_start_time,
                self.session_end_time,
                self.session_allowed_days,
                self.hotkeys,
            )
        except ValueError as exc:
            self.log(str(exc))
            return

        self.platform_selector.set_platforms(self.platform_store.platform_names(), selected=platform_name)
        self.platform_selector.set_new_platform_name("")
        self.log(f"Saved new platform profile: {platform_name}")

    def run(self) -> None:
        self.mainloop()

