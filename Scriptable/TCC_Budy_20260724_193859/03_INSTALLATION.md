# Installation

## Récupérer la livraison

Dans Working Copy, clonez ou ouvrez le dépôt `dalquier/Scriptable`, branche `main`, puis effectuez un pull.

Le dossier à récupérer est :

`Scriptable/TCC_Budy_20260724_193859/projet/`

## Copier dans iCloud Drive

1. Dans Working Copy, utilisez **Share / Open in Files** sur le dossier `projet`.
2. Copiez son contenu vers `iCloud Drive/Pyto/TCC Budy/`.
3. Vérifiez que le chemin final est `iCloud Drive/Pyto/TCC Budy/app.py`.

## Ouvrir dans Pyto

1. Ouvrez `app.py`.
2. Lancez le script.
3. Les dossiers locaux `data/` et `logs/` seront créés automatiquement.

## Dépendances

Aucune installation `pip` n’est requise. Le projet utilise les modules standards Python ainsi que `pyto_ui` et `mainthread` fournis par Pyto.

## Clés API

Aucune clé OpenAI n’est utilisée dans cette version. Ne placez jamais de clé dans le dépôt.

## Test d’installation

- créez une conversation ;
- envoyez un message ;
- revenez à l’historique ;
- rouvrez la conversation ;
- testez la suppression ;
- testez le bouton **Fermer** ;
- envoyez `/erreur` pour vérifier le repli.

## Diagnostic

- si l’interface ne s’ouvre pas, relancez Pyto ;
- si la base ne se crée pas, vérifiez les droits d’écriture du dossier ;
- si **Fermer** affiche seulement « fermeture », relevez la version de Pyto et le comportement exact ;
- n’effacez pas `data/tcc_budy.sqlite3` si vous souhaitez conserver les conversations.
