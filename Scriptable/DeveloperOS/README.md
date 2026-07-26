# DeveloperOS Draft v0.1

Draft autonome minimale pour Pyto/Python 3.10.

## Principe

Le moteur charge une mission depuis `task.txt`, appelle l'API OpenAI, sauvegarde chaque réponse dans `state.json` et relance automatiquement tant que le statut retourné vaut `continue` ou que la réponse se termine par `En cours`.

## Installation rapide

1. Ouvrir ce dossier dans Pyto.
2. Copier `config.example.json` vers `config.json` si des réglages différents sont nécessaires.
3. Définir la variable d'environnement `OPENAI_API_KEY`.
4. Lancer `main.py`.

## Fichiers

- `main.py` : point d'entrée.
- `executor.py` : boucle autonome et appel OpenAI.
- `planner.py` : création du prompt.
- `state.py` : reprise automatique via `state.json`.
- `config.py` : configuration.
- `task.txt` : mission active.

## Limites de cette Draft

Elle sait poursuivre une conversation API de manière autonome et mémoriser son état. Elle ne modifie pas encore le code du projet, ne lance pas encore les tests et ne crée pas de commits GitHub.
