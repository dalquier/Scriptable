# GitHub Content Manager V6.2

Gestionnaire GitHub pour Pyto, conçu pour fonctionner sans `WebView`, sans `View.present()` et sans `TableView.reload()`.

## Réglages initiaux

- Dépôt : `dalquier/Scriptable`
- Branche : `main`
- Dossier racine : `Scriptable`
- Jeton : vide

La lecture du dépôt public fonctionne sans jeton. Un jeton GitHub disposant de `Contents: Read and write` est nécessaire pour créer, modifier, renommer, déplacer ou supprimer des fichiers.

## Lancement

Ouvrir `projet/main.py` dans Pyto et l’exécuter.

## Affichage des fichiers

La liste est affichée dans une zone texte numérotée. Saisir le numéro d’un élément dans le champ `N°` puis appuyer sur `Sélectionner`. Un dossier est ouvert immédiatement ; un fichier est chargé dans l’éditeur.