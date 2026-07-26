# -*- coding: utf-8 -*-
"""Diagnostic des capacités WebView de la version installée de Pyto."""

import json
import platform
import sys

import pyto_ui as ui

from browser_adapter import BrowserAdapter


def main():
    web = ui.WebView()
    adapter = BrowserAdapter(web)
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "webview_type": type(web).__name__,
        "capabilities": adapter.capabilities(),
        "all_public_methods": [name for name in dir(web) if not name.startswith("_")],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
