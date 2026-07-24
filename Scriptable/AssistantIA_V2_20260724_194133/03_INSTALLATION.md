# Installation

## Récupération depuis GitHub

### Avec Working Copy

1. Installer Working Copy depuis l’App Store.
2. Ajouter le dépôt `dalquier/Scriptable`.
3. Effectuer un `Pull` sur la branche `main`.
4. Ouvrir le dossier `Scriptable/AssistantIA_V2_20260724_194133/projet`.
5. Utiliser la feuille de partage pour copier ce dossier vers un emplacement accessible à Pyto dans l’app Fichiers.

### Depuis l’app GitHub

1. Ouvrir le dépôt `dalquier/Scriptable`.
2. Aller dans `Scriptable/AssistantIA_V2_20260724_194133`.
3. Télécharger ou partager les fichiers vers l’app Fichiers.

## Ouverture dans Pyto

1. Ouvrir Pyto.
2. Ouvrir le dossier `projet`.
3. Vérifier que tous les fichiers listés dans `01_ARBORESCENCE.md` sont présents.
4. Ouvrir `config.py`.
5. Renseigner la clé OpenAI dans un fichier local `secrets.py` :

```python
OPENAI_API_KEY = "VOTRE_CLE_OPENAI"
```

6. Ne jamais versionner ce fichier.
7. Lancer `main.py`.

## Dépendances

Le projet utilise uniquement la bibliothèque standard pour les fonctions principales.

Pour l’extraction PDF, installer facultativement :

```text
pypdf
```

ou :

```text
PyPDF2
```

Les formats TXT, Markdown, JSON, CSV, DOCX, XLSX et PPTX sont traités sans dépendance externe.

## Paramètres

Les paramètres principaux se trouvent dans `config.py` et `default_settings.json` :

- modèle OpenAI ;
- modèle d’embeddings ;
- mode de recherche Web ;
- taille des passages ;
- nombre de sources documentaires ;
- limites de contexte ;
- langue de l’interface.

## Import des documents

1. Depuis l’application, utiliser le bouton `Importer`.
2. Sélectionner un ou plusieurs fichiers depuis iCloud Drive, Google Drive, Dropbox, OneDrive ou le stockage local.
3. Les fichiers sont copiés dans `data/knowledge`.
4. L’application indexe uniquement les fichiers nouveaux ou modifiés.

Les documents Google Docs, Sheets et Slides natifs doivent être exportés auparavant en DOCX, XLSX, PPTX, PDF, TXT ou Markdown.

## Test d’installation

1. Lancer `main.py`.
2. Vérifier que la barre de statut indique que l’application est prête.
3. Envoyer : `Réponds uniquement par OK.`
4. Activer le mode Web puis demander une information actuelle.
5. Importer un fichier texte contenant une phrase unique.
6. Demander à l’assistant de retrouver cette phrase et vérifier l’affichage d’une source documentaire.

## Diagnostic

### Clé OpenAI absente

Vérifier `secrets.py` ou la valeur locale de `OPENAI_API_KEY`.

### Erreur de modèle

Modifier `OPENAI_MODEL` dans `config.py` pour utiliser un modèle disponible dans le projet API.

### Recherche Web non disponible

Passer le mode Web sur `off`, puis vérifier que le modèle choisi prend en charge l’outil `web_search`.

### PDF sans texte

Le PDF peut être numérisé ou le module PDF peut être absent. Installer `pypdf` ou convertir le document en texte.

### Le clavier masque la saisie

Fermer puis rouvrir la vue. L’interface place le compositeur en haut pour limiter ce problème dans Pyto.

### Index vide

Importer au moins un fichier pris en charge et utiliser le bouton de réindexation.
