# Codex Reader v8.4

Correction du cas « Question détectée mais vide ».

## Cause

Le bon encadré était trouvé, mais le nettoyage supprimait les descendants interactifs qui contenaient réellement le texte.

## Correction

- capture du texte brut de la question avant tout clic ;
- capture d’un HTML de secours avant nettoyage ;
- clic d’expansion après capture ;
- extraction de la réponse par `Range` DOM entre la question et la barre des pouces ;
- nettoyage sélectif qui ne supprime plus le contenu de la question ;
- reconstruction sûre du HTML affiché.

Copier tout le dossier `projet/` dans Pyto et lancer `app.py`.
