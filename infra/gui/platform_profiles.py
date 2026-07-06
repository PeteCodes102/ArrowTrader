from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

_DEFAULT_PROFILES: dict[str, dict[str, object]] = {
    "Tradovate": {
        "window_name": "Tradovate",
        "secret": "",
        "api_url": "http://127.0.0.1:8000/api/v1",
        "session_filter": {
            "enabled": False,
            "start_time": "09:30",
            "end_time": "16:00",
            "allowed_days": "123456",
        },
        "hotkeys": {
            "buy": "ctrl+shift+b",
            "sell": "ctrl+shift+s",
            "exit": "ctrl+shift+e",
            "reverse": "ctrl+shift+r",
        },
    },
    "TradingView": {
        "window_name": "TradingView",
        "secret": "",
        "api_url": "http://127.0.0.1:8000/api/v1",
        "session_filter": {
            "enabled": False,
            "start_time": "09:30",
            "end_time": "16:00",
            "allowed_days": "123456",
        },
        "hotkeys": {
            "buy": "alt+b",
            "sell": "alt+s",
            "exit": "alt+e",
            "reverse": "alt+r",
        },
    },
}


class PlatformProfileStore:
    """Persist platform profile presets to a JSON file."""

    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = file_path or Path(__file__).with_name("platform_profiles.json")
        self._profiles = self._load_profiles()

    def _load_profiles(self) -> dict[str, dict[str, object]]:
        if not self.file_path.exists():
            profiles = deepcopy(_DEFAULT_PROFILES)
            self._write_profiles(profiles)
            return profiles

        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("Profile file must contain an object at the top level.")
            profiles = self._normalize(raw)
        except Exception:
            profiles = deepcopy(_DEFAULT_PROFILES)
            self._write_profiles(profiles)
            return profiles

        if not profiles:
            profiles = deepcopy(_DEFAULT_PROFILES)
            self._write_profiles(profiles)
        return profiles

    def _normalize(self, raw: dict[str, object]) -> dict[str, dict[str, object]]:
        profiles: dict[str, dict[str, object]] = {}
        for platform_name, payload in raw.items():
            if not isinstance(payload, dict):
                continue
            window_name = str(payload.get("window_name", ""))
            secret = str(payload.get("secret", ""))
            api_url = str(payload.get("api_url", "http://127.0.0.1:8000/api/v1"))
            session_filter = payload.get("session_filter", {})
            if not isinstance(session_filter, dict):
                session_filter = {}
            hotkeys = payload.get("hotkeys", {})
            if not isinstance(hotkeys, dict):
                hotkeys = {}
            profiles[str(platform_name)] = {
                "window_name": window_name,
                "secret": secret,
                "api_url": api_url,
                "session_filter": {
                    "enabled": bool(session_filter.get("enabled", False)),
                    "start_time": str(session_filter.get("start_time", "09:30")),
                    "end_time": str(session_filter.get("end_time", "16:00")),
                    "allowed_days": str(session_filter.get("allowed_days", "123456")),
                },
                "hotkeys": {
                    "buy": str(hotkeys.get("buy", "")),
                    "sell": str(hotkeys.get("sell", "")),
                    "exit": str(hotkeys.get("exit", "")),
                    "reverse": str(hotkeys.get("reverse", "")),
                },
            }
        return profiles

    def _write_profiles(self, profiles: dict[str, dict[str, object]]) -> None:
        self.file_path.write_text(json.dumps(profiles, indent=2), encoding="utf-8")

    def platform_names(self) -> list[str]:
        return list(self._profiles.keys())

    def get_profile(self, platform_name: str) -> dict[str, object]:
        if platform_name not in self._profiles:
            raise KeyError(f"Unknown platform profile: {platform_name!r}")
        return deepcopy(self._profiles[platform_name])

    def save_profile(
        self,
        platform_name: str,
        window_name: str,
        secret: str,
        api_url: str,
        session_filter_enabled: bool,
        session_filter_start_time: str,
        session_filter_end_time: str,
        session_filter_allowed_days: str,
        hotkeys: dict[str, str],
    ) -> None:
        self._profiles[platform_name] = {
            "window_name": window_name,
            "secret": secret,
            "api_url": api_url,
            "session_filter": {
                "enabled": bool(session_filter_enabled),
                "start_time": session_filter_start_time,
                "end_time": session_filter_end_time,
                "allowed_days": session_filter_allowed_days,
            },
            "hotkeys": {
                "buy": hotkeys.get("buy", ""),
                "sell": hotkeys.get("sell", ""),
                "exit": hotkeys.get("exit", ""),
                "reverse": hotkeys.get("reverse", ""),
            },
        }
        self._write_profiles(self._profiles)

    def add_profile(
        self,
        platform_name: str,
        window_name: str,
        secret: str,
        api_url: str,
        session_filter_enabled: bool,
        session_filter_start_time: str,
        session_filter_end_time: str,
        session_filter_allowed_days: str,
        hotkeys: dict[str, str],
    ) -> None:
        if platform_name in self._profiles:
            raise ValueError(f"Platform profile already exists: {platform_name!r}")
        self.save_profile(
            platform_name,
            window_name,
            secret,
            api_url,
            session_filter_enabled,
            session_filter_start_time,
            session_filter_end_time,
            session_filter_allowed_days,
            hotkeys,
        )
