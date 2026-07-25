from __future__ import annotations

from datetime import datetime, timedelta

import widgets as wd

from core.registry import Registry
from core.url_scheme import run_by_id

BACKGROUND = wd.Color.rgb(12 / 255, 14 / 255, 20 / 255)
CARD = wd.Color.rgb(29 / 255, 33 / 255, 44 / 255)
PRIMARY = wd.Color.rgb(72 / 255, 139 / 255, 1)
TEXT = wd.Color.rgb(1, 1, 1)
MUTED = wd.Color.rgb(174 / 255, 180 / 255, 194 / 255)


def _text(value: str, size: float, color=TEXT, bold: bool = False, padding=None):
    name = ".AppleSystemUIFont" if not bold else ".AppleSystemUIFontBold"
    return wd.Text(
        value,
        font=wd.Font(name, size),
        color=color,
        padding=padding or wd.PADDING_NONE,
    )


def _favorite_items():
    registry = Registry.load()
    favorites = [item for item in registry.items if item.favorite]
    return (favorites or registry.search())[:3]


class LauncherProvider(wd.TimelineProvider):
    def timeline(self):
        return [datetime.now(), datetime.now() + timedelta(hours=1)]

    def widget(self, date):
        widget = wd.Widget()
        items = _favorite_items()

        small = widget.small_layout
        small.set_background_color(BACKGROUND)
        small.add_row([_text("▶", 28, PRIMARY, True), wd.Spacer()])
        small.add_vertical_spacer()
        small.add_row([_text("Launcher Pro", 16, TEXT, True)])
        small.add_row([_text(f"{len(Registry.load().items)} éléments", 11, MUTED)])
        small.set_link("open")

        medium = widget.medium_layout
        medium.set_background_color(BACKGROUND)
        medium.add_row([
            _text("Launcher Pro", 17, TEXT, True),
            wd.Spacer(),
            _text("Favoris", 11, MUTED),
        ])
        medium.add_vertical_spacer()
        if not items:
            medium.add_row([_text("Ajoute un script ou un projet", 13, MUTED)])
            medium.set_link("open")
        else:
            for item in items:
                kind = "APP" if item.kind == "project" else "PY"
                label = _text(f"{kind}  {item.name}", 13, TEXT, True, wd.PADDING_VERTICAL)
                label.link = item.id
                medium.add_row([label, wd.Spacer(), _text("▶", 15, PRIMARY, True)])

        large = widget.large_layout
        large.set_background_color(BACKGROUND)
        large.add_row([_text("Launcher Pro", 20, TEXT, True)])
        large.add_row([_text("Scripts et projets Pyto", 12, MUTED)])
        large.add_vertical_spacer()
        if not items:
            large.add_row([_text("Aucun favori", 15, MUTED)])
            large.set_link("open")
        else:
            for item in items:
                kind = "Projet" if item.kind == "project" else "Script"
                title = _text(item.name, 15, TEXT, True, wd.PADDING_VERTICAL)
                title.link = item.id
                large.add_row([title, wd.Spacer(), _text(kind, 11, MUTED)])
        return widget


def handle_link(value: str) -> None:
    if value == "open":
        from ui.main_view import present_launcher

        present_launcher()
        return

    item, result = run_by_id(value)
    if result.output:
        print(result.output, end="")
    if not result.success:
        raise RuntimeError(result.error or f"Échec de {item.name}")


if wd.link is not None:
    handle_link(str(wd.link))
else:
    wd.provide_timeline(LauncherProvider())
