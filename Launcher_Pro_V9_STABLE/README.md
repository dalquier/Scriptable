# Launcher Pro V9 — Sprint 1

Application Pyto permettant de constituer une bibliothèque persistante de scripts et de projets Python, puis de les lancer.

## Fonctionnalités

- import d'un fichier `.py` ou d'un dossier de projet ;
- détection automatique du point d'entrée (`__main__.py`, `main.py`, etc.) ;
- bibliothèque JSON persistante, recherche et favoris ;
- renommage et suppression (la suppression de la fiche ne supprime jamais les sources) ;
- exécution avec répertoire de travail et `sys.path` isolés ;
- interface native Pyto.

## Architecture

`launcher_pro` est séparé en cinq couches :

- `ui` : adaptation Pyto uniquement ;
- `controller` : orchestration et modèles de vue ;
- `services` : import et détection du point d'entrée ;
- `runner` : exécution Python ;
- `registry` : modèle et persistance de la bibliothèque.

Le code métier (`controller`, `services`, `runner`, `registry`) n'importe jamais Pyto.

## Installation dans Pyto

1. Copiez le dossier `Launcher_Pro_V9_STABLE` dans les documents de Pyto.
2. Ouvrez puis exécutez `main.py`.
3. Utilisez **Importer** pour sélectionner un script ou **Projet** pour sélectionner un dossier.

Les métadonnées sont écrites dans `Documents/Launcher Pro V9/library.json`. Une copie privée et durable de chaque source est conservée dans `Documents/Launcher Pro V9/library/` ; les originaux ne sont jamais modifiés.

## Développement

```bash
cd Launcher_Pro_V9_STABLE
python -m unittest discover -s tests -v
```
