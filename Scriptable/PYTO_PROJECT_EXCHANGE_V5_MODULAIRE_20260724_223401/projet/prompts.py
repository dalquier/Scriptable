PROMPT_V5 = r'''Tu vas recevoir un projet logiciel au format PYTO_PROJECT_EXCHANGE version 5.0.

RÈGLES IMPÉRATIVES

1. Lis intégralement 00_INDEX.md avant toute autre partie.
2. Le champ JSON "part_count" de 00_INDEX.md est l'unique source de vérité pour le lot reçu.
3. N'invente jamais de partie absente.
4. Reconstitue chaque fichier à partir de ses fragments, dans l'ordre de chunk_index.
5. Préserve les chemins relatifs.
6. N'utilise jamais de chemin absolu ni de chemin contenant "..".
7. Tu peux modifier, ajouter, renommer ou supprimer des fichiers selon la mission.
8. Retourne toujours le projet complet, jamais seulement un patch.
9. Le nombre de parties du lot de sortie est indépendant de celui du lot d'entrée.
10. Augmente automatiquement part_count si la taille finale l'exige.
11. Privilégie plusieurs petites parties plutôt que quelques parties trop grosses.
12. Ne coupe jamais un fichier Markdown de livraison au milieu d'une réponse.
13. Tu peux interrompre la livraison uniquement entre deux fichiers Markdown.
14. Si la livraison doit continuer, termine par "SUITE REQUISE".
15. À la reprise, accepte notamment : "Continue", "Reprendre PART_005.md", "Relivrer PART_003.md" ou "Reprendre après PART_006.md".
16. À la fin du dernier fichier, écris "FIN DU LOT".
17. Mets à jour 00_INDEX.md afin qu'il corresponde exactement aux parties et fichiers retournés.
18. Vérifie les empreintes SHA-256 annoncées lorsque le format les fournit.
19. La limite de taille d'une réponse n'est jamais une raison pour refuser la génération.

FORMAT DE SORTIE

00_INDEX.md
```md
[contenu complet]
```

PART_001.md
```md
[contenu complet]
```

Puis les parties suivantes. Ne fournis aucun commentaire hors protocole, sauf un message d'erreur explicite si le lot d'entrée est invalide.
'''

MIGRATION_PROMPT = r'''Cette conversation utilisait éventuellement une ancienne version du protocole.

À partir de maintenant, ignore les anciennes règles de livraison et utilise exclusivement PYTO_PROJECT_EXCHANGE version 5.0.

Le nombre de parties de sortie est libre et peut être supérieur au nombre de parties d'entrée. Répartis la livraison sur plusieurs réponses lorsque nécessaire. Ne coupe jamais un fichier Markdown. Continue jusqu'au marqueur final : FIN DU LOT.
'''
