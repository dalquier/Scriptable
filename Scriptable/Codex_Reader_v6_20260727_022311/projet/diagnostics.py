# -*- coding: utf-8 -*-
"""Diagnostic des capacités WebView de Pyto."""

import pyto_ui as ui

web = ui.WebView()
print("TYPE:", type(web))
print("ATTRIBUTS WEBVIEW:")
for name in sorted(dir(web)):
    if any(token in name.lower() for token in ("java", "eval", "script", "html", "url", "view")):
        print(" -", name)

native = getattr(web, "__py_view__", None)
print("\nNATIVE:", type(native), native)
if native is not None:
    print("ATTRIBUTS NATIFS PERTINENTS:")
    for name in sorted(dir(native)):
        if any(token in name.lower() for token in ("java", "eval", "script", "web", "cookie", "data")):
            print(" -", name)
