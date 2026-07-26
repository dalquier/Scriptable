# Launcher Pro V9

## Mission

Launcher Pro est une application Pyto destinée à gérer et lancer des scripts et projets Python sur iPhone.

Le projet doit privilégier la stabilité, la lisibilité et la maintenabilité.

## Objectifs

- importer un script
- importer un projet
- détecter automatiquement le point d'entrée
- lancer un script
- lancer un projet
- gérer une bibliothèque persistante
- rechercher
- gérer les favoris
- renommer
- supprimer

## Architecture

La séparation suivante est obligatoire :

UI

↓

Controller

↓

Services

↓

Runner

↓

Registry

Le code métier ne doit jamais dépendre de Pyto.

Toute interaction Pyto doit être isolée dans les modules UI.

## Arborescence

core/
ui/
tests/
docs/
library/
logs/
data/

## Règles

- fonctions courtes
- classes simples
- type hints partout
- docstrings
- journalisation systématique
- aucune duplication de code
- pas de variables globales inutiles

## Git

Petits commits atomiques.

Un seul objectif par commit.

Chaque commit doit laisser un projet exécutable.

## Tests

Chaque nouvelle fonctionnalité doit disposer d'un test correspondant.

Aucune régression n'est acceptable.

## Runner

Toujours restaurer :

- sys.path
- sys.argv
- cwd
- __main__

après chaque lancement.

## Registry

Le registre JSON est la source de vérité.

Ne jamais rescanner le disque inutilement.

## UI

La vue ne lance jamais directement un script.

La vue émet une intention.

Le Controller exécute l'action.

## Style

Code lisible avant tout.

Préférer une solution simple à une solution complexe.

Éviter les dépendances inutiles.
