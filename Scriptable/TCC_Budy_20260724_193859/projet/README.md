# TCC Budy — Sprint 0.2 v0.8

Prototype local Pyto comprenant :

- WebView avec Aujourd’hui, Historique et Conversation ;
- SQLite et migrations ;
- création, reprise et suppression des conversations ;
- fournisseur local simulé ;
- serveur HTTP local `127.0.0.1` pour le pont JavaScript–Python ;
- bouton **Fermer** intégré dans la page et exécuté sur le thread principal Pyto.

## Lancement

Ouvrir puis exécuter `app.py` dans Pyto.

## Test d’erreur

Envoyer `/erreur` pour simuler un échec du fournisseur et vérifier le bouton Réessayer.

Aucun appel OpenAI n’est effectué dans cette version.
