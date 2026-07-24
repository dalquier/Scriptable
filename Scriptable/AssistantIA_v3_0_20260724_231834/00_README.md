# AssistantIA v3.0

Généré le 24 juillet 2026 à 23:18, heure de Paris.

## Objectif

AssistantIA v3.0 est une application de conversation IA conçue pour Pyto sur iPhone et iPad. Elle utilise l’API OpenAI Responses, conserve les conversations dans SQLite et permet d’activer la recherche Web à la demande.

## Résumé fonctionnel

- interface graphique native `pyto_ui` ;
- conversations persistantes ;
- historique local SQLite ;
- création de nouvelles conversations ;
- recherche Web facultative ;
- gestion lisible des erreurs réseau et API ;
- architecture séparant interface, métier, stockage et client HTTP.

## Environnement cible

- iOS ou iPadOS ;
- Pyto ;
- Python 3.10 ou version compatible ;
- accès Internet ;
- clé API OpenAI valide.

## Dépendances

Aucune dépendance Python externe. Le projet utilise `pyto_ui`, `sqlite3`, `urllib`, `json`, `pathlib` et `threading`.

## Point d’entrée

`projet/main.py`

## Démarrage

1. récupérer le dossier depuis GitHub avec Working Copy ;
2. copier `projet/config_local.example.py` en `projet/config_local.py` ;
3. renseigner la clé OpenAI dans `config_local.py` ;
4. ouvrir `projet/main.py` dans Pyto ;
5. exécuter le script.

## Limitations connues

- la réponse n’est pas encore diffusée en streaming ;
- l’interface affiche une seule conversation à la fois ;
- l’indexation documentaire RAG n’est pas incluse dans cette version ;
- la disponibilité du modèle configuré dépend du compte API OpenAI.

## Actions manuelles restantes

- créer localement `config_local.py` ;
- y renseigner la clé OpenAI ;
- tester le modèle configuré avec le compte API utilisé.
