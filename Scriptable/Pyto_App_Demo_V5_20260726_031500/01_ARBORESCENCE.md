# Arborescence

```text
Pyto_App_Demo_V5_20260726_031500/
├── 00_README.md
├── 01_ARBORESCENCE.md
├── 02_MANIFEST.json
├── 03_INSTALLATION.md
├── 04_CHANGELOG.md
└── projet/
    ├── main.py
    ├── app_state.py
    ├── native_services.py
    ├── webview_app.py
    └── ui/
        ├── index.html
        ├── app.css
        └── app.js
```

## Rôles

- `main.py` : point d'entrée.
- `app_state.py` : persistance JSON et état applicatif.
- `native_services.py` : services UIKit/iOS.
- `webview_app.py` : hébergement WebView et pont avec JavaScript.
- `ui/index.html` : structure de l'interface.
- `ui/app.css` : design et adaptation iPhone.
- `ui/app.js` : navigation, rendu et commandes vers Python.
