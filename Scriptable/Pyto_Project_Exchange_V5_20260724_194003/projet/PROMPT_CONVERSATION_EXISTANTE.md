# Prompt — imposer PYTO_PROJECT_EXCHANGE 5.0 dans une discussion existante

À partir de maintenant, nous utilisons exclusivement `PYTO_PROJECT_EXCHANGE` version `5.0`.

Ignore tout format d’échange précédent.

## Réception

- `00_INDEX.md` est le registre canonique.
- Le champ JSON `part_count` est l’unique source de vérité.
- N’invente jamais de partie supplémentaire.
- Si `part_count = 1`, `PART_001.md` constitue le lot complet.
- Si la mission est fournie avec la dernière partie, commence immédiatement.
- Lorsque toutes les parties annoncées sont présentes, il est interdit d’affirmer que le projet est incomplet.

## Modification

- Reconstitue tous les fichiers dans l’ordre de `chunk_index`.
- Tu peux ajouter, modifier, renommer, déplacer ou supprimer des fichiers.
- Renvoie toujours le projet final complet.
- Ne renvoie jamais seulement un patch, un diff, un résumé ou des extraits.
- Mets à jour `00_INDEX.md`, `file_count`, `part_count`, les chemins, les fragments, les tailles et les SHA-256 lorsque tu peux les calculer exactement.

## Sortie multi-réponses

- Le nombre de parties de sortie peut être différent de celui du projet reçu.
- Augmente automatiquement `part_count` lorsque la sortie est trop volumineuse.
- Livre `00_INDEX.md` dans la première réponse.
- Livre ensuite autant de fichiers `PART_XXX.md` complets que possible.
- Chaque fichier Markdown doit être dans son propre bloc Markdown complet.
- N’interromps jamais un fichier Markdown au milieu de son contenu.
- Interromps la livraison uniquement entre deux fichiers Markdown.

Si des parties restent à livrer, termine uniquement par :

`SUITE REQUISE — PROCHAIN FICHIER : PART_XXX.md`

Quand j’écris `Continue`, reprends exactement au fichier annoncé, sans introduction et sans répéter les fichiers déjà livrés.

Après la dernière partie, termine uniquement par :

`FIN DU LOT — N PARTIES LIVRÉES`

Une limite de taille de réponse ne justifie jamais un refus. Augmente `part_count` et poursuis sur plusieurs réponses.
