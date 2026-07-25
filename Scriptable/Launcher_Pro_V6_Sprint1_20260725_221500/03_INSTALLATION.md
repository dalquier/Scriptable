# Installation et test

## Installation

1. Télécharge le dossier `projet`.
2. Conserve les sous-dossiers `core` et `data`.
3. Ouvre `install.py` dans Pyto.
4. Exécute-le une fois.

## Validation du Sprint 1

Exécute `test_sprint1.py`.

Le test vérifie :

- la création des dossiers et JSON ;
- la lecture et l'écriture du registre ;
- la création d'une sauvegarde ;
- l'exécution d'un script local de démonstration ;
- l'ajout d'une entrée dans l'historique ;
- l'écriture dans le journal.

## Utilisation

Exécute `LauncherPro.py`.

Le menu console permet d'importer, lister, lancer, supprimer et sauvegarder des scripts. L'interface native complète sera ajoutée au Sprint 2.

## Limite iOS

Launcher Pro copie chaque script importé dans `data/scripts`. Cette copie locale évite de perdre l'accès au fichier original lorsque le fournisseur de fichiers iOS révoque l'autorisation temporaire.
