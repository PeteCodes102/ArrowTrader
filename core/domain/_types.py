from typing import Union
import datetime as dt

WindowName = str

# A hotkey is a sequence of steps; each step is a list of keys pressed together.
# e.g. "ctrl+shift+b then enter" → [["ctrl", "shift", "b"], ["enter"]]
# e.g. "F3"                      → [["f3"]]
Hotkey = list[list[str]]

Timestamp = Union[str, dt.datetime]

