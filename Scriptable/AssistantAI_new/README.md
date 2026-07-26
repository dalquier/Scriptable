# AssistantAI new

Nouvelle copie de travail issue du projet `AssistantIA_v5` stabilisé par Codex.

Objectifs de cette version :

- repartir des fichiers corrigés de la version Codex ;
- aligner la version applicative et le manifeste ;
- utiliser la branche `main` comme référence canonique ;
- conserver la compatibilité Pyto/iPhone ;
- ne jamais versionner `config_local.py` ni les bases SQLite.

## Installation

1. Copier le contenu de `Scriptable/AssistantIA_v5/` dans ce dossier si tous les fichiers ne sont pas encore présents.
2. Dupliquer `projet/config_local.example.py` en `projet/config_local.py`.
3. Ajouter la clé OpenAI uniquement dans `config_local.py`.
4. Lancer `projet/diagnostic.py`.
5. Lancer `projet/main.py`.

## Corrections spécifiques prévues

- `APP_VERSION` alignée sur `5.0.1` ;
- manifeste aligné sur la branche `main` ;
- prise en charge moderne de `PresentationMode.FULLSCREEN` avec repli compatible ;
- compatibilité explicite avec l’absence de `ui.delay` dans Pyto ;
- validation manuelle obligatoire sur iPhone avant fusion finale.
