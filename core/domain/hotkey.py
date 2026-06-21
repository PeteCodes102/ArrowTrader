from __future__ import annotations

from core.domain._types import Hotkey

# The separator that denotes sequential steps in a hotkey string.
_STEP_SEP = " then "


def parse_hotkey(text: str) -> Hotkey:
    """
    Parse a user-typed hotkey string into a ``Hotkey`` (sequence of key combos).

    Format rules
    ────────────
    - Keys within a single chord are joined with ``+``
    - Sequential steps (press one chord, then another) are separated by `` then ``
    - Parsing is case-insensitive; all keys are lowercased for pyautogui

    Examples
    ────────
    >>> parse_hotkey("F3")
    [['f3']]

    >>> parse_hotkey("Shift+Alt+b")
    [['shift', 'alt', 'b']]

    >>> parse_hotkey("ctrl+shift+b then enter")
    [['ctrl', 'shift', 'b'], ['enter']]

    >>> parse_hotkey("ctrl+shift+b then ctrl+shift+s then enter")
    [['ctrl', 'shift', 'b'], ['ctrl', 'shift', 's'], ['enter']]
    """
    text = text.strip()
    if not text:
        raise ValueError("Hotkey string must not be empty.")

    steps = [s.strip() for s in text.lower().split(_STEP_SEP)]

    parsed: Hotkey = []
    for step in steps:
        if not step:
            continue
        keys = [k.strip() for k in step.split("+") if k.strip()]
        if not keys:
            continue
        parsed.append(keys)

    if not parsed:
        raise ValueError(f"Could not parse hotkey: {text!r}")

    return parsed


def format_hotkey(hotkey: Hotkey) -> str:
    """
    Inverse of ``parse_hotkey`` — turns a parsed ``Hotkey`` back into a
    human-readable string.

    >>> format_hotkey([['ctrl', 'shift', 'b'], ['enter']])
    'ctrl+shift+b then enter'
    """
    return _STEP_SEP.join("+".join(step) for step in hotkey)
