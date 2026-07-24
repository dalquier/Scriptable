# Changelog

## Correctif de configuration autonome — 25 juillet 2026

### Fichiers modifiés

- `projet/tcc_budy/support/config.py`
- `projet/config.example.json`
- `03_INSTALLATION.md`
- `04_CHANGELOG.md`

### Corrections

- suppression de la dépendance d’exécution à `config.example.json` ;
- création automatique de `config.json` au premier lancement ;
- démarrage automatique avec le simulateur lorsqu’aucune clé OpenAI n’est présente ;
- activation automatique d’OpenAI lorsqu’une clé valide existe dans `secrets.json` ;
- prise en charge de `OPENAI_MODEL` dans `secrets.json` ;
- validation renforcée du contenu JSON et messages d’erreur plus précis ;
- conservation de `config.example.json` comme documentation uniquement.

### Compatibilité

- aucun changement du schéma SQLite ;
- aucune migration de données ;
- les valeurs `provider: simulator` et `provider: openai` restent acceptées ;
- la nouvelle valeur recommandée est `provider: auto`.

## Phase 2 — 24 juillet 2026

### Version précédente identifiable

`Scriptable/TCC_Budy_20260724_193859`

### Fichiers créés

- `config.example.json`
- `tcc_budy/support/config.py`
- `tcc_budy/providers/factory.py`
- `tcc_budy/providers/openai_provider.py`
- fichiers `__init__.py` nécessaires aux imports et aux tests

### Fichiers réécrits

Tous les scripts du projet ont été recréés dans cette livraison horodatée.

### Fonctionnalités ajoutées

- fournisseur OpenAI via l’API Responses ;
- sélection `simulator` ou `openai` par configuration ;
- clé API séparée dans `secrets.json` ;
- contexte conversationnel local limité ;
- `store: false` par défaut pour les réponses distantes ;
- affichage du fournisseur et du modèle actifs ;
- tests du parseur de réponse OpenAI.

### Corrections

- suppression du bouton HTML de fermeture non fiable ;
- présentation native `SHEET` utilisée comme mécanisme de fermeture ;
- maintien de la persistance avant appel fournisseur ;
- fermeture explicite des fichiers de log ;
- constantes Pyto modernes uniquement.

### Incompatibilités et migrations

- aucune migration de schéma supplémentaire ; le schéma SQLite v1 est conservé ;
- le fournisseur reçoit désormais une liste de messages et non un texte isolé.
