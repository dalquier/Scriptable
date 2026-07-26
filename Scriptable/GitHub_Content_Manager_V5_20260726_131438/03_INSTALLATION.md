# Installation dans Pyto

1. Depuis GitHub, télécharge le dossier de livraison ou clone le dépôt.
2. Place le dossier `projet` dans un emplacement accessible à Pyto, par exemple iCloud Drive/Pyto.
3. Ouvre `projet/main.py` dans Pyto.
4. Exécute le script.
5. Dans Réglages, saisis :
   - le dépôt au format `propriétaire/nom` ;
   - la branche ;
   - le dossier racine facultatif ;
   - un jeton GitHub personnel disposant des droits nécessaires.

## Jeton GitHub

Pour un dépôt public en lecture seule, certaines opérations peuvent fonctionner sans jeton. Pour créer, modifier, renommer ou supprimer des fichiers, un jeton avec accès au contenu du dépôt est nécessaire.

Ne mets jamais le jeton dans `config.example.json` ni dans un fichier synchronisé. L'application tente de le conserver dans le trousseau iOS avec `keyring`. Si `keyring` n'est pas disponible, le jeton reste uniquement en mémoire pour la session.

## Utilisation

- Touchez un dossier pour l'ouvrir.
- Touchez un fichier texte pour le consulter et le modifier.
- Utilisez `+` pour créer un fichier ou un dossier.
- Utilisez le menu d'un fichier pour renommer ou supprimer.
- Le journal local permet de retrouver les dernières actions.
