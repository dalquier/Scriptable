from __future__ import annotations

try:
    import pyto_ui as ui
except ImportError:  # Permet d'importer le module hors de Pyto pour les tests.
    ui = None


def _color(light_hex: str, dark_hex: str):
    if ui is None:
        return light_hex
    dynamic = getattr(ui.Color, "dynamic", None)
    if callable(dynamic):
        try:
            return dynamic(ui.Color.hex(light_hex), ui.Color.hex(dark_hex))
        except Exception:
            pass
    try:
        return ui.Color.hex(dark_hex)
    except Exception:
        return dark_hex


BACKGROUND = _color("F2F2F7", "0B0B0F")
CARD = _color("FFFFFF", "1C1C1E")
CARD_ALT = _color("F7F7FA", "252529")
TEXT = _color("111114", "FFFFFF")
SECONDARY_TEXT = _color("6E6E73", "A1A1AA")
PRIMARY = _color("246BFD", "4C8DFF")
PRIMARY_SOFT = _color("E7EFFF", "182B50")
SUCCESS = _color("168A45", "38D276")
DANGER = _color("D92D20", "FF5A52")
BORDER = _color("E2E2E8", "34343A")

TITLE = "Launcher Pro"
SUBTITLE = "Tes scripts Python, prêts à partir"


def font(size: float, bold: bool = False):
    if ui is None:
        return None
    try:
        return (ui.Font.bold_system_font_of_size(size) if bold
                else ui.Font.system_font_of_size(size))
    except Exception:
        return None
