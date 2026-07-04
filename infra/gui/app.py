import threading

import customtkinter as ctk
from infra.gui.theme.styles import COLORS, FONTS
from infra.gui.components import (
    PlatformProfileSection,
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
        self._setup()
        self._build()

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup(self) -> None:
        self.title("Arrow Trader")
        self.geometry("780x800")
        self.minsize(580, 580)
        self.configure(fg_color=COLORS["bg"])

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)  # log panel stretches

        # ── Header bar ────────────────────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 0))

        ctk.CTkLabel(
            header_frame,
            text="◈  ARROW TRADER",
            font=FONTS["title"],
            text_color=COLORS["text"],
        ).pack(side="left")

        # ── Divider ───────────────────────────────────────────────────────────
        ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS["border"],
            corner_radius=0,
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(14, 0))

        # ── Platform profile selector ─────────────────────────────────────────
        self.platform_selector = PlatformProfileSection(
            self,
            platform_names=self.platform_store.platform_names(),
            on_select=self.load_platform_profile,
            on_save_current=self.save_selected_platform_profile,
            on_save_new=self.save_platform_profile_as_new,
        )
        self.platform_selector.grid(row=2, column=0, sticky="ew", padx=24, pady=(14, 0))

        # ── Window / Secret inputs ─────────────────────────────────────────────
        self.window_input = WindowInputSection(self, default_api_url=self._default_api_url)
        self.window_input.grid(row=3, column=0, sticky="ew", padx=24, pady=(10, 0))

        # ── Hotkey inputs ──────────────────────────────────────────────────────
        self.hotkey_inputs = HotkeyInputSection(self)
        self.hotkey_inputs.grid(row=4, column=0, sticky="ew", padx=24, pady=(10, 0))

        # ── Trader API intake toggle ──────────────────────────────────────────
        self.trader_power = TraderPowerSection(self, command=self._on_trader_power_changed)
        self.trader_power.grid(row=5, column=0, sticky="ew", padx=24, pady=(10, 0))

        # ── Action buttons ─────────────────────────────────────────────────────
        self.action_buttons = ActionButtonSection(self)
        self.action_buttons.grid(row=6, column=0, sticky="ew", padx=24, pady=(14, 0))

        # ── Activity log ───────────────────────────────────────────────────────
        self.log_panel = LogPanel(self)
        self.log_panel.grid(row=7, column=0, sticky="nsew", padx=24, pady=(10, 24))

        if self.platform_selector.selected_platform:
            self.load_platform_profile(self.platform_selector.selected_platform, announce=False)

    # ── Public helpers ────────────────────────────────────────────────────────

    @property
    def window_name(self) -> str:
        return self.window_input.window_name

    @property
    def secret(self) -> str:
        return self.window_input.secret

    @property
    def api_url(self) -> str:
        return self.window_input.api_url

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

    def load_platform_profile(self, platform_name: str, announce: bool = True) -> None:
        try:
            profile = self.platform_store.get_profile(platform_name)
        except KeyError:
            self.log(f"Unknown platform profile: {platform_name}")
            return

        self.platform_selector.set_selected_platform(platform_name, notify=False)
        self.window_input.set_window_name(str(profile.get("window_name", "")))
        self.window_input.set_secret(str(profile.get("secret", "")))
        self.window_input.set_api_url(str(profile.get("api_url", self._default_api_url)))
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

