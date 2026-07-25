# Installation de Launcher Pro V5

## 1. Récupération

Télécharge le dossier `projet` depuis GitHub puis place-le dans un emplacement accessible à Pyto.

Emplacement conseillé :

```text
Sur mon iPhone/Pyto/LauncherProV5/
```

Le fichier `LauncherPro.py` et les modules `launcher_*.py` doivent rester ensemble.

## 2. Initialisation

Dans Pyto :

1. ouvre `install.py` ;
2. exécute-le ;
3. vérifie que le message `Installation prête` apparaît ;
4. ouvre et exécute `LauncherPro.py`.

## 3. Ajouter un script

Dans l’application :

1. touche `＋ Ajouter` ;
2. sélectionne un fichier `.py` dans Fichiers ;
3. saisis un nom ;
4. valide.

Le script est copié dans `data/scripts/`. Le lanceur travaille ensuite sur cette copie afin de conserver un accès fiable après redémarrage.

## 4. Widget

Ajoute `launcher_widget.py` comme widget Pyto. Le widget affiche un bouton central et ouvre le lanceur via une URL x-callback utilisant `runpy`.

Selon la configuration de Pyto/iOS, le widget peut ouvrir Pyto avant d’afficher Launcher Pro : iOS ne permet pas à un script arbitraire d’afficher durablement une interface native sans que l’application hôte soit active.

## 5. Raccourci iOS recommandé

Dans Raccourcis :

1. ajoute l’action Pyto `Run Script` ;
2. sélectionne `LauncherPro.py` ;
3. active `Show Console` uniquement si tu veux voir la console ;
4. ajoute le raccourci à l’écran d’accueil ou à un widget.

## 6. Limites connues

- Les fournisseurs comme Google Drive peuvent exposer des fichiers temporaires ou non persistants.
- Launcher Pro copie donc les scripts importés dans son dossier local.
- Les interfaces créées par un script lancé restent soumises au cycle de vie de Pyto.
- Un script qui appelle `sys.exit()` ou modifie fortement `sys.path` peut perturber sa propre exécution ; le lanceur restaure néanmoins le répertoire courant et `sys.argv`.
