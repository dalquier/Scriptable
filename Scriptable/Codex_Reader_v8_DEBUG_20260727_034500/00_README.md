# Codex Reader v8 DEBUG

Version de diagnostic et de contournement pour Pyto.

## Pourquoi l’analyse échoue

La page Codex affiche bien la question, la réponse et les pouces, mais les icônes peuvent être rendues sans texte, sans `aria-label` et sans attribut sémantique stable. L’algorithme automatique ne trouve alors pas la borne basse de la réponse et renvoie `Bloc de réponse introuvable`.

## Cette version ajoute

- diagnostic DOM complet ;
- enregistrement local du HTML et des candidats détectés ;
- extraction automatique améliorée ;
- mode manuel à deux touches : toucher l’encadré gris, puis toucher la zone des pouces ;
- écran de résultat avec deux cartes et boutons Copier.

## Point d’entrée

`projet/app.py`

## Fichiers de diagnostic

`Documents/CodexReaderDebug/Diagnostics/`
