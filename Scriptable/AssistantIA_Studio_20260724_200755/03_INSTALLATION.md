# Installation dans Pyto

## 1. Récupérer le projet

Télécharger ou cloner le dossier :

```text
Scriptable/AssistantIA_Studio_20260724_200755/projet
```

Puis le placer dans un dossier accessible par Pyto, idéalement dans iCloud Drive.

## 2. Créer la configuration privée

Créer localement le fichier :

```text
projet/config.local.py
```

avec le contenu suivant :

```python
OPENAI_API_KEY = "sk-..."
```

Ce fichier est ignoré par Git et ne doit jamais être envoyé dans le dépôt.

## 3. Lancer l’application

Ouvrir puis exécuter :

```text
projet/main.py
```

## 4. Dépendances

La première version privilégie exclusivement la bibliothèque standard Python et les modules fournis par Pyto :

- `pyto_ui`
- `sqlite3`
- `urllib`
- `json`
- `pathlib`
- `threading`

## 5. Données locales

Les données seront créées automatiquement dans les dossiers `database/` et `data/`. Elles ne devront pas être versionnées.

## 6. Diagnostic

En cas d’erreur, vérifier en priorité :

1. que la clé OpenAI est valide ;
2. que l’iPhone dispose d’un accès Internet ;
3. que le modèle configuré est disponible pour la clé API ;
4. que le dossier du projet est accessible en écriture depuis Pyto.
