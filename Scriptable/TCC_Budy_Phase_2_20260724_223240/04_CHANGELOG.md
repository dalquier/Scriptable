# Changelog

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
- le fournisseur reçoit désormais une liste de messages et non un texte isolé ;
- `config.json` et `secrets.json` doivent être créés localement.
