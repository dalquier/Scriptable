# TCC Budy — Phase 2

- **Généré le :** 24 juillet 2026 à 22:32 (Europe/Paris)
- **Objectif :** lancer la Phase 2 avec un fournisseur OpenAI optionnel tout en conservant le socle local SQLite et le simulateur.
- **Environnement cible :** Pyto sur iPhone/iPad, iOS, Python 3.10+ compatible Pyto.
- **Dépendances :** bibliothèque standard Python et `pyto_ui` fourni par Pyto.
- **Point d’entrée :** `projet/app.py`.

## Résumé fonctionnel

Cette version réécrit le projet complet autour d’un fournisseur abstrait. Le simulateur reste disponible pour les tests hors ligne. Le fournisseur OpenAI utilise l’API Responses par HTTP natif, avec historique local limité, persistance SQLite avant appel distant, idempotence et reprise après erreur.

## Fermeture de l’interface

Le bouton HTML « Fermer » a été supprimé. La fermeture est désormais confiée à la présentation native `SHEET` de Pyto/iOS : contrôle natif de la feuille ou glissement vers le bas. Cette solution en rupture évite les appels `close()`/`dismiss()` non fiables depuis le thread HTTP de la WebView.

## Démarrage

1. Copier `projet/config.example.json` vers `projet/config.json`.
2. Conserver `provider: simulator` pour un test sans API.
3. Pour OpenAI, créer `projet/secrets.json` avec la clé API, puis définir `provider: openai`.
4. Lancer `projet/run_tests.py`.
5. Lancer `projet/app.py`.

## Limitations connues

- La fermeture native doit être validée sur la version exacte de Pyto installée.
- La Phase 2 ne comprend pas encore la mémoire durable validée, les synthèses structurées, le RAG, la voix ou les embeddings.
- L’API OpenAI est facturée séparément de ChatGPT.

## Actions manuelles restantes

- Créer localement `config.json` et éventuellement `secrets.json`.
- Renseigner une clé API réelle uniquement dans `secrets.json`, jamais dans GitHub.
- Tester la fermeture native et les appels OpenAI sur l’iPhone réel.
