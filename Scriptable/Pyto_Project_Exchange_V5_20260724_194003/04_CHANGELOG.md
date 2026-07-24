# Changelog — Version 5.0

Création initiale du projet.

## Fichiers créés

- `00_README.md`
- `01_ARBORESCENCE.md`
- `02_MANIFEST.json`
- `03_INSTALLATION.md`
- `04_CHANGELOG.md`
- `projet/main.py`
- `projet/PROMPT_CHATGPT.md`
- `projet/PROMPT_CONVERSATION_EXISTANTE.md`

## Fonctionnalités ajoutées

- export récursif d’un projet Pyto ;
- encodage UTF-8 ou Base64 selon le type de fichier ;
- fragmentation automatique des gros fichiers ;
- regroupement logique des fragments ;
- création de `00_INDEX.md` et des fichiers `PART_XXX.md` ;
- import sécurisé avec validation de l’arborescence, des fragments et des SHA-256 ;
- prompt principal PPE5 intégré ;
- prompt spécifique pour les conversations ChatGPT existantes ;
- livraison multi-réponses imposée lorsque nécessaire ;
- interface Pyto présentée en feuille refermable.

## Corrections par rapport à la version 3

- `part_count` est explicitement défini comme l’unique source de vérité ;
- un projet reçu en une partie peut être renvoyé en plusieurs parties ;
- une limite de sortie ne peut plus justifier un refus ;
- la reprise après `Continue` est imposée ;
- les fichiers de prompt sont également ajoutés dans chaque lot exporté.

## Fichiers modifiés

Aucun : nouvelle livraison horodatée.

## Fichiers supprimés

Aucun.

## Incompatibilités

L’importateur V5 exige un lot déclaré en version `5.0`. Les anciens lots doivent être importés avec leur outil d’origine ou adaptés au nouveau marqueur.

## Migration

Conserver les anciens scripts pour restaurer les lots V2/V3. Utiliser V5 pour les nouveaux échanges.
