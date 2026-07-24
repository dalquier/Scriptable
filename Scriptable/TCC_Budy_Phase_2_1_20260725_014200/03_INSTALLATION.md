# Installation

## Working Copy

1. Ouvrir le dépôt `dalquier/Scriptable`.
2. Effectuer un `Pull` de la branche `main`.
3. Ouvrir `Scriptable/TCC_Budy_Phase_2_1_20260725_014200/projet`.
4. Rendre ce dossier accessible à Pyto depuis Working Copy ou l’app Fichiers.

## Configuration automatique

Au premier lancement, `config.json` est créé automatiquement. Sans clé API, le simulateur local est utilisé.

Pour OpenAI, créer localement `secrets.json` :

```json
{
  "OPENAI_API_KEY": "COLLER_LA_CLE_API_ICI",
  "OPENAI_MODEL": "gpt-5.5-mini"
}
```

Le fichier est exclu par `.gitignore`.

## Lancement

1. Exécuter `run_tests.py`.
2. Exécuter `app.py`.
3. Tester une nouvelle conversation.
4. Tester le bouton natif `Fermer` en haut à droite.

## Diagnostic

- Écran vide : vérifier que `pyto_ui.WebView.load_url()` existe.
- Erreur 401 : clé OpenAI invalide.
- Erreur 429 : quota ou limite API.
- Le simulateur apparaît malgré une clé : vérifier le nom `OPENAI_API_KEY` dans `secrets.json`.
- Fermer ne répond pas : vérifier que le bouton est bien natif, puis tester le glissement vers le bas comme repli.
- Clavier masquant la saisie : fermer et relancer Pyto après une mise à jour iOS ou Pyto.

Aucune dépendance pip n’est requise.