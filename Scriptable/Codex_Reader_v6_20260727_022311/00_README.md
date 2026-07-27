# Codex Reader v6

Application Pyto dédiée à l’extraction d’une question et de sa réponse depuis une page Codex/ChatGPT authentifiée.

## Expérience cible

1. La WebView ouvre ChatGPT avec son stockage de site normal.
2. La connexion effectuée avec Apple est réutilisée tant que Pyto conserve les cookies de la WebView.
3. L’utilisateur ouvre un lien `https://chatgpt.com/s/...`.
4. Il touche **Sélectionner** puis touche directement l’encadré gris de la dernière question.
5. Le moteur récupère la question choisie et l’ensemble de la réponse qui suit, jusqu’à la zone d’actions/évaluation (pouces, copier, etc.).
6. Une vue résultat affiche deux cartes distinctes, avec mise en forme et bouton Copier sous chaque carte.

## Limite de sécurité

Le script ne lit jamais les identifiants Apple et ne peut pas importer la session de l’app ChatGPT ou de Safari. La session est celle de la WebView Pyto. Elle est généralement conservée par le stockage web persistant de l’application, mais iOS ou Pyto peuvent l’effacer lors d’une réinstallation, d’un nettoyage des données ou d’un changement majeur de version.

## Point d’entrée

`projet/app.py`
