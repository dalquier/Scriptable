# -*- coding: utf-8 -*-
import pyto_ui as ui

web = ui.WebView()
print("TYPE:", type(web))
print("ATTRIBUTS JAVASCRIPT:")
for name in dir(web):
    if "javascript" in name.lower() or "evaluate" in name.lower() or "_js" in name.lower():
        print(" -", name)
