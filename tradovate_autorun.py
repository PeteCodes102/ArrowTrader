"""Standalone Tradovate automation runner using pyautogui.

Edit the constants in the CONFIGURATION section before running this file.
Run with: python tradovate_autorun.py
"""

from __future__ import annotations

import random
import subprocess
import sys
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


# ==============================
# CONFIGURATION (EDIT THESE)
# ==============================

# Full path to Tradovate executable.
TRADOVATE_EXECUTABLE = config("TRADOVATE_EXECUTABLE")
# Part of the Tradovate window title used to focus the app.
TRADOVATE_WINDOW_TITLE = "Tradovate"

# Login credentials.
USERNAME = config("TRADOVATE_USERNAME")
PASSWORD = config("TRADOVATE_PASSWORD")

# If None, uses current interpreter (sys.executable).
PYTHON_EXECUTABLE: str | None = None

# Path to project entrypoint script.
PROJECT_ROOT = Path(__file__).resolve().parent
MAIN_SCRIPT_PATH = PROJECT_ROOT / "main.py"

# Exit method after main.py is launched.
# - "alt_shift_e": focuses Tradovate and sends Alt+Shift+E (Tradovate EXIT hotkey).
TRADOVATE_EXIT_METHOD = config("TRADOVATE_EXIT_METHOD", default="alt_shift_e")

# Output handling for spawned processes.
SUPPRESS_TRADOVATE_LOGS = True
SUPPRESS_MAIN_SCRIPT_LOGS = False


# ==============================
# TIMING CONFIGURATION
# ==============================

APP_LAUNCH_WAIT_SECONDS = 5
POST_FOCUS_WAIT_SECONDS = 0.7
POST_LOGIN_WAIT_SECONDS = 1.0
PRE_MAIN_LAUNCH_WAIT_SECONDS = 0.8
PRE_EXIT_WAIT_SECONDS = 1.2

# Typing and key timing.
CHAR_INTERVAL_SECONDS = 0.07
BASE_STEP_DELAY_SECONDS = 0.5
JITTER_MIN_SECONDS = 0.05
JITTER_MAX_SECONDS = 0.18

# Safety.
ENABLE_PYAUTOGUI_FAILSAFE = True


def _sleep_human(base_seconds: float) -> None:
    jitter = random.uniform(JITTER_MIN_SECONDS, JITTER_MAX_SECONDS)
    time.sleep(max(0.0, base_seconds + jitter))


def _press_key(key: str, delay_after: float = BASE_STEP_DELAY_SECONDS) -> None:
    pyautogui.press(key)
    _sleep_human(delay_after)


def _type_human(text: str, delay_after: float = BASE_STEP_DELAY_SECONDS) -> None:
    pyautogui.write(text, interval=CHAR_INTERVAL_SECONDS)
    _sleep_human(delay_after)


def _open_tradovate() -> None:
    executable = Path(TRADOVATE_EXECUTABLE)
    if not executable.exists():
        raise FileNotFoundError(
            f"Tradovate executable not found: {TRADOVATE_EXECUTABLE}"
        )

    popen_kwargs = {"cwd": str(executable.parent)}
    if SUPPRESS_TRADOVATE_LOGS:
        popen_kwargs.update(
            {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "stdin": subprocess.DEVNULL,
            }
        )

    subprocess.Popen([str(executable)], **popen_kwargs)
    time.sleep(APP_LAUNCH_WAIT_SECONDS)


def _focus_tradovate_window() -> bool:
    if hasattr(pyautogui, "getWindowsWithTitle"):
        windows = pyautogui.getWindowsWithTitle(TRADOVATE_WINDOW_TITLE)
    elif gw is not None:
        windows = gw.getWindowsWithTitle(TRADOVATE_WINDOW_TITLE)
    else:
        raise RuntimeError(
            "Window focusing unavailable. Install with: pip install pygetwindow"
        )

    if not windows:
        return False

    target = windows[0]
    if target.isMinimized:
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


def _launch_main_script() -> subprocess.Popen[bytes]:
    if not MAIN_SCRIPT_PATH.exists():
        raise FileNotFoundError(f"main.py not found at: {MAIN_SCRIPT_PATH}")

    python_cmd = PYTHON_EXECUTABLE or sys.executable
    if not python_cmd:
        raise RuntimeError("Could not determine Python executable.")

    popen_kwargs = {"cwd": str(PROJECT_ROOT)}
    if SUPPRESS_MAIN_SCRIPT_LOGS:
        popen_kwargs.update(
            {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "stdin": subprocess.DEVNULL,
            }
        )

    time.sleep(PRE_MAIN_LAUNCH_WAIT_SECONDS)
    return subprocess.Popen(
        [python_cmd, str(MAIN_SCRIPT_PATH)],
        **popen_kwargs,
    )



def _execute_tradovate_exit() -> None:
    time.sleep(PRE_EXIT_WAIT_SECONDS)
    if not _focus_tradovate_window():
        print("Warning: Tradovate window not found for exit command.")
        return

    if TRADOVATE_EXIT_METHOD == "alt_shift_e":
        pyautogui.hotkey("alt", "shift", "e")
        _sleep_human(BASE_STEP_DELAY_SECONDS)
        return

    raise ValueError(
        "Invalid TRADOVATE_EXIT_METHOD. Use 'alt_shift_e'."
    )


def run() -> None:
    pyautogui.FAILSAFE = ENABLE_PYAUTOGUI_FAILSAFE
    pyautogui.PAUSE = 0.12

    print("Starting Tradovate automation in 3 seconds...")
    time.sleep(3)

    _open_tradovate()  # 1

    if not _focus_tradovate_window():  # 2
        raise RuntimeError(
            "Tradovate window not found. Check TRADOVATE_WINDOW_TITLE and launch timing."
        )

    _login_sequence()  # 3-9
    _launch_main_script()  # 10 # 11

    print("Automation sequence completed.")


if __name__ == "__main__":
    run()