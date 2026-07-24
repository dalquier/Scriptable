# Installation

## Récupération avec Working Copy

1. Ouvrir le dépôt `dalquier/Scriptable` dans Working Copy.
2. Effectuer un pull de la branche `main`.
3. Ouvrir le dossier `Scriptable/AssistantIA_corrige_20260724_235500`.
4. Partager ou copier le dossier `projet` vers un emplacement accessible à Pyto dans l'app Fichiers.

## Configuration OpenAI

Dans `projet`, dupliquer :

`config_local.example.py`

et renommer la copie :

`config_local.py`

Puis renseigner :

```python
OPENAI_API_KEY = "sk-votre-cle"
```

Ne jamais envoyer ce fichier dans GitHub.

## Test

1. Exécuter `projet/diagnostic.py`.
2. Vérifier que `pyto_ui disponible` vaut `True`.
3. Vérifier que `config_local.py présent` vaut `True`.
4. Exécuter `projet/main.py`.

## Erreurs courantes

- `Fichier config_local.py introuvable` : créer le fichier local.
- `La clé OpenAI locale est absente ou invalide` : vérifier la valeur de la clé.
- `Erreur OpenAI HTTP 401` : clé incorrecte ou révoquée.
- `Erreur OpenAI HTTP 403` : accès au modèle ou à l'outil Web non autorisé.
- `Erreur OpenAI HTTP 400` : vérifier le modèle configuré et désactiver temporairement le Web.
- `No module named pyto_ui` : le script n'est pas exécuté dans Pyto.
- Écran vide : lancer `diagnostic.py`, puis vérifier la console Pyto.
