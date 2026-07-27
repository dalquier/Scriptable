# Installation

1. Dans Working Copy, mets à jour `dalquier/Scriptable`.
2. Copie le dossier `projet` dans un dossier accessible par Pyto, sans modifier les noms de fichiers.
3. Ouvre `app.py` dans Pyto.
4. Lance le script.
5. Appuie sur **Connexion** et utilise **Continuer avec Apple** dans la WebView.
6. Une fois connecté, ouvre un lien Codex avec le champ URL natif.
7. Appuie sur **Sélectionner**, puis touche l’encadré gris de la question voulue.
8. Lorsque l’encadré est surligné, appuie sur **Afficher**.

## Connexion mémorisée

Le script utilise toujours la même WebView Pyto et ne demande pas de navigation privée. Les cookies sont donc réutilisés lorsque la version de Pyto conserve le stockage web entre deux lancements. Aucun identifiant Apple n’est enregistré par le projet.

## En cas d’échec d’extraction

Lance `diagnostics.py`. Si l’exécution JavaScript n’est pas exposée par ta version de `pyto_ui.WebView`, le rapport indiquera les méthodes disponibles.
