# Installation dans Pyto

1. Récupérer `Scriptable/AssistantIA_v5` avec Working Copy ou Git.
2. Ouvrir le dossier `projet` depuis un emplacement local/iCloud accessible à Pyto.
3. Dupliquer `config_local.example.py` en `config_local.py` et remplacer uniquement la valeur fictive.
4. Vérifier dans `config.py` que `MODEL` est autorisé pour le compte; il est volontairement modifiable sans toucher au client.
5. Exécuter `diagnostic.py` (résolution DNS optionnelle, aucun appel OpenAI payant).
6. Exécuter `main.py`.

La base est créée dans `projet/database/assistantia_v5.sqlite3`. La clé, les bases, caches Python et métadonnées macOS sont ignorés par Git. Aucune dépendance pip n'est requise.
