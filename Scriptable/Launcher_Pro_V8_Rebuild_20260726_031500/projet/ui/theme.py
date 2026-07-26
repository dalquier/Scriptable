from __future__ import annotations

import pyto_ui as ui


def color(hex_value: str):
    value = hex_value.strip().lstrip("#")
    if len(value) == 6:
        r, g, b = int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
        return ui.Color.rgb(r / 255, g / 255, b / 255)
    return ui.Color.rgb(0, 0, 0)


BACKGROUND = color("0B0F17")
SURFACE = color("141A24")
SURFACE_ALT = color("202938")
CARD = color("171E2A")
PRIMARY = color("4F8CFF")
PRIMARY_SOFT = color("1E3159")
TEXT = color("FFFFFF")
MUTED = color("AAB3C2")
DANGER = color("FF6B6B")


def font(size: float, bold: bool = False):
    try:
        return ui.Font.system_font_of_size(size, weight=0.6 if bold else 0.0)
    except Exception:
        try:
            return ui.Font(".AppleSystemUIFontBold" if bold else ".AppleSystemUIFont", size)
        except Exception:
            return None
