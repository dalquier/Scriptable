# Installation

## Récupération avec Working Copy

1. Ouvrir Working Copy sur l’iPhone.
2. Cloner ou ouvrir le dépôt `dalquier/Scriptable`.
3. Effectuer un pull de la branche `main`.
4. Ouvrir le dossier `Scriptable/Pyto_Project_Exchange_V5_20260724_194003`.
5. Vérifier que les huit fichiers du manifeste sont présents.

## Accès depuis l’app Fichiers

1. Dans Working Copy, activer l’intégration avec l’app Fichiers si nécessaire.
2. Ouvrir l’app Fichiers.
3. Aller dans Working Copy, puis dans le dépôt `Scriptable`.
4. Ouvrir `Scriptable/Pyto_Project_Exchange_V5_20260724_194003/projet`.

## Ouverture dans Pyto

1. Dans Pyto, ouvrir `projet/main.py` depuis l’app Fichiers.
2. Exécuter `main.py`.
3. L’interface présente cinq actions :
   - exporter un projet ;
   - importer un lot ;
   - copier le prompt principal ;
   - copier le prompt pour une conversation existante ;
   - fermer la vue.

## Dépendances

Aucune installation `pip` n’est requise. Les modules suivants sont fournis par Pyto :

- `pyto_ui` ;
- `file_system` ;
- `pasteboard`.

Les autres imports appartiennent à la bibliothèque standard Python.

## Paramètres et clés API

Aucune clé API n’est nécessaire pour le fonctionnement local de cette version. Aucun secret réel ne doit être ajouté au dépôt.

## Test d’export

1. Créer un petit dossier de test contenant un fichier Python et un fichier texte.
2. Lancer `main.py`.
3. Choisir **Exporter un projet**.
4. Sélectionner le dossier de test puis un dossier de destination.
5. Vérifier la présence de `00_INDEX.md`, d’au moins un fichier `PART_XXX.md` et des deux prompts.

## Test d’import

1. Lancer `main.py`.
2. Choisir **Importer un lot**.
3. Sélectionner le dossier précédemment exporté.
4. Choisir un nouveau dossier de destination.
5. Comparer les fichiers restaurés aux fichiers d’origine.

## Diagnostic des erreurs courantes

- **Partie manquante** : vérifier la valeur `part_count` dans `00_INDEX.md` et la présence exacte de toutes les parties attendues.
- **SHA-256 invalide** : un fichier ou un fragment a été modifié, tronqué ou mal recopié.
- **Chemin relatif non sûr** : le lot contient un chemin absolu, vide ou incluant `..`.
- **Version incompatible** : le lot importé n’est pas au format PPE 5.0.
- **Sélecteur de dossier fermé sans choix** : relancer l’action et sélectionner un dossier accessible à Pyto.
- **Vue non refermable** : utiliser le bouton **Fermer** ; la présentation est configurée en mode feuille.
