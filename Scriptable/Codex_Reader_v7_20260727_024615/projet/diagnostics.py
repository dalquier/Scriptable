# -*- coding: utf-8 -*-
"""Diagnostic rapide des capacités WebView de Pyto."""

import pyto_ui as ui

web = ui.WebView()
print("TYPE:", type(web))
print("ATTRIBUTS JAVASCRIPT:")
for name in dir(web):
    lowered = name.lower()
    if "java" in lowered or "script" in lowered or "eval" in lowered or "web" in lowered:
        print(" -", name)
