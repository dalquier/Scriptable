# TCC Budy — Phase 2

Généré le 25 juillet 2026 à 01:14:27 (Europe/Paris).

## Objectif

Fournir une version nettoyée et autonome de TCC Budy pour Pyto sur iPhone, avec conversation locale persistante, fournisseur simulé, fournisseur OpenAI optionnel et configuration automatique.

## Résumé fonctionnel

- conversations persistées dans SQLite ;
- historique, reprise et suppression ;
- fournisseur local de simulation ;
- fournisseur OpenAI via l’API Responses ;
- configuration `auto`, `simulator` ou `openai` ;
- création automatique de `config.json` au premier lancement ;
- lecture facultative de `secrets.json` ;
- fermeture par la feuille native Pyto/iOS ;
- tests automatiques du socle et du parseur OpenAI.

## Environnement cible

- iPhone ou iPad ;
- Pyto ;
- Python 3 fourni par Pyto ;
- connexion Internet uniquement pour OpenAI.

## Dépendances

Aucune dépendance `pip`. Le projet utilise la bibliothèque standard et `pyto_ui` fourni par Pyto.

## Point d’entrée

`projet/app.py`

## Démarrage

1. Récupérer le dossier avec Working Copy.
2. Ouvrir `projet/run_tests.py` dans Pyto et lancer les tests.
3. Ouvrir `projet/app.py` et l’exécuter.
4. Sans `secrets.json`, le mode `auto` utilise le simulateur.
5. Pour OpenAI, créer localement `projet/secrets.json` avec la clé API.

## Limitations connues

- pas de mémoire durable validée ;
- pas de RAG Google Drive ;
- pas de recherche Web ;
- pas de voix temps réel ;
- pas de séances TCC structurées complètes ;
- la fermeture repose sur le contrôle natif de la feuille Pyto/iOS.

## Actions manuelles restantes

- créer localement `secrets.json` pour OpenAI ;
- ne jamais committer ce fichier ;
- valider la fermeture native sur l’iPhone réel ;
- vérifier la disponibilité et le tarif du modèle OpenAI configuré avant usage.
