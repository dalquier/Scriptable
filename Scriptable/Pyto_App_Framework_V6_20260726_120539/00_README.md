# Pyto App Framework V6

Framework compact pour créer dans Pyto une interface proche d’une application iPhone.

## Objectifs

- interface WebView plein écran ;
- navigation inférieure type application iOS ;
- stockage JSON persistant ;
- pont d’actions JavaScript → Python ;
- services natifs Pyto optionnels ;
- architecture simple, lisible et réutilisable ;
- compatibilité Pyto prioritaire.

## Démarrage

Ouvrir puis exécuter :

`projet/main.py`

Ne pas déplacer `main.py` seul : il dépend des autres fichiers et du dossier `ui`.

## Principe

- Python gère l’état, les fichiers et les actions.
- HTML/CSS/JavaScript gèrent l’interface.
- `pyto_ui.WebView` héberge l’application.
- Les commandes sont envoyées via des URL internes `pytoapp://...`.

## Limites

Cette V6 est une base d’application personnelle exécutée dans Pyto. Elle ne génère pas un fichier IPA et ne devient pas une application App Store autonome.
