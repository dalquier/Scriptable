# Changelog

## Phase 2.1 — 25 juillet 2026

Version précédente : `Scriptable/TCC_Budy_Phase_2_20260725_011427`.

### Fonctionnalités ajoutées

- nouvel accueil plus équilibré ;
- cartes de démarrage rapide ;
- hiérarchie visuelle revue ;
- navigation Aujourd’hui / Historique ;
- en-tête natif Pyto ;
- bouton natif Fermer ;
- fermeture prioritaire par `sender.superview.superview.close()` ;
- stratégies de repli compatibles avec différentes versions de Pyto.

### Corrections

- suppression de la fermeture via JavaScript et HTTP ;
- meilleur dimensionnement de la WebView sous l’en-tête natif ;
- composition mieux positionnée au-dessus du clavier ;
- marges, densité et largeur des conversations harmonisées.

### Fichiers supprimés

Aucun fichier vide, cache, journal, base SQLite, secret ou fichier d’exemple n’est livré.

### Migration

Le schéma SQLite v1 est conservé. Aucune migration de données supplémentaire.