# Installation sur iPhone/iPad

## 1. Récupérer la livraison avec Working Copy

1. Ouvrir Working Copy.
2. Cloner ou ouvrir le dépôt `dalquier/Scriptable`.
3. Effectuer un pull de la branche `main`.
4. Naviguer vers `Scriptable/PYTO_PROJECT_EXCHANGE_V5_MODULAIRE_20260724_223401/projet/`.

## 2. Accéder depuis l’app Fichiers

Dans Working Copy, utiliser l’option de partage ou d’accès aux fichiers pour rendre le dépôt visible dans l’app Fichiers d’iOS. Vérifier que tous les fichiers Python restent dans le même dossier `projet/`.

## 3. Ouvrir dans Pyto

1. Ouvrir Pyto.
2. Depuis l’explorateur de fichiers de Pyto, ouvrir le dossier `projet/`.
3. Ouvrir `main.py`.
4. Exécuter `main.py`.

Le point d’entrée importe automatiquement les autres modules présents dans le même dossier.

## 4. Dépendances

Aucun paquet externe à installer. Le projet utilise :

- la bibliothèque standard Python ;
- `pyto_ui`, fourni par Pyto.

## 5. Paramètres

Les paramètres de découpage et d’exclusion sont dans `config.py` :

- `TARGET_PART_CHARACTERS` ;
- `MAX_FRAGMENT_CHARACTERS` ;
- `EXCLUDED_DIR_NAMES` ;
- `EXCLUDED_FILE_NAMES`.

Aucune clé API n’est requise.

## 6. Test d’installation

1. Lancer `main.py`.
2. Vérifier que la feuille affiche quatre boutons.
3. Appuyer sur `Copier le prompt V5`, puis coller dans Notes pour contrôler la copie.
4. Créer un petit dossier de test contenant un fichier `.py` et un fichier `.json`.
5. Appuyer sur `Exporter un projet`, sélectionner le dossier de test puis un dossier de destination.
6. Vérifier la présence de `00_INDEX.md` et d’au moins un `PART_001.md`.
7. Appuyer sur `Importer un lot` et sélectionner ce dossier d’échange.
8. Vérifier que les fichiers reconstruits sont identiques aux fichiers de test.

## 7. Diagnostic des erreurs courantes

### Les boutons semblent inactifs

- Vérifier que `main.py` est lancé depuis le dossier contenant tous les modules.
- Vérifier qu’aucun fichier n’a été renommé.
- Fermer puis relancer Pyto après un pull Working Copy.
- Lire la console Pyto : une erreur d’import empêche l’initialisation de l’interface.

### Aucun sélecteur de dossier ne s’ouvre

La disponibilité de `pick_directory` dépend de la version de Pyto. Le projet tente automatiquement une solution de repli avec `pick_document`. Mettre Pyto à jour si aucune API n’est disponible.

### Erreur `No module named ...`

Tous les fichiers Python doivent rester ensemble dans `projet/`. Ne lancer pas une copie isolée de `main.py`.

### Échec de l’import SHA-256

Une partie Markdown a été modifiée, tronquée ou mal copiée. Reconstituer le lot complet sans modifier les blocs de contenu.

### Échec sur un fichier binaire

Vérifier que le contenu Base64 n’a pas été reformatté par un éditeur intermédiaire.
