# Changelog

## Correctif boutons — 25 juillet 2026, 21:12

### Cause identifiée

`ui.show_view()` retourne immédiatement dans certaines versions de Pyto. Le bloc `finally` de `webview.py` arrêtait alors le serveur HTTP local juste après l’affichage de l’interface. La page restait visible, mais les boutons ne pouvaient plus appeler `/api`.

### Correction

- maintien explicite du serveur local avec `threading.Event()` tant que la vue est ouverte ;
- libération de l’attente lors de l’appui sur le bouton natif `Fermer` ;
- fermeture prioritaire par `sender.superview.superview.close()` ;
- arrêt propre du serveur seulement après la fermeture ;
- repositionnement adaptatif du bouton `Fermer` lors du redimensionnement.

### Commit du correctif

`1233c47f4b0924b9797f7df477881bb6929ce4f9`

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
