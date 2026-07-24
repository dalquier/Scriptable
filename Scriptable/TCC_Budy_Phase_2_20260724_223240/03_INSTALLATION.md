# Installation

## Récupération depuis GitHub

1. Ouvrir Working Copy.
2. Cloner ou ouvrir `dalquier/Scriptable`.
3. Effectuer un `Pull` sur la branche `main`.
4. Ouvrir `Scriptable/TCC_Budy_Phase_2_20260724_223240/projet`.
5. Utiliser le partage Working Copy ou l’app Fichiers pour rendre le dossier accessible à Pyto.

## Premier lancement

Aucune copie de `config.example.json` n’est nécessaire.

Au premier lancement, TCC Budy crée automatiquement `config.json` avec une configuration sûre :

```json
{
  "provider": "auto",
  "model": "gpt-5.5-mini",
  "api_url": "https://api.openai.com/v1/responses",
  "timeout_seconds": 90,
  "max_output_tokens": 1200,
  "context_message_limit": 12,
  "store_remote_responses": false,
  "system_instructions": "Instructions système de TCC Budy"
}
```

Le fichier `config.example.json` reste uniquement une référence documentaire. Il n’est jamais requis à l’exécution.

## Activation d’OpenAI

Créer localement `projet/secrets.json` :

```json
{
  "OPENAI_API_KEY": "COLLER_LA_CLE_API_ICI",
  "OPENAI_MODEL": "gpt-5.5-mini"
}
```

Puis conserver dans `config.json` :

```json
{
  "provider": "auto"
}
```

Avec `provider: auto` :

- une clé présente active automatiquement OpenAI ;
- aucune clé présente lance automatiquement le simulateur local.

Il est aussi possible de forcer un comportement :

```json
{
  "provider": "openai"
}
```

ou :

```json
{
  "provider": "simulator"
}
```

Même avec `provider: openai`, l’application revient au simulateur si aucune clé n’est disponible afin de rester démarrable.

`secrets.json` est ignoré par Git et ne doit jamais être committé.

## Lancement dans Pyto

1. Ouvrir `run_tests.py` et l’exécuter.
2. Vérifier que les tests réussissent.
3. Ouvrir `app.py` et l’exécuter.
4. Créer une conversation et envoyer un message.
5. Vérifier dans l’interface si le fournisseur actif est OpenAI ou le simulateur.
6. Fermer la feuille avec le contrôle natif Pyto/iOS ou un glissement vers le bas.

## Dépendances

Aucune installation `pip` n’est requise. Le projet utilise la bibliothèque standard et `pyto_ui` fourni par Pyto.

## Diagnostic

- `config.example.json est introuvable` : cette erreur est corrigée dans la version actuelle ; effectuer un nouveau `Pull`.
- `JSON invalide dans config.json` : vérifier les virgules, guillemets et accolades.
- OpenAI ne s’active pas : vérifier que `secrets.json` est au même niveau que `app.py` et contient `OPENAI_API_KEY`.
- `Erreur OpenAI HTTP 401` : clé invalide ou révoquée.
- `Erreur OpenAI HTTP 429` : quota, crédit ou limite atteinte.
- `Impossible de joindre OpenAI` : vérifier la connexion et le délai.
- La fenêtre ne se ferme pas : utiliser la fermeture native de la feuille, pas un bouton HTML.
- La migration échoue : supprimer uniquement la base locale de test ou restaurer une migration cohérente ; ne pas modifier une migration déjà appliquée.
