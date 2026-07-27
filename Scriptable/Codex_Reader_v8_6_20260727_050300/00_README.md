# Codex Reader v8.6

Correction du cas où la réponse contient des tableaux, panneaux repliables ou sections imbriquées.

La v8.6 n’utilise plus un simple DOM Range comme méthode principale. Elle recherche le plus petit ancêtre commun de la question et de la borne basse, puis collecte les blocs frères compris entre les deux.

## Installation

Copier tous les fichiers du dossier `projet/` dans un même dossier Pyto et lancer `app.py`.
