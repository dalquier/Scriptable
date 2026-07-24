# Changelog

## 2026-07-24 — Version 2.0.0

Création initiale du projet.

### Fichiers créés

- fichiers de contrôle et de documentation ;
- point d’entrée Pyto ;
- client OpenAI Responses API ;
- interface principale ;
- stockage local ;
- conversations ;
- RAG documentaire ;
- embeddings ;
- import multi-formats ;
- configuration par défaut ;
- règles d’exclusion Git.

### Fonctionnalités ajoutées

- conversation OpenAI ;
- recherche Web OpenAI ;
- affichage des sources Web ;
- affichage des sources documentaires ;
- index SQLite ;
- import local depuis l’app Fichiers ;
- réindexation incrémentale ;
- interface adaptée à Pyto et à l’iPhone ;
- persistance de l’historique.

### Corrections intégrées par rapport aux prototypes précédents

- historique assistant envoyé avec le type `output_text` ;
- suppression des paramètres de raisonnement incompatibles ;
- abandon de la sélection persistante d’un dossier Google Drive ;
- séparation claire entre interface, API, stockage et RAG ;
- saisie placée en haut afin de limiter le masquage par le clavier.

### Incompatibilités

Cette livraison remplace les anciens prototypes `AssistantIA` et leurs patchs successifs. Il est déconseillé de mélanger leurs modules.

### Migration

Les anciennes conversations JSON peuvent être conservées comme archive, mais elles ne sont pas importées automatiquement.
