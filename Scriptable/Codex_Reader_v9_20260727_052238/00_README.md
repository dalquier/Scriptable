# Codex Reader v9

Application Pyto destinée à extraire le dernier échange d’une tâche Codex ouverte dans une WebView authentifiée.

## Changement d’architecture

La v9 n’essaie plus de cloner une zone comprise entre deux nœuds DOM. Elle :

1. détecte la dernière carte de question ;
2. recherche tous les blocs sémantiques placés après cette carte ;
3. les classe dans l’ordre réel du document ;
4. retire les contrôles, doublons et descendants redondants ;
5. reconstruit une réponse HTML indépendante de l’interface Codex.

Cette méthode accepte notamment :

- titres et paragraphes ;
- listes ;
- blocs de code ;
- tableaux ;
- panneaux « Fichiers (n) » ;
- sections repliables ;
- réponses dont le compositeur et les pouces appartiennent à des branches DOM différentes.

## Parcours

- **Analyser** : détection automatique.
- **Choisir la question** : active un mode de sélection visuelle si l’automatique échoue.
- Touchez l’encadré gris, puis **Extraire le choix**.
- La vue finale contient une carte Question et une carte Réponse avec un bouton Copier sous chacune.

## Démarrage

Copier tous les fichiers de `projet/` dans un même dossier Pyto puis lancer `app.py`.
