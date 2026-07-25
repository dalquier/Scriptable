# Arborescence

```text
Launcher_Pro_20260725_220815/
├── 00_README.md
├── 01_ARBORESCENCE.md
├── 02_MANIFEST.json
├── 03_INSTALLATION.md
├── 04_CHANGELOG.md
└── projet/
    ├── LauncherPro.py
    ├── install.py
    ├── launcher_widget.py
    ├── launcher_core.py
    ├── launcher_storage.py
    ├── launcher_runner.py
    ├── launcher_picker.py
    ├── launcher_theme.py
    └── data/
        ├── registry.json
        └── scripts/
            └── .gitkeep
```

## Responsabilités

- `LauncherPro.py` : interface et orchestration.
- `launcher_core.py` : modèles et logique métier.
- `launcher_storage.py` : lecture/écriture atomique du registre.
- `launcher_runner.py` : exécution isolée avec capture des erreurs.
- `launcher_picker.py` : import via le sélecteur iOS.
- `launcher_theme.py` : constantes visuelles.
- `launcher_widget.py` : raccourci widget Pyto.
- `install.py` : préparation et vérification de l’installation.
