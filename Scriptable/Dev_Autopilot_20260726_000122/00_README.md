# Dev Autopilot

Dev Autopilot est un orchestrateur Python simple qui poursuit automatiquement un développement avec l’API OpenAI et écrit les fichiers produits dans GitHub.

## Limite importante

Cette première version ne peut pas injecter automatiquement le mot `Continue` dans une discussion déjà ouverte dans l’application ChatGPT. L’API OpenAI et l’application ChatGPT sont deux environnements séparés. Le projet utilise donc un **transfert de contexte** : vous copiez une fois le contexte utile de la discussion en cours dans `projet/handoff.md`, puis l’orchestrateur poursuit le travail de façon autonome via l’API OpenAI.

## Fonctionnement

1. Lire `projet/handoff.example.md`.
2. Le copier en `projet/handoff.md`.
3. Y coller le contexte et la mission issus de la discussion ChatGPT en cours.
4. Définir localement les variables d’environnement :
   - `OPENAI_API_KEY`
   - `GITHUB_TOKEN`
   - éventuellement `OPENAI_MODEL`, `GITHUB_REPOSITORY`, `GITHUB_BRANCH` et `TARGET_ROOT`
5. Lancer `projet/main.py` dans Pyto ou Python 3.10+.
6. Le modèle renvoie un objet JSON contenant un statut, un résumé et des fichiers complets.
7. Les fichiers sont créés ou remplacés dans GitHub.
8. Tant que le statut est `in_progress`, le script envoie automatiquement `Continue`.
9. Le script s’arrête lorsque le statut est `complete`, `blocked`, ou lorsque le nombre maximal d’itérations est atteint.

## Dépôt par défaut

- Dépôt : `dalquier/Scriptable`
- Branche : `main`
- Racine des fichiers générés : `Scriptable/Generated_Project`

Ces valeurs peuvent être remplacées par des variables d’environnement.

## Sécurité

Ne placez jamais de clé API ou de jeton GitHub dans les fichiers suivis par Git. Le projet lit uniquement les secrets depuis les variables d’environnement.

## Point d’entrée

`projet/main.py`

## État de cette livraison

Première version fonctionnelle minimale : boucle OpenAI, continuation automatique, état persistant local et écriture GitHub.
