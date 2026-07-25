# Launcher Pro V7

Launcher Pro V7 est un lanceur professionnel pour Pyto sur iPhone et iPad.

Il prend en charge deux types d’éléments :

- **Script autonome** : un seul fichier `.py`, copié dans la bibliothèque locale de Launcher Pro ;
- **Projet Pyto** : un dossier complet avec un script d’entrée (`main.py`, `bootstrap.py`, etc.), lancé avec le dossier racine ajouté à `sys.path`.

## Fonctionnalités

- interface native Pyto en feuille, non plein écran ;
- ajout de scripts autonomes ;
- ajout de projets complets ;
- choix et modification du nom ;
- catégorie, favori et icône ;
- modification du point d’entrée d’un projet ;
- recherche ;
- historique d’exécution ;
- sortie standard et erreurs affichées ;
- suppression ;
- persistance JSON ;
- sauvegarde automatique du registre ;
- bouton Fermer.

## Démarrage

1. Télécharge le dossier `projet` en conservant son arborescence.
2. Place-le dans Pyto.
3. Exécute `install.py` une fois.
4. Exécute `LauncherPro.py`.

Consulte `03_INSTALLATION.md` pour les détails.