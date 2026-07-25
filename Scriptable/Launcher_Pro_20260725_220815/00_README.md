# Launcher Pro V5

Launcher Pro est un lanceur de scripts Python conçu pour Pyto sur iPhone et iPad.

## Fonctionnalités livrées

- interface native Pyto avec liste de scripts ;
- ajout d’un fichier `.py` depuis le sélecteur iOS ;
- copie sécurisée du script importé dans la bibliothèque locale du lanceur ;
- nom personnalisable ;
- favoris ;
- recherche ;
- lancement direct ;
- suppression ;
- historique minimal d’exécution ;
- persistance JSON ;
- point d’entrée URL/x-callback documenté ;
- widget Pyto servant de raccourci visuel.

## Installation rapide

1. Télécharge le dossier `projet` dans Pyto.
2. Place-le dans un dossier accessible à Pyto, idéalement `Sur mon iPhone/Pyto/LauncherProV5`.
3. Exécute `install.py` une fois.
4. Exécute ensuite `LauncherPro.py`.

Consulte `03_INSTALLATION.md` pour les détails et limites iOS.

## Principe important

Lors de l’ajout d’un script externe, Launcher Pro en conserve une copie dans son propre dossier `data/scripts/`. Cette stratégie évite de dépendre durablement d’un accès iOS fragile à un fichier externe. Le chemin source est néanmoins mémorisé à titre informatif.

## Compatibilité

Cible : Pyto 19.x, Python 3.10+, iOS/iPadOS récents.
