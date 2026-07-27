# Changelog

## 9.0.0-alpha.1 — Sprint 1

### Ajouté

- modèle métier `LauncherItem` et validation des invariants ;
- chemins de données, journaux et bibliothèque gérée ;
- registre JSON versionné avec écriture atomique et restauration transactionnelle ;
- journal technique rotatif et historique métier JSONL ;
- validation syntaxique, import durable des scripts et copie complète des projets ;
- détection automatique et sélection explicite des points d'entrée ;
- recherche, favoris, renommage et suppression ;
- moteur de lancement avec suivi du statut, de la durée et des erreurs ;
- restauration de `cwd`, `sys.path`, `sys.argv` et `__main__` après chaque exécution ;
- contrôleur central agnostique de Pyto ;
- point d'entrée console provisoire et suite de tests unitaires.

### Sécurité et robustesse

- exclusion des caches, métadonnées Git et artefacts compilés lors des imports ;
- rejet des chemins de lancement sortant du projet ;
- sérialisation des exécutions modifiant l'état global de Python ;
- nettoyage des copies incomplètes et compensation des mutations échouées.

### À venir — Sprint 2

- interface graphique Pyto ;
- sélecteurs natifs de fichiers et projets ;
- intégration visuelle complète avec le contrôleur du Sprint 1 ;
- validation sur appareils iOS/iPadOS.
