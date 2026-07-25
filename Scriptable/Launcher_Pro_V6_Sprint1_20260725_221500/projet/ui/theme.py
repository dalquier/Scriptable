from __future__ import annotations

try:
    import pyto_ui as ui
except ImportError:  # Permet d'importer le module hors de Pyto pour les tests.
    ui = None


def _hex_components(value: str):
    """Convertit RRGGBB ou #RRGGBB en composantes comprises entre 0 et 1."""
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        raise ValueError(f"Couleur hexadécimale invalide : {value}")
    return tuple(int(cleaned[index:index + 2], 16) / 255 for index in (0, 2, 4))


def _rgb(value: str):
    """Crée toujours un véritable objet pyto_ui.Color dans Pyto."""
    if ui is None:
        return value

    red, green, blue = _hex_components(value)
    rgb = getattr(ui.Color, "rgb", None)
    if not callable(rgb):
        raise RuntimeError("Cette version de Pyto ne fournit pas ui.Color.rgb")

    try:
        return rgb(red, green, blue, 1.0)
    except TypeError:
        return rgb(red, green, blue)


def _color(light_hex: str, dark_hex: str):
    """Crée une couleur adaptative, avec repli sur une couleur Pyto valide."""
    if ui is None:
        return light_hex

    light = _rgb(light_hex)
    dark = _rgb(dark_hex)

    dynamic = getattr(ui.Color, "dynamic", None)
    if callable(dynamic):
        try:
            return dynamic(light, dark)
        except Exception:
            pass

    # Certaines versions exposent la couleur adaptative sous le nom `color`.
    color_factory = getattr(ui.Color, "color", None)
    if callable(color_factory):
        try:
            return color_factory(light=light, dark=dark)
        except Exception:
            pass

    # Repli sûr : la version sombre reste un objet Color, jamais une chaîne.
    return dark


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
