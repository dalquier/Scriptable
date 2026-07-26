# GitHub Content Manager V6

Gestionnaire natif Pyto pour consulter et modifier le contenu d’un dépôt GitHub depuis un iPhone.

## Principes V6

- interface 100 % `pyto_ui` native ;
- aucune WebView ;
- aucun JavaScript ;
- aucun appel `View.present()` ;
- affichage par `ui.show_view()` ;
- client GitHub fondé sur la bibliothèque standard Python ;
- jeton conservé uniquement dans le dossier local du projet sur l’iPhone.

## Fonctions

- lister le contenu d’un dossier ;
- ouvrir un fichier texte ;
- enregistrer un fichier ;
- créer un fichier ;
- créer un dossier via `.gitkeep` ;
- renommer un fichier ;
- supprimer un fichier ;
- modifier dépôt, branche, dossier racine et jeton.

## Démarrage

Lancer `projet/main.py` dans Pyto.
