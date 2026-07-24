# Changelog

## Phase 2 nettoyée — 25 juillet 2026

### Version précédente identifiable

`Scriptable/TCC_Budy_Phase_2_20260724_223240`

### Création

Création d’une nouvelle livraison horodatée complète et autonome.

### Nettoyage

- suppression de `config.example.json`, désormais inutile à l’exécution ;
- suppression de tous les fichiers `__init__.py` vides ;
- absence de dossiers vides ;
- exclusion des fichiers générés à l’exécution : base SQLite, journaux, caches et secrets ;
- documentation et manifeste reconstruits à partir des fichiers réellement livrés.

### Corrections intégrées

- création automatique de `config.json` ;
- mode `auto` : OpenAI avec clé, simulateur sans clé ;
- aucune dépendance d’exécution envers un fichier d’exemple ;
- clé et modèle OpenAI lus depuis `secrets.json` ;
- fermeture reposant sur la feuille native Pyto/iOS ;
- journalisation avec fermeture explicite du gestionnaire ;
- conservation de la persistance avant appel réseau et de l’idempotence par `request_id`.

### Fonctionnalités conservées

- conversations et messages SQLite ;
- historique, reprise et suppression ;
- simulateur local ;
- adaptateur OpenAI Responses ;
- contexte récent limité ;
- erreurs OpenAI lisibles ;
- tests automatiques.

### Migrations

Aucune nouvelle migration de schéma. La migration SQLite v1 est conservée sans modification.
