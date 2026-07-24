# Pyto Project Exchange V5

- Généré le : 2026-07-24 19:40:03 Europe/Paris
- Dépôt : `dalquier/Scriptable`
- Branche : `main`
- Environnement cible : Pyto sur iOS
- Point d’entrée : `projet/main.py`

## Objectif

Fournir une version 5 de Pyto Project Exchange capable d’exporter et d’importer des projets complets au format Markdown, de préparer des livraisons multi-réponses, de générer un prompt de bascule pour les conversations existantes et de préparer les métadonnées nécessaires à une livraison GitHub.

## Résumé fonctionnel

- export récursif d’un projet ;
- import sécurisé d’un lot Markdown ;
- fragmentation automatique des fichiers volumineux ;
- index canonique ;
- contrôle SHA-256 ;
- prompt ChatGPT V5 intégré ;
- prompt séparé pour imposer le protocole dans une conversation existante ;
- interface Pyto simple et refermable.

## Dépendances

Aucune dépendance Python externe. Le script utilise uniquement la bibliothèque standard et les modules `pyto_ui`, `file_system` et `pasteboard` fournis par Pyto.

## Démarrage

1. Récupérer le dossier avec Working Copy.
2. Ouvrir `projet/main.py` dans Pyto.
3. Exécuter le script.
4. Choisir Exporter, Importer ou Copier le prompt.

## Limitations connues

- Les très gros projets produisent de nombreuses parties Markdown.
- Les métadonnées GitHub sont générées mais l’écriture GitHub reste réalisée par ChatGPT ou un connecteur externe.
- Les fichiers binaires sont encodés en Base64.

## Actions manuelles restantes

- Vérifier que Working Copy expose bien le dépôt dans l’app Fichiers.
- Autoriser Pyto à accéder au dossier du projet lors du sélecteur iOS.
