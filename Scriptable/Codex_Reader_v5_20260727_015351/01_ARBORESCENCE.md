# Arborescence

```text
Codex_Reader_v5_20260727_015351/
├── 00_README.md
├── 01_ARBORESCENCE.md
├── 02_MANIFEST.json
├── 03_INSTALLATION.md
├── 04_CHANGELOG.md
└── projet/
    ├── app.py
    ├── browser_adapter.py
    ├── extractor.py
    ├── renderer.py
    ├── storage.py
    ├── diagnostics.py
    └── README.md
```

## Rôle des modules

- `app.py` : interface Pyto et orchestration.
- `browser_adapter.py` : compatibilité avec plusieurs versions de `pyto_ui.WebView`, puis fallback WKWebView.
- `extractor.py` : JavaScript d’extraction et normalisation des résultats.
- `renderer.py` : construction de la vue HTML dédiée.
- `storage.py` : préférences, historique et exports.
- `diagnostics.py` : inventaire des méthodes disponibles dans la version locale de Pyto.
