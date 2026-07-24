# AssistantIA Studio

AssistantIA Studio est une plateforme IA modulaire destinée à fonctionner principalement sous Pyto sur iPhone et iPad.

## Objectif

Fournir un socle réutilisable pour créer des assistants spécialisés avec :

- une interface de conversation moderne ;
- l’API OpenAI Responses ;
- la recherche Web ;
- un historique local SQLite ;
- une mémoire persistante ;
- un moteur RAG documentaire local ;
- une architecture modulaire et extensible.

## État de la livraison

Livraison en cours, réalisée progressivement et directement dans GitHub.

## Démarrage prévu

Le point d’entrée sera :

```text
projet/main.py
```

La clé OpenAI ne devra jamais être enregistrée dans GitHub. Elle sera fournie localement dans Pyto au moyen d’un fichier de configuration privé ignoré par Git.

## Environnement cible

- iPhone ou iPad
- Pyto
- Python 3.10 ou version compatible fournie par Pyto
- accès réseau pour l’API OpenAI

## Licence

Projet privé de travail. Aucun droit de redistribution n’est accordé par défaut.
