# État du projet

Version : Draft v0.1 autonome

Statut : prototype exécutable créé

Branche de travail : `feature/developeros-sprint0`

## Réalisé

- Boucle autonome minimale dans `draft_v01.py`.
- Appel direct à l’API OpenAI sans dépendance externe.
- État persistant dans `state.json`.
- Reprise après interruption en relançant le script.
- Journalisation dans `developeros.log`.
- Tâche de départ dans `task.txt`.
- Relance automatique tant que le statut vaut `continue`.
- Compatibilité de secours avec une réponse se terminant par `En cours`.
- Arrêt sur `done`, `blocked`, erreur ou limite d’itérations.
- Compatible Python 3.10 / Pyto.

## Limites actuelles

- Le prototype raisonne et enchaîne les appels, mais ne modifie pas encore lui-même les fichiers du dépôt.
- Il ne crée pas encore de commits GitHub.
- Il ne lance pas encore les tests.
- La clé API doit être fournie dans `OPENAI_API_KEY`.
- Le modèle utilisé par défaut est `gpt-5.6`, modifiable avec `OPENAI_MODEL`.

## Point de reprise exact

La prochaine conversation doit commencer par lire ce fichier puis implémenter, dans cet ordre :

1. un outil local très simple permettant à l’agent de lire et modifier les fichiers du dossier `DeveloperOS` ;
2. une validation des chemins pour empêcher toute sortie du dossier du projet ;
3. un lanceur de tests Python ;
4. une boucle correction → nouveau test ;
5. seulement ensuite, l’intégration GitHub pour créer des commits.

## Fichiers principaux

- `draft_v01.py` : moteur autonome minimal.
- `task.txt` : mission courante.
- `state.json` : créé automatiquement au premier lancement.
- `developeros.log` : créé automatiquement.
- `config.example.json` : variables de configuration disponibles.

## Commande de lancement

```bash
python draft_v01.py
```

Dans Pyto, ouvrir `draft_v01.py`, renseigner la variable d’environnement `OPENAI_API_KEY`, puis exécuter le script.
