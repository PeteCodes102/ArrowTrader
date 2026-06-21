from __future__ import annotations

import ctypes
import time

import pyautogui
import pygetwindow as gw

from core.domain._types import Hotkey

# Remove built-in pause delays for lowest-latency dispatch.
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0

_cached_window_title: str | None = None
_cached_window = None

_SW_SHOW = 5
_SW_RESTORE = 9
_SWP_NOMOVE = 0x0002
_SWP_NOSIZE = 0x0001
_HWND_TOPMOST = -1
_HWND_NOTOPMOST = -2


def _window_handle(window) -> int | None:
    return getattr(window, "_hWnd", None)


def _is_window_active(hwnd: int | None) -> bool:
    if not hwnd:
        return False
    try:
        user32 = ctypes.windll.user32
        return user32.GetForegroundWindow() == hwnd
    except Exception:
        return False


def _force_foreground(hwnd: int | None) -> None:
    if not hwnd:
        return

    user32 = ctypes.windll.user32
    foreground_hwnd = user32.GetForegroundWindow()
    current_thread_id = user32.GetCurrentThreadId()
    foreground_thread_id = user32.GetWindowThreadProcessId(foreground_hwnd, None)
    target_thread_id = user32.GetWindowThreadProcessId(hwnd, None)

    attach_foreground = foreground_thread_id and foreground_thread_id != current_thread_id
    attach_target = target_thread_id and target_thread_id != current_thread_id

    try:
        if attach_foreground:
            user32.AttachThreadInput(foreground_thread_id, current_thread_id, True)
        if attach_target:
            user32.AttachThreadInput(target_thread_id, current_thread_id, True)

        user32.ShowWindow(hwnd, _SW_RESTORE)
        user32.ShowWindow(hwnd, _SW_SHOW)
        user32.SetWindowPos(hwnd, _HWND_TOPMOST, 0, 0, 0, 0, _SWP_NOMOVE | _SWP_NOSIZE)
        user32.SetWindowPos(hwnd, _HWND_NOTOPMOST, 0, 0, 0, 0, _SWP_NOMOVE | _SWP_NOSIZE)
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        user32.SetFocus(hwnd)
        user32.SetActiveWindow(hwnd)
    finally:
        if attach_target:
            user32.AttachThreadInput(target_thread_id, current_thread_id, False)
        if attach_foreground:
            user32.AttachThreadInput(foreground_thread_id, current_thread_id, False)


def _click_title_bar(window) -> None:
    try:
        title_x = window.left + max(window.width // 2, 20)
        title_y = window.top + min(16, max(window.height // 8, 8))
        pyautogui.click(title_x, title_y)
    except Exception:
        pass


def _activate_window(window) -> bool:
    hwnd = _window_handle(window)

    for attempt in range(6):
        try:
            if getattr(window, "isMinimized", False):
                window.restore()
            window.activate()
        except Exception:
            pass

        try:
            _force_foreground(hwnd)
        except Exception:
            pass

        if _is_window_active(hwnd):
            return True

        if attempt >= 2:
            _click_title_bar(window)
            if _is_window_active(hwnd):
                return True

        time.sleep(0.05 + 0.03 * attempt)

    return _is_window_active(hwnd)


def _activate_cached_window(window_title: str) -> bool:
    global _cached_window_title, _cached_window

    if _cached_window is None or _cached_window_title != window_title:
        return False

    try:
        return _activate_window(_cached_window)
    except Exception:
        _cached_window = None
        _cached_window_title = None
        return False


def focus_window(window_title: str) -> bool:
    """Focus on a window by its title."""
    global _cached_window_title, _cached_window

    if _activate_cached_window(window_title):
        return True

    try:
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            return False

        # Prefer an exact-title match when available for deterministic focus.
        window = next((w for w in windows if getattr(w, "title", "") == window_title), windows[0])
        if not _activate_window(window):
            return False

        _cached_window = window
        _cached_window_title = window_title
        return True
    except (IndexError, Exception):
        return False


def press_hotkey(hotkey: Hotkey) -> None:
    """
    Execute a parsed hotkey sequence.

    Each step in the sequence is a list of keys pressed simultaneously.
    Steps are executed in order.

    Examples
    ────────
    [["f3"]]                              → pyautogui.press("f3")
    [["ctrl", "shift", "b"]]              → pyautogui.hotkey("ctrl", "shift", "b")
    [["ctrl", "shift", "b"], ["enter"]]   → hotkey then press enter
    """
    for step in hotkey:
        if len(step) == 1:
            pyautogui.press(step[0])
        else:
            pyautogui.hotkey(*step)


def execute_trade(window_title: str, hotkey: Hotkey) -> None:
    """Focus on the trading window and execute the trade using the specified hotkeys."""
    if focus_window(window_title):
        press_hotkey(hotkey)
    else:
        raise RuntimeError(f"Unable to focus target window: {window_title!r}")