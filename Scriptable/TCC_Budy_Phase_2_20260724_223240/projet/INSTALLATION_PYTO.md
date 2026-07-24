# Installation dans Pyto

1. Récupérer le dossier `projet` avec Working Copy.
2. Le rendre accessible dans l'app Fichiers puis l'ouvrir dans Pyto.
3. Copier `config.example.json` vers `config.json`.
4. Pour le simulateur, conserver `"provider": "simulator"`.
5. Pour OpenAI, choisir `"provider": "openai"` puis créer `secrets.json` :

```json
{"OPENAI_API_KEY":"COLLER_LA_CLE_ICI"}
```

6. Ne jamais committer `secrets.json`.
7. Lancer `run_tests.py`, puis `app.py`.
8. Pour fermer l'application, utiliser la fermeture native de la feuille Pyto/iOS ou la faire glisser vers le bas.
