# ─────────────────────────────────────────────────────────
#  Arrow Trader — Design Tokens
# ─────────────────────────────────────────────────────────

COLORS = {
    # Background layers
    "bg":            "#0D1117",
    "surface":       "#161B22",
    "surface_alt":   "#21262D",
    "border":        "#30363D",
    "border_subtle": "#21262D",

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

FONTS = {
    "title":   ("Segoe UI",   18, "bold"),
    "section": ("Segoe UI",   10, "bold"),
    "label":   ("Segoe UI",    9, "normal"),
    "input":   ("Consolas",   12, "normal"),
    "button":  ("Segoe UI",   11, "bold"),
    "mono":    ("Consolas",   11, "normal"),
}

# ── Shared entry widget kwargs ─────────────────────────────
ENTRY_STYLE = {
    "height":                  38,
    "corner_radius":            8,
    "border_width":             1,
    "border_color":             COLORS["border"],
    "fg_color":                 COLORS["surface_alt"],
    "text_color":               COLORS["text"],
    "placeholder_text_color":   COLORS["text_dim"],
    "font":                     FONTS["input"],
}

# ── Per-action button kwargs ───────────────────────────────
_BTN_BASE = {
    "height":        44,
    "corner_radius":  8,
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
