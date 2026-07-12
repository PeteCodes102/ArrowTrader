"""Launch Tradovate and log the user in using values from .env.

This script only opens Tradovate, focuses the window, and performs the
username/password login flow. It does not start the ArrowTrader app.
"""

from __future__ import annotations

import random
import time
from pathlib import Path

try:
    import pyautogui
    from decouple import config
except ImportError as exc:
    raise SystemExit(
        "Missing dependency 'pyautogui' or 'python-decouple'. Install with: pip install pyautogui python-decouple"
    ) from exc

try:
    import pygetwindow as gw
except ImportError:
    gw = None


TRADOVATE_EXECUTABLE = config("TRADOVATE_EXECUTABLE")
TRADOVATE_WINDOW_TITLE = config("TRADOVATE_WINDOW_TITLE", default="Tradovate")
USERNAME = config("TRADOVATE_USERNAME")
PASSWORD = config("TRADOVATE_PASSWORD")

APP_LAUNCH_WAIT_SECONDS = 5.0
POST_FOCUS_WAIT_SECONDS = 0.7
POST_LOGIN_WAIT_SECONDS = 1.0
CHAR_INTERVAL_SECONDS = 0.07
BASE_STEP_DELAY_SECONDS = 0.35
JITTER_MIN_SECONDS = 0.05
JITTER_MAX_SECONDS = 0.18
ENABLE_PYAUTOGUI_FAILSAFE = True


def _sleep_human(base_seconds: float) -> None:
    time.sleep(max(0.0, base_seconds + random.uniform(JITTER_MIN_SECONDS, JITTER_MAX_SECONDS)))


def _press_key(key: str, delay_after: float = BASE_STEP_DELAY_SECONDS) -> None:
    pyautogui.press(key)
    _sleep_human(delay_after)


def _type_human(text: str, delay_after: float = BASE_STEP_DELAY_SECONDS) -> None:
    pyautogui.write(text, interval=CHAR_INTERVAL_SECONDS)
    _sleep_human(delay_after)


def _open_tradovate() -> None:
    executable = Path(TRADOVATE_EXECUTABLE)
    if not executable.exists():
        raise FileNotFoundError(f"Tradovate executable not found: {TRADOVATE_EXECUTABLE}")

    executable.parent.mkdir(parents=True, exist_ok=True)
    import subprocess

    subprocess.Popen([str(executable)], cwd=str(executable.parent))
    time.sleep(APP_LAUNCH_WAIT_SECONDS)


def _focus_tradovate_window() -> bool:
    if hasattr(pyautogui, "getWindowsWithTitle"):
        windows = pyautogui.getWindowsWithTitle(TRADOVATE_WINDOW_TITLE)
    elif gw is not None:
        windows = gw.getWindowsWithTitle(TRADOVATE_WINDOW_TITLE)
    else:
        raise RuntimeError("Window focusing unavailable. Install with: pip install pygetwindow")

    if not windows:
        return False

    target = windows[0]
    if getattr(target, "isMinimized", False):
        target.restore()
        _sleep_human(0.4)

    target.activate()
    time.sleep(POST_FOCUS_WAIT_SECONDS)
    return True


def _login_sequence() -> None:
    _type_human(USERNAME)
    _press_key("tab")
    _type_human(PASSWORD)
    _press_key("tab")
    _press_key("enter")
    _press_key("tab")
    _press_key("tab")
    _press_key("tab")
    _press_key("enter")
    time.sleep(POST_LOGIN_WAIT_SECONDS)


def run() -> None:
    pyautogui.FAILSAFE = ENABLE_PYAUTOGUI_FAILSAFE
    pyautogui.PAUSE = 0.12

    print("Starting Tradovate automation in 3 seconds...")
    time.sleep(3)

    _open_tradovate()

    if not _focus_tradovate_window():
        raise RuntimeError(
            "Tradovate window not found. Check TRADOVATE_WINDOW_TITLE and launch timing."
        )

    _login_sequence()
    print("Tradovate login sequence completed.")


if __name__ == "__main__":
    run()