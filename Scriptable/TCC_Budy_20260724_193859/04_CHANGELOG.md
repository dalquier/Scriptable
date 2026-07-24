# Changelog

## Sprint 0.2.2

### Fichiers créés

- fichiers de contrôle de la livraison GitHub ;
- `.gitignore` dans le projet.

### Fichiers modifiés

- `projet/tcc_budy/ui/webview.py` : couleurs et autoresizing modernes, fermeture renforcée via `close()` puis `dismiss()` ;
- `projet/README.md` ;
- `projet/INSTALLATION_PYTO.md`.

### Fichiers supprimés de la livraison

- base SQLite locale ;
- fichiers WAL/SHM ;
- journaux ;
- métadonnées `__MACOSX` ;
- caches Python.

### Corrections

- suppression des avertissements liés à `COLOR_SYSTEM_BACKGROUND`, `FLEXIBLE_WIDTH` et `FLEXIBLE_HEIGHT` sur les versions modernes de Pyto ;
- fermeture du logger déjà gérée explicitement ;
- tentative de fermeture de la vue par `close()` puis `dismiss()` sur le thread principal.

### Tests

- 4 tests automatiques réussis.

Version précédente identifiable : Sprint 0.2 v0.8.
