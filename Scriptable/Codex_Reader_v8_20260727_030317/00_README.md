# Codex Reader v8

Application Pyto dédiée à l’extraction du dernier échange d’un lien ChatGPT/Codex partagé.

## Parcours

1. Vérification de la session ChatGPT dans la WebView.
2. Connexion avec Apple uniquement si nécessaire.
3. Collage du lien `https://chatgpt.com/s/...`.
4. Chargement du lien.
5. Détection automatique de la dernière question et de la réponse associée.
6. Affichage dans deux cartes modernes avec boutons de copie.

## Point d’entrée

`projet/app.py`

## Compatibilité confirmée

La v8 utilise directement `pyto_ui.WebView.evaluate_js`, méthode disponible sur l’installation Pyto de Damien.

## Limite

La mémorisation de la connexion dépend du stockage persistant des cookies de la WebView Pyto. Le script ne récupère ni les identifiants Apple ni la session de l’application ChatGPT ou de Safari.
