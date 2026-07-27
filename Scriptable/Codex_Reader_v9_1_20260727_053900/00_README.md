# Codex Reader v9.1

Correction du traitement des conversations Codex comportant plusieurs échanges.

## Correction principale

La v9 utilisait le premier marqueur « Exécution durant… » comme limite globale. Elle pouvait donc sélectionner systématiquement la première question et sa première réponse.

La v9.1 :

- détecte toutes les cartes de question dans l’ordre du DOM ;
- élimine les conteneurs parents redondants ;
- sélectionne explicitement la dernière carte ;
- détermine la borne de réponse propre à cette carte ;
- exclut tous les blocs appartenant aux échanges précédents ;
- indique le numéro de l’échange sélectionné dans le statut.

## Installation

Copier tous les fichiers du dossier `projet/` dans un même dossier Pyto, puis lancer `app.py`.
