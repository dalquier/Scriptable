# Codex Reader v8.3

Version reconstruite à partir du diagnostic DOM réel de Codex sur iPhone/Pyto.

## Principe d’extraction

1. Repère le dernier bouton `Donner un avis positif` ou `Donner un avis négatif`.
2. Repère avant lui le dernier grand `DIV[role="button"]` arrondi : l’encadré gris de la question.
3. Clique sur cet encadré pour demander son expansion.
4. Crée un `Range` DOM allant juste après la question jusqu’à la barre des pouces.
5. Nettoie et normalise ce fragment pour former la réponse.
6. Affiche deux cartes propres avec un bouton Copier sous chacune.

## Installation

Copier tous les fichiers du dossier `projet/` dans un même dossier Pyto, puis lancer `app.py`.

La session ChatGPT repose sur les cookies de la WebView Pyto. Aucun identifiant Apple n’est enregistré par le script.
