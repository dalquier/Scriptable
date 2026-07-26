# Installation

1. Télécharge le dossier `projet` sur l’iPhone.
2. Ouvre `main.py` dans Pyto.
3. Lance le script.
4. Dans la zone Réglages, saisis :
   - dépôt : `dalquier/Scriptable`
   - branche : `main`
   - dossier racine : `Scriptable`
   - jeton : un Personal Access Token GitHub autorisé à lire et écrire `Contents`.
5. Appuie sur **Enregistrer réglages** puis **Lister**.

## Important

Le jeton n’est jamais inclus dans GitHub. Il est conservé dans `github_manager_v6.local.json`, créé localement à côté du script. Ne partage pas ce fichier.

## Utilisation

- saisis un chemin relatif dans le champ **Chemin** ;
- **Lister** affiche un dossier ;
- **Ouvrir** charge un fichier dans l’éditeur ;
- **Enregistrer** met à jour le fichier ouvert ;
- les autres commandes utilisent les champs **Chemin** et **Nouveau chemin**.
