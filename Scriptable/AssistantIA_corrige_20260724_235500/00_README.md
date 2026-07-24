# AssistantIA corrigé

Version 3.1.0 reconstruite à partir du projet transmis par l'utilisateur.

## Objectif

Fournir une application de conversation native Pyto utilisant l'API OpenAI Responses, avec historique SQLite local et recherche Web activable.

## Environnement

- iPhone ou iPad
- Pyto
- Python fourni par Pyto
- accès Internet
- clé API OpenAI

## Point d'entrée

`projet/main.py`

## Démarrage

1. Copier `projet/config_local.example.py` vers `projet/config_local.py`.
2. Remplacer la valeur factice par votre clé OpenAI.
3. Exécuter `projet/diagnostic.py`.
4. Exécuter `projet/main.py`.

## Corrections principales

- format `input` de l'API Responses corrigé avec des contenus `input_text` ;
- base SQLite vierge reconstruite automatiquement au lieu de livrer une base existante ;
- fichier secret réel supprimé de la livraison ;
- compatibilité renforcée avec les constructeurs `pyto_ui` ;
- mode de présentation Pyto plus robuste ;
- diagnostic local fourni ;
- gestion des erreurs réseau et des délais améliorée.

## Limitations

- la disponibilité du modèle dépend de votre compte API ;
- la recherche Web peut dépendre du type d'outil accepté par la version courante de l'API ;
- l'interface est conçue pour Pyto, pas pour Scriptable.
