# Installation

## Récupération depuis GitHub

1. Ouvrir Working Copy.
2. Cloner ou ouvrir `dalquier/Scriptable`.
3. Effectuer un `Pull` sur la branche `main`.
4. Ouvrir `Scriptable/TCC_Budy_Phase_2_20260724_223240/projet`.
5. Utiliser le partage Working Copy ou l’app Fichiers pour rendre le dossier accessible à Pyto.

## Configuration

Copier `config.example.json` vers `config.json`. Pour rester en mode local :

```json
{"provider":"simulator"}
```

Pour OpenAI, définir `provider` à `openai` et créer `secrets.json` :

```json
{"OPENAI_API_KEY":"COLLER_LA_CLE_API_ICI"}
```

`secrets.json` est ignoré par Git et ne doit jamais être committé. Le modèle, l’URL, le délai, la limite de contexte et le nombre maximal de jetons sont configurables dans `config.json`.

## Lancement dans Pyto

1. Ouvrir `run_tests.py` et l’exécuter.
2. Vérifier que les quatre tests réussissent.
3. Ouvrir `app.py` et l’exécuter.
4. Créer une conversation et envoyer un message.
5. Fermer la feuille avec le contrôle natif Pyto/iOS ou un glissement vers le bas.

## Dépendances

Aucune installation `pip` n’est requise. Le projet utilise la bibliothèque standard et `pyto_ui` fourni par Pyto.

## Diagnostic

- `OpenAI est activé mais aucune clé...` : créer `secrets.json`.
- `Erreur OpenAI HTTP 401` : clé invalide ou révoquée.
- `Erreur OpenAI HTTP 429` : quota, crédit ou limite atteinte.
- `Impossible de joindre OpenAI` : vérifier la connexion et le délai.
- La fenêtre ne se ferme pas : utiliser la fermeture native de la feuille, pas un bouton HTML.
- La migration échoue : supprimer uniquement la base locale de test ou restaurer une migration cohérente ; ne pas modifier une migration déjà appliquée.
