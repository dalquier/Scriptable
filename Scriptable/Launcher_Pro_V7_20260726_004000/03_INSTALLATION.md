# Installation de Launcher Pro V7

## Installation propre

1. Télécharge le dossier `projet` complet depuis GitHub.
2. Place-le dans un dossier dédié, par exemple :

```text
Sur mon iPhone/Pyto/LauncherProV7/
```

3. Conserve impérativement les sous-dossiers `core`, `ui` et `data`.
4. Ouvre `install.py` dans Pyto.
5. Exécute-le une fois.
6. Ouvre ensuite `LauncherPro.py` et exécute-le.

## Ajouter un script autonome

1. Touche `＋ Script`.
2. Sélectionne un fichier `.py`.
3. Le fichier est copié immédiatement dans `data/scripts/`.
4. Une fiche de modification s’ouvre pour changer le nom et la catégorie.

Un script autonome doit contenir tout ce dont il a besoin, sauf les modules installés dans Pyto.

## Ajouter un projet Pyto

1. Touche `＋ Projet`.
2. Sélectionne le dossier racine du projet.
3. Launcher Pro détecte les fichiers `.py`.
4. Choisis le script de démarrage : `main.py`, `bootstrap.py`, `app.py` ou tout autre fichier proposé.
5. Modifie ensuite le nom, la catégorie ou le point d’entrée avec le bouton `•••`.

Les projets ne sont pas copiés. Launcher Pro mémorise leur dossier et lance le point d’entrée avec le dossier racine ajouté à `sys.path`.

## Modifier ou supprimer

Sur une carte, touche `•••` pour :

- modifier le nom ;
- modifier la catégorie ;
- modifier le point d’entrée d’un projet ;
- supprimer l’élément.

## Conservation des données

Les données sont stockées dans :

```text
projet/data/
```

Pour une mise à jour future, conserve ce dossier afin de garder ta bibliothèque et ton historique.
