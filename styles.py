_LIGHT_THEME = {
    "BG": "#F4F7F5",
    "SIDEBAR": "#12372F",
    "SIDEBAR_HI": "#245548",
    "TEXT": "#16362E",
    "MUTED": "#80918C",
    "WHITE": "#FFFFFF",
    "CORAL": "#F0644D",
    "MINT": "#9ED9B7",
    "GOLD": "#E6B84A",
    "BLUE": "#78B7C8",
    "BORDER": "#DFE7E3",
    "PALE": "#EDF3F0",
    "SELECTED": "#DDEFE5",
    "PROGRESS_TROUGH": "#DDE4DE"
}

_DARK_THEME = {
    "BG": "#101816",
    "SIDEBAR": "#0B211B",
    "SIDEBAR_HI": "#1F473B",
    "TEXT": "#E6F0EB",
    "MUTED": "#9BAEA6",
    "WHITE": "#1A2923",
    "CORAL": "#FF8A72",
    "MINT": "#8ED4AA",
    "GOLD": "#EDC36B",
    "BLUE": "#7BC6D8",
    "BORDER": "#33453D",
    "PALE": "#263831",
    "SELECTED": "#315044",
    "PROGRESS_TROUGH": "#2B3C34"
}

DARK_MODE = False


def set_dark_mode(enabled):
    global BG, SIDEBAR, SIDEBAR_HI, TEXT, MUTED, WHITE
    global CORAL, MINT, GOLD, BLUE, BORDER, PALE
    global SELECTED, PROGRESS_TROUGH, DARK_MODE

    palette = _DARK_THEME if enabled else _LIGHT_THEME

    BG = palette["BG"]
    SIDEBAR = palette["SIDEBAR"]
    SIDEBAR_HI = palette["SIDEBAR_HI"]
    TEXT = palette["TEXT"]
    MUTED = palette["MUTED"]
    WHITE = palette["WHITE"]
    CORAL = palette["CORAL"]
    MINT = palette["MINT"]
    GOLD = palette["GOLD"]
    BLUE = palette["BLUE"]
    BORDER = palette["BORDER"]
    PALE = palette["PALE"]
    SELECTED = palette["SELECTED"]
    PROGRESS_TROUGH = palette["PROGRESS_TROUGH"]
    DARK_MODE = enabled


set_dark_mode(False)

FONT = "Segoe UI"