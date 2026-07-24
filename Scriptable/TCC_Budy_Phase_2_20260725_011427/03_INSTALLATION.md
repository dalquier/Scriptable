# Installation

## Récupération depuis GitHub

1. Ouvrir Working Copy.
2. Cloner ou ouvrir le dépôt `dalquier/Scriptable`.
3. Effectuer un `Pull` sur la branche `main`.
4. Ouvrir `Scriptable/TCC_Budy_Phase_2_20260725_011427/projet`.
5. Rendre ce dossier accessible à Pyto via Working Copy ou l’app Fichiers d’iOS.

## Lancement dans Pyto

1. Ouvrir `run_tests.py` et l’exécuter.
2. Vérifier que les tests réussissent.
3. Ouvrir `app.py` et l’exécuter.
4. Créer une conversation et envoyer un message.
5. Fermer la feuille avec le contrôle natif Pyto/iOS ou un glissement vers le bas.

## Configuration automatique

Au premier lancement, `config.json` est créé automatiquement avec le mode `auto`.

- sans `secrets.json`, le simulateur local est utilisé ;
- avec une clé valide dans `secrets.json`, OpenAI est utilisé automatiquement ;
- `provider` peut aussi être forcé à `simulator` ou `openai` dans `config.json`.

## Configuration OpenAI

Créer localement `projet/secrets.json` :

```json
{
  "OPENAI_API_KEY": "COLLER_LA_CLE_API_ICI",
  "OPENAI_MODEL": "gpt-5.5-mini"
}
```

Le fichier est ignoré par Git et ne doit jamais être committé.

Le fichier `config.json` généré peut être ajusté :

```json
{
  "provider": "auto",
  "model": "gpt-5.5-mini",
  "api_url": "https://api.openai.com/v1/responses",
  "timeout_seconds": 90,
  "max_output_tokens": 1200,
  "context_message_limit": 12,
  "store_remote_responses": false,
  "system_instructions": "Tu es TCC Budy, un compagnon personnel de réflexion inspiré des TCC."
}
```

## Dépendances

Aucune installation `pip` n’est requise. Le projet utilise uniquement la bibliothèque standard et `pyto_ui`.

## Test d’installation

- lancer `run_tests.py` ;
- lancer ensuite `app.py` ;
- vérifier que le bandeau indique `Simulateur local` sans clé ;
- ajouter `secrets.json`, relancer et vérifier que le bandeau indique `OpenAI`.

## Diagnostic

- `JSON invalide` : corriger la syntaxe de `config.json` ou `secrets.json` ;
- `OpenAI est activé mais aucune clé` : ajouter `secrets.json` ou remettre `provider` à `auto` ;
- erreur HTTP 401 : clé invalide ou révoquée ;
- erreur HTTP 429 : quota, crédit ou limite atteinte ;
- erreur réseau : vérifier la connexion et le délai ;
- la fenêtre ne se ferme pas : utiliser la fermeture native de la feuille, pas un bouton HTML ;
- migration incohérente : ne pas modifier une migration déjà appliquée ; restaurer le fichier d’origine ou supprimer uniquement la base locale de test.
