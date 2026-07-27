# Codex Reader v7

Application Pyto simplifiée pour ouvrir un lien Codex authentifié, vérifier la connexion, analyser automatiquement la dernière question et sa réponse, puis afficher deux cartes copiables dans une interface de type iPhone.

## Parcours

1. Le script vérifie si la session ChatGPT est active.
2. Si nécessaire, il affiche l’écran de connexion Apple.
3. L’utilisateur colle le lien Codex dans le champ principal.
4. Le script charge la page et analyse automatiquement la dernière question et la dernière réponse.
5. Une vue de résultat affiche deux cartes : Question et Réponse.
6. Un bouton sous chaque carte copie le contenu intégral.

## Point d’entrée

`projet/app.py`

## Limite connue

La session dépend du stockage web persistant de la WebView Pyto. iOS ou Pyto peuvent exceptionnellement purger les cookies. Le script ne récupère jamais les identifiants Apple et ne lit pas la session de l’application ChatGPT native.