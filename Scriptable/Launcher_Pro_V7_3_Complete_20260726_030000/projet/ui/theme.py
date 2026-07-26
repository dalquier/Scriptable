from __future__ import annotations

try:
    import pyto_ui as ui
except ImportError:
    ui = None


def _rgb(hex_value: str):
    if ui is None:
        return hex_value
    value = hex_value.strip().lstrip("#")
    red = int(value[0:2], 16) / 255
    green = int(value[2:4], 16) / 255
    blue = int(value[4:6], 16) / 255
    return ui.Color.rgb(red, green, blue)


BACKGROUND = _rgb("0B0D12")
SURFACE = _rgb("171A21")
SURFACE_ALT = _rgb("20242D")
CARD = _rgb("1B1F27")
TEXT = _rgb("F7F8FA")
MUTED = _rgb("9AA2B1")
PRIMARY = _rgb("4C8DFF")
PRIMARY_SOFT = _rgb("18315F")
SUCCESS = _rgb("35C978")
DANGER = _rgb("FF5A5F")
WARNING = _rgb("F6B94A")
BORDER = _rgb("323844")


def font(size: float, bold: bool = False):
    if ui is None:
        return None
    try:
        return ui.Font.bold_system_font_of_size(size) if bold else ui.Font.system_font_of_size(size)
    except Exception:
        return None
