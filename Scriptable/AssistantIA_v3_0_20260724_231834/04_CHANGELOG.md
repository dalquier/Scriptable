# Journal des changements

## Version 3.0 — 24 juillet 2026

Création initiale du projet.

### Fichiers créés

- fichiers de contrôle `00_README.md`, `01_ARBORESCENCE.md`, `02_MANIFEST.json`, `03_INSTALLATION.md` et `04_CHANGELOG.md` ;
- `.gitignore` ;
- noyau applicatif ;
- client OpenAI Responses ;
- stockage SQLite ;
- gestionnaire de conversations ;
- interface graphique Pyto ;
- point d’entrée principal ;
- exemple de configuration privée.

### Fonctionnalités ajoutées

- interface plein écran ;
- saisie multiligne ;
- historique local persistant ;
- création de nouvelles conversations ;
- recherche Web facultative ;
- appels réseau exécutés hors du fil principal ;
- gestion des erreurs API, réseau et configuration.

### Fichiers modifiés

Aucun fichier d’une ancienne livraison n’a été modifié.

### Fichiers supprimés

Aucun.

### Migration

Cette livraison est indépendante des anciennes versions. La base SQLite est créée automatiquement sous `projet/database/assistantia_v3.sqlite3`.

### Incompatibilités

Le point d’entrée graphique nécessite Pyto et son module `pyto_ui`.
