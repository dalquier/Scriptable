# Widget et lancement par URL — Launcher Pro V7.1

## Fichiers concernés

- `projet/launcher_widget.py`
- `projet/LauncherProURL.py`
- `projet/core/url_scheme.py`

## Installer le widget

1. Ouvre `launcher_widget.py` dans Pyto.
2. Exécute-le une première fois afin que Pyto enregistre sa configuration.
3. Ajoute un widget Pyto sur l’écran d’accueil.
4. Choisis `launcher_widget.py` comme script du widget.
5. Les éléments favoris sont affichés en priorité. Sans favori, les premiers éléments de la bibliothèque sont utilisés.

Le petit widget ouvre Launcher Pro. Le widget moyen ou grand permet de lancer directement les éléments affichés.

## Créer une URL pour ouvrir Launcher Pro

Dans l’application, touche le bouton `URL` situé dans la barre supérieure. L’URL x-callback est copiée dans le presse-papiers.

Cette URL peut être utilisée dans :

- Safari ;
- Raccourcis iOS avec l’action `Ouvrir les URL` ;
- Scriptable ;
- Notes ;
- un tag NFC ou une automatisation personnelle.

## Créer une URL pour un script ou un projet

1. Touche `Modifier` sur la carte concernée.
2. Choisis `Copier URL`.
3. Colle ensuite l’URL dans l’application ou le raccourci souhaité.

L’identifiant interne reste stable même si le nom de l’élément est modifié.

## Modifier le nom

1. Touche `Modifier` sur la carte.
2. Modifie le premier champ.
3. Choisis `Enregistrer`.

Pour un projet, le troisième champ correspond au chemin relatif du script d’entrée.

## Limite iOS

Une URL x-callback peut ouvrir Pyto selon la configuration d’iOS. Le widget Pyto exécute son propre script et utilise le registre local de Launcher Pro.
