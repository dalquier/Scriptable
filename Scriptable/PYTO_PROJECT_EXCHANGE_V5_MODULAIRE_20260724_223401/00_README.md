# PYTO_PROJECT_EXCHANGE V5 Modulaire

- Généré le : 2026-07-24 à 22:34:01 (Europe/Paris)
- Objectif : fournir une version modulaire, maintenable et exécutable sous Pyto du projet PYTO_PROJECT_EXCHANGE V5.
- Résumé : export complet d’un projet Pyto vers un lot Markdown multipartie, import d’un lot, validation des chemins, calcul de SHA-256, copie de prompts ChatGPT et interface iOS avec boutons fonctionnels.
- Environnement cible : Pyto sur iPhone/iPad, Python 3.10+.
- Dépendances : bibliothèque standard Python et module `pyto_ui` fourni par Pyto.
- Point d’entrée : `projet/main.py`.

## Démarrage

1. Récupérer le dossier avec Working Copy ou l’app Fichiers.
2. Ouvrir `projet/main.py` dans Pyto.
3. Exécuter le script.
4. Utiliser les boutons Exporter, Importer, Copier le prompt V5 ou Copier le prompt de migration.

## Fonctions principales

- Export récursif d’un dossier projet.
- Exclusion des fichiers temporaires et secrets usuels.
- Encodage UTF-8 ou Base64 selon le type de fichier.
- Découpage des gros fichiers en fragments.
- Répartition automatique en `PART_XXX.md`.
- Génération de `00_INDEX.md`.
- Import transactionnel vers un nouveau dossier.
- Protection contre les chemins absolus et `..`.
- Vérification des empreintes SHA-256 des fichiers reconstruits.
- Interface modulaire avec callbacks conservés en mémoire.

## Limitations connues

- Le sélecteur de dossier dépend des API disponibles dans la version installée de Pyto. Le projet utilise en priorité `pick_directory`, puis `pick_document` comme solution de repli.
- Les fichiers extrêmement volumineux augmentent la consommation mémoire lors de l’export.
- Le mode DELTA et l’historique de snapshots avancé ne sont pas inclus dans cette livraison corrective : la priorité est une base V5 fiable et fonctionnelle.

## Actions manuelles restantes

- Aucune clé API n’est nécessaire.
- Ne pas ajouter de secrets dans le dossier du projet.
- Adapter les exclusions dans `projet/config.py` si certains répertoires propres à vos projets doivent être ignorés.