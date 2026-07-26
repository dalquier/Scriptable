# Launcher Pro V9 — Sprint 1

Première version fonctionnelle et testable du cœur de Launcher Pro pour Pyto. Le Sprint 1 utilise exclusivement la bibliothèque standard Python et ne contient volontairement pas encore l'interface graphique finale.

## Fonctionnalités terminées

- modèle `LauncherItem` sérialisable avec favoris et statistiques d'exécution ;
- arborescence persistante `data/`, `logs/` et `library/{scripts,projects}` ;
- registre JSON versionné, validé et écrit atomiquement ;
- journal technique rotatif et historique métier JSON Lines ;
- validation syntaxique des scripts UTF-8 ;
- copie durable d'un script ou d'un projet complet ;
- découverte, classement, détection automatique et sélection explicite du point d'entrée ;
- recherche, favoris, renommage et suppression transactionnels ;
- exécution des scripts et projets, avec métriques et résultat persistant ;
- restauration garantie de `cwd`, `sys.path`, `sys.argv` et `sys.modules['__main__']` ;
- contrôleur central basé sur des intentions, indépendant de Pyto.

## Architecture

```text
projet/
├── LauncherPro.py            # point d'entrée exécutable provisoire
├── config.py                 # configuration standard
├── controller/               # orchestration des intentions
├── core/
│   ├── history.py            # événements métier JSONL
│   ├── importer.py           # validation, détection et copies
│   ├── library_service.py    # façade métier
│   ├── logger.py             # journal technique rotatif
│   ├── models.py             # LauncherItem
│   ├── paths.py              # dossiers d'exécution
│   ├── registry.py           # registre JSON atomique
│   └── runner.py             # moteur d'exécution
└── tests/                    # tests unitaires du cœur
```

Le code métier n'importe ni `pyto_ui`, ni `file_system`, ni aucune dépendance tierce.

## Exécution

Depuis `Launcher_Pro_V9_STABLE/projet` :

```bash
python LauncherPro.py
```

Le point d'entrée initialise les dossiers persistants et affiche la bibliothèque. La future UI utilisera exclusivement `LauncherController.dispatch()`.

## Tests

```bash
cd Launcher_Pro_V9_STABLE/projet
python -m unittest discover -s tests -v
python -m compileall -q LauncherPro.py config.py core controller tests
```

## Sprint 2

Restent volontairement à réaliser :

- interface graphique Pyto native et vues de bibliothèque ;
- adaptateurs Pyto pour sélectionner fichiers et dossiers ;
- navigation, recherche et menus d'actions visuels ;
- exécution asynchrone pilotée par l'UI et présentation des erreurs ;
- tests manuels sur iPhone/iPad et tests de l'adaptateur Pyto.
