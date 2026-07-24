# Installation d’AssistantIA v3.0

## Récupération depuis GitHub

Dans Working Copy, ouvrez le dépôt `dalquier/Scriptable`, effectuez un pull de la branche `main`, puis naviguez vers :

`Scriptable/AssistantIA_v3_0_20260724_231834`

## Accès depuis l’app Fichiers

Depuis Working Copy, partagez ou exportez le dossier de livraison vers iCloud Drive, dans un emplacement accessible par Pyto.

## Préparation dans Pyto

1. ouvrez le dossier `projet` ;
2. copiez `config_local.example.py` ;
3. renommez la copie en `config_local.py` ;
4. remplacez la valeur factice par votre vraie clé OpenAI ;
5. ne synchronisez jamais `config_local.py` dans GitHub.

Exemple local :

```python
OPENAI_API_KEY = "sk-proj-votre-vraie-cle"
```

## Dépendances

Aucune installation externe n’est requise. Le projet utilise uniquement les modules standards de Python et `pyto_ui`, fourni par Pyto.

## Lancement

Ouvrez puis exécutez :

`projet/main.py`

## Test de l’installation

1. l’interface doit s’ouvrir en plein écran ;
2. saisissez une question simple ;
3. appuyez sur `Envoyer` ;
4. vérifiez que la réponse s’affiche ;
5. fermez puis relancez l’application pour vérifier la persistance SQLite ;
6. activez `Web : oui` et testez une question nécessitant une information récente.

## Diagnostic des erreurs courantes

- `config_local.py introuvable` : créez-le à partir du fichier exemple ;
- clé invalide : vérifiez la clé et l’accès API ;
- erreur HTTP 401 : authentification incorrecte ;
- erreur HTTP 429 : quota ou limite de débit atteinte ;
- modèle indisponible : modifiez `OPENAI_MODEL` dans `config.py` ;
- erreur réseau : vérifiez la connexion Internet ;
- base SQLite non inscriptible : déplacez le projet dans un dossier accessible en écriture par Pyto ;
- erreur `pyto_ui` : exécutez le script dans Pyto et non dans un interpréteur Python standard.
