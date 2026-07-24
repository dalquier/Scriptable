# Prompt principal — PYTO_PROJECT_EXCHANGE 5.0

Tu vas recevoir un projet logiciel au format `PYTO_PROJECT_EXCHANGE` version `5.0`.

## Règle absolue

Le champ JSON `part_count` de `00_INDEX.md` est l’unique source de vérité concernant le nombre de parties reçues. N’invente jamais de partie supplémentaire.

## Réception

1. Lis toujours `00_INDEX.md` en premier.
2. Attends exactement `PART_001.md` à `PART_NNN.md`, où N est la valeur de `part_count`.
3. Si `part_count` vaut 1, `PART_001.md` est la dernière partie.
4. Si la mission est déjà fournie avec la dernière partie, commence immédiatement le travail.
5. Lorsque toutes les parties annoncées sont présentes, il est interdit d’affirmer que le projet est incomplet.

## Modification

- Reconstitue tous les fichiers à partir des fragments ordonnés par `chunk_index`.
- Tu peux ajouter, modifier, renommer, déplacer ou supprimer des fichiers.
- Renvoie toujours le projet final complet, jamais seulement un patch, un diff, un résumé ou des extraits.
- Mets à jour le manifeste, `file_count`, `part_count`, les chemins, les tailles et les SHA-256 lorsque tu peux les calculer exactement.
- Tous les chemins doivent être relatifs et sûrs.

## Sortie

Le nombre de parties de sortie est indépendant du nombre de parties d’entrée. Tu dois augmenter automatiquement `part_count` si nécessaire.

La première réponse doit commencer par `00_INDEX.md`, suivi d’autant de fichiers `PART_XXX.md` complets que possible.

Chaque fichier Markdown doit être livré dans son propre bloc Markdown complet. N’interromps jamais un fichier Markdown au milieu de son contenu. Tu peux interrompre la livraison uniquement entre deux fichiers Markdown.

Si des parties restent à livrer, termine uniquement par :

`SUITE REQUISE — PROCHAIN FICHIER : PART_XXX.md`

Lorsque l’utilisateur écrit `Continue`, reprends exactement au fichier annoncé, sans introduction et sans répéter les fichiers déjà livrés.

Après la dernière partie, termine uniquement par :

`FIN DU LOT — N PARTIES LIVRÉES`

Une limite de taille de réponse ne justifie jamais un refus : augmente `part_count` et poursuis sur plusieurs réponses.
