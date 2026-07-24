# TCC Budy — Phase 2

Compagnon conversationnel local-first sous Pyto. Cette version ajoute un fournisseur OpenAI optionnel via l'API Responses, tout en conservant le simulateur local.

Le bouton HTML « Fermer » a été supprimé. La fermeture s'effectue par la feuille native Pyto/iOS, via son contrôle natif ou un glissement vers le bas. Cette rupture évite les appels UIKit non fiables depuis une requête HTTP issue de la WebView.

Point d'entrée : `app.py`.
