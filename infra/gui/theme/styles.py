# ─────────────────────────────────────────────────────────
#  Arrow Trader — Design Tokens
# ─────────────────────────────────────────────────────────

_BASE_COLORS = {
    # Background layers
    "bg":            "#0B0F14",
    "surface":       "#121821",
    "surface_alt":   "#1A222C",
    "border":        "#26303B",
    "border_subtle": "#1A222C",

    # Text
    "text":          "#E6EDF3",
    "text_dim":      "#8B949E",
    "text_muted":    "#484F58",

    # Accent
    "accent":        "#388BFD",
    "accent_muted":  "#1F3A5F",

    # Action colours
    "buy":           "#3FB950",
    "buy_hover":     "#238636",
    "buy_muted":     "#0F2B1A",

    "sell":          "#F85149",
    "sell_hover":    "#B91C1C",
    "sell_muted":    "#2B0F0F",

    "exit":          "#E3B341",
    "exit_hover":    "#B45309",
    "exit_muted":    "#2B1F00",

    "reverse":       "#BC8CFF",
    "reverse_hover": "#7C3AED",
    "reverse_muted": "#1E0F38",
}

_THEME_OVERRIDES: dict[str, dict[str, str]] = {
    "Default": {},
    "Black & Green": {
        "bg": "#000000",
        "surface": "#020402",
        "surface_alt": "#051005",
        "border": "#0F3B0F",
        "border_subtle": "#0A240A",
        "text": "#33FF66",
        "text_dim": "#1ED760",
        "text_muted": "#138A3D",
        "accent": "#2BFF5B",
        "accent_muted": "#0F4A20",
        "buy": "#0A260F",
        "buy_hover": "#113816",
        "buy_muted": "#061907",
        "sell": "#0A260F",
        "sell_hover": "#113816",
        "sell_muted": "#061907",
        "exit": "#0A260F",
        "exit_hover": "#113816",
        "exit_muted": "#061907",
        "reverse": "#0A260F",
        "reverse_hover": "#113816",
        "reverse_muted": "#061907",
    },
    "Black & Gray": {
        "bg": "#000000",
        "surface": "#050505",
        "surface_alt": "#111111",
        "border": "#2A2A2A",
        "border_subtle": "#1C1C1C",
        "text": "#C7C7C7",
        "text_dim": "#9A9A9A",
        "text_muted": "#6E6E6E",
        "accent": "#B0B0B0",
        "accent_muted": "#4E4E4E",
        "buy": "#1A1A1A",
        "buy_hover": "#252525",
        "buy_muted": "#121212",
        "sell": "#1A1A1A",
        "sell_hover": "#252525",
        "sell_muted": "#121212",
        "exit": "#1A1A1A",
        "exit_hover": "#252525",
        "exit_muted": "#121212",
        "reverse": "#1A1A1A",
        "reverse_hover": "#252525",
        "reverse_muted": "#121212",
    },
    "Orange & White": {
        "bg": "#F97316",
        "surface": "#EA580C",
        "surface_alt": "#C2410C",
        "border": "#FDBA74",
        "border_subtle": "#FDBA74",
        "text": "#FFFFFF",
        "text_dim": "#FFF7ED",
        "text_muted": "#FED7AA",
        "accent": "#FFFFFF",
        "accent_muted": "#FFE7D1",
        "buy": "#B45309",
        "buy_hover": "#9A4208",
        "buy_muted": "#7C2D12",
        "sell": "#B45309",
        "sell_hover": "#9A4208",
        "sell_muted": "#7C2D12",
        "exit": "#B45309",
        "exit_hover": "#9A4208",
        "exit_muted": "#7C2D12",
        "reverse": "#B45309",
        "reverse_hover": "#9A4208",
        "reverse_muted": "#7C2D12",
    },
}

COLORS: dict[str, str] = dict(_BASE_COLORS)

FONTS = {
    "title":   ("Segoe Print", 20, "bold"),
    "section": ("Segoe Print", 13, "bold"),
    "label":   ("Segoe UI",    10, "normal"),
    "input":   ("Consolas",    12, "normal"),
    "button":  ("Segoe UI",    11, "bold"),
    "mono":    ("Consolas",    11, "normal"),
}

# ── Shared entry widget kwargs ─────────────────────────────
ENTRY_STYLE = {
    "height":                  36,
    "corner_radius":            7,
    "border_width":             1,
    "border_color":             COLORS["border"],
    "fg_color":                 COLORS["surface_alt"],
    "text_color":               COLORS["text"],
    "placeholder_text_color":   COLORS["text_dim"],
    "font":                     FONTS["input"],
}

# ── Per-action button kwargs ───────────────────────────────
_BTN_BASE = {
    "height":        38,
    "corner_radius":  7,
    "border_width":   0,
    "font":           FONTS["button"],
}

ACTION_BUTTONS = {
    "buy": {
        **_BTN_BASE,
        "fg_color":    COLORS["buy"],
        "hover_color": COLORS["buy_hover"],
        "text_color":  "#0D1117",
    },
    "sell": {
        **_BTN_BASE,
        "fg_color":    COLORS["sell"],
        "hover_color": COLORS["sell_hover"],
        "text_color":  "#E6EDF3",
    },
    "exit": {
        **_BTN_BASE,
        "fg_color":    COLORS["exit"],
        "hover_color": COLORS["exit_hover"],
        "text_color":  "#0D1117",
    },
    "reverse": {
        **_BTN_BASE,
        "fg_color":    COLORS["reverse"],
        "hover_color": COLORS["reverse_hover"],
        "text_color":  "#0D1117",
    },
}


def _refresh_action_buttons() -> None:
    ACTION_BUTTONS["buy"].update(
        {
            "fg_color": COLORS["buy"],
            "hover_color": COLORS["buy_hover"],
            "text_color": COLORS["text"],
        }
    )
    ACTION_BUTTONS["sell"].update(
        {
            "fg_color": COLORS["sell"],
            "hover_color": COLORS["sell_hover"],
            "text_color": COLORS["text"],
        }
    )
    ACTION_BUTTONS["exit"].update(
        {
            "fg_color": COLORS["exit"],
            "hover_color": COLORS["exit_hover"],
            "text_color": COLORS["text"],
        }
    )
    ACTION_BUTTONS["reverse"].update(
        {
            "fg_color": COLORS["reverse"],
            "hover_color": COLORS["reverse_hover"],
            "text_color": COLORS["text"],
        }
    )


def available_theme_names() -> list[str]:
    return list(_THEME_OVERRIDES.keys())


def apply_theme(theme_name: str) -> str:
    selected = theme_name if theme_name in _THEME_OVERRIDES else "Default"
    merged = dict(_BASE_COLORS)
    merged.update(_THEME_OVERRIDES[selected])
    COLORS.clear()
    COLORS.update(merged)
    _refresh_action_buttons()
    return selected
