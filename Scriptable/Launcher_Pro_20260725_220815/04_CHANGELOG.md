# Changelog

## 5.0.0 — 2026-07-25

- création de l’architecture modulaire ;
- ajout de l’interface native Pyto ;
- ajout du sélecteur de fichiers iOS avec détection adaptative de l’API Pyto ;
- copie locale sécurisée des scripts importés ;
- registre JSON avec écriture atomique ;
- recherche, favoris, suppression et statistiques d’exécution ;
- moteur `runpy` avec restauration du contexte ;
- widget Pyto et URL x-callback ;
- script d’installation et documentation complète.

## Validation restante

Le code a été structuré et contrôlé statiquement, mais son comportement exact doit être validé sur l’iPhone cible, car certaines signatures de `pyto_ui`, `widgets` et `file_system` peuvent varier selon la build de Pyto installée. Le module de sélection essaie plusieurs noms d’API afin de réduire ce risque.
