# -*- coding: utf-8 -*-
"""Diagnostic rapide de la WebView Pyto."""

import pyto_ui as ui

web = ui.WebView()
print("TYPE:", type(web))
print("evaluate_js disponible:", hasattr(web, "evaluate_js"))
print("Méthodes contenant js/javascript:")
for name in dir(web):
    if "js" in name.lower() or "javascript" in name.lower():
        print(" -", name)
