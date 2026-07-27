# Codex Reader v10

Application Pyto pour ouvrir une page ChatGPT/Codex authentifiée, détecter le dernier échange et copier la question ou la réponse complète sans champ éditable caché.

## Principes v10

- extraction par bornes DOM entre la dernière question et la question suivante ou le compositeur ;
- aucune limite volontaire de longueur ;
- copie depuis le texte complet extrait, indépendante de l'affichage HTML ;
- plusieurs échanges pris en charge ;
- le bouton Nouvelle analyse efface l'URL mémorisée et le champ visible ;
- copie sans focus sur un champ de saisie, donc sans ouverture du clavier iOS.

## Lancement

Copier le dossier `projet/` dans Pyto puis lancer `app.py`.
