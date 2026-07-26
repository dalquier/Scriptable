# AssistantIA v5

Application iPhone pour **Pyto**, sans dépendance pip, utilisant l'API OpenAI Responses et SQLite.

## Fonctions

- conversation persistante et restauration de la dernière session;
- appels réseau hors du thread d'interface, verrou anti-double envoi;
- contexte multi-message et nouveau fil de conversation;
- recherche Web optionnelle (`web_search`) et collecte des citations URL disponibles;
- erreurs HTTP, réseau, timeout, JSON et réponse vide présentées sans exposer la clé;
- interface adaptative clair/sombre, repli de zone sûre et compositeur placé au-dessus du clavier.

## Lancement

1. Copier `projet/config_local.example.py` vers `projet/config_local.py`.
2. Remplacer la valeur fictive par la clé API (ce fichier est ignoré par Git).
3. Ajuster `MODEL` dans `projet/config.py` selon les modèles autorisés pour le compte.
4. Exécuter `projet/diagnostic.py`, puis `projet/main.py` dans Pyto.

En cas d'échec API, le message utilisateur reste enregistré pour permettre une nouvelle tentative; aucune fausse réponse assistant n'est créée. Voir `TESTS_IPHONE.md` pour la recette complète.
