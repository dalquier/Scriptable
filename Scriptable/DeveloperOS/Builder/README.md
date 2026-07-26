# DeveloperOS Builder v0.1

DeveloperOS Builder reprend le projet existant dans `Scriptable/DeveloperOS/` et poursuit sa construction par itérations contrôlées.

## Objectif

Le Builder doit être capable de :

- analyser l'existant ;
- indexer les fichiers du projet ;
- déterminer la prochaine étape utile ;
- demander à OpenAI une proposition de modification structurée ;
- écrire les changements dans un espace de travail local ;
- valider la syntaxe Python ;
- sauvegarder son état pour reprendre après interruption.

La v0.1 ne pousse pas encore automatiquement vers GitHub. Elle prépare des changements locaux sûrs et traçables.

## Démarrage

1. Copier `settings.example.json` vers `settings.json`.
2. Définir `OPENAI_API_KEY` dans l'environnement Pyto.
3. Lancer `builder.py` depuis ce dossier.

## Sécurité

- les fichiers hors du dossier DeveloperOS sont ignorés ;
- les chemins absolus et `..` sont refusés ;
- les suppressions automatiques sont interdites en v0.1 ;
- chaque modification est sauvegardée dans `Builder/backups/` avant écriture.
