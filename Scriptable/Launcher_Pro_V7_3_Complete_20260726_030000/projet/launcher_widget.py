from __future__ import annotations

import threading
import urllib.parse
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

import widgets as wd

DIRECT_ITEM_ID = ""
BACKGROUND = wd.Color.rgb(12 / 255, 14 / 255, 20 / 255)
PRIMARY = wd.Color.rgb(72 / 255, 139 / 255, 1)
TEXT = wd.Color.rgb(1, 1, 1)
MUTED = wd.Color.rgb(174 / 255, 180 / 255, 194 / 255)


def _script_path() -> Path:
    path = getattr(threading.current_thread(), "script_path", None)
    if path:
        return Path(str(path))
    try:
        return Path(__file__)
    except Exception:
        return Path("launcher_widget.py")


def _launcher_path() -> Path:
    return _script_path().resolve().parent / "LauncherPro.py"


def _launcher_url(item_id: str = "") -> str:
    launcher = _launcher_path()
    root = launcher.parent
    argv = [str(launcher), "--run", item_id] if item_id else [str(launcher)]
    code = (
        "import os,runpy,sys;"
        f"p={str(launcher)!r};r={str(root)!r};"
        "sys.path.insert(0,r) if r not in sys.path else None;"
        "os.chdir(r);"
        f"sys.argv={argv!r};"
        "runpy.run_path(p,run_name='__main__')"
    )
    return "pyto://x-callback/?code=" + urllib.parse.quote(code, safe="")


def _text(value: str, size: float, color=TEXT, bold: bool = False, padding=None):
    name = ".AppleSystemUIFontBold" if bold else ".AppleSystemUIFont"
    return wd.Text(value, font=wd.Font(name, size), color=color, padding=padding or wd.PADDING_NONE)


class LauncherProvider(wd.TimelineProvider):
    def timeline(self):
        return [datetime.now(), datetime.now() + timedelta(hours=1)]

    def widget(self, date):
        widget = wd.Widget()
        action = "run" if DIRECT_ITEM_ID else "open"

        small = widget.small_layout
        small.set_background_color(BACKGROUND)
        small.add_row([_text("▶", 30, PRIMARY, True), wd.Spacer()])
        small.add_vertical_spacer()
        small.add_row([_text("Launcher Pro", 16, TEXT, True)])
        small.add_row([_text("Lancer" if DIRECT_ITEM_ID else "Ouvrir", 11, MUTED)])
        small.set_link(action)

        medium = widget.medium_layout
        medium.set_background_color(BACKGROUND)
        medium.add_row([_text("▶", 24, PRIMARY, True), _text("  Launcher Pro", 18, TEXT, True), wd.Spacer()])
        medium.add_vertical_spacer()
        medium.add_row([_text("Toucher pour ouvrir tes scripts et projets", 13, MUTED)])
        medium.set_link(action)

        large = widget.large_layout
        large.set_background_color(BACKGROUND)
        large.add_row([_text("Launcher Pro", 21, TEXT, True), wd.Spacer(), _text("Pyto", 12, MUTED)])
        large.add_vertical_spacer()
        large.add_row([_text("Scripts autonomes et projets", 15, TEXT, True)])
        large.add_row([_text("Ouvre la bibliothèque depuis l’écran d’accueil.", 12, MUTED)])
        large.add_vertical_spacer()
        large.add_row([_text("▶  Ouvrir", 16, PRIMARY, True)])
        large.set_link(action)
        return widget


def handle_link(value: str) -> None:
    item_id = DIRECT_ITEM_ID if value == "run" else ""
    webbrowser.open(_launcher_url(item_id))


if wd.link is not None:
    handle_link(str(wd.link))
else:
    wd.provide_timeline(LauncherProvider())
