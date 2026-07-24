# Changelog

## Version 5.0 modulaire — 2026-07-24 22:34

Création initiale du projet modulaire.

### Fichiers créés

- `00_README.md`
- `01_ARBORESCENCE.md`
- `02_MANIFEST.json`
- `03_INSTALLATION.md`
- `04_CHANGELOG.md`
- `projet/.gitignore`
- `projet/app_controller.py`
- `projet/config.py`
- `projet/exporter.py`
- `projet/file_picker.py`
- `projet/importer.py`
- `projet/main.py`
- `projet/prompts.py`
- `projet/ui_app.py`
- `projet/utils.py`

### Fonctionnalités ajoutées

- Architecture modulaire séparant interface, contrôleur, export, import, sélection de fichiers, prompts, configuration et utilitaires.
- Callbacks de boutons explicitement conservés en mémoire.
- Export complet vers `00_INDEX.md` et `PART_XXX.md`.
- Fragmentation et répartition automatique des contenus.
- Encodage UTF-8 et Base64.
- Import avec validation des chemins et empreintes SHA-256.
- Prompt ChatGPT V5 et prompt de migration copiables.
- Interface Pyto affichée en mode feuille refermable.

### Corrections

- Suppression de la logique monolithique qui rendait difficile le diagnostic des boutons inactifs.
- Liaison explicite de chaque bouton à une méthode du contrôleur.
- Ajout d’un sélecteur de dossier avec solution de repli.

### Incompatibilités et migrations

- Cette livraison ne modifie pas l’ancienne livraison horodatée.
- Lancer désormais `projet/main.py` et conserver tous les modules dans le même dossier.
- Le mode DELTA et les snapshots avancés de l’ancienne proposition ne sont pas repris dans cette version corrective.

### Fichiers modifiés

Aucun fichier d’une ancienne livraison n’a été modifié.

### Fichiers supprimés

Aucun fichier supprimé.
