# Installation dans Pyto

## Installation

1. Dans Working Copy ou GitHub, récupérer le dossier `Scriptable/Codex_Reader_v5_20260727_015351/projet`.
2. Copier ce dossier dans `Sur mon iPhone/Pyto` ou `iCloud Drive/Pyto`.
3. Ouvrir `app.py` dans Pyto.
4. Lancer le script.

## Première connexion

1. Appuyer sur **Connexion**.
2. Dans la WebView, choisir **Continuer avec Apple**.
3. Terminer l’authentification.
4. Revenir à l’interface si nécessaire.
5. Coller le lien Codex dans le champ URL, puis appuyer sur **Ouvrir**.

La session dépend du stockage de cookies de la WebView Pyto. iOS ou Pyto peuvent demander une nouvelle connexion après suppression des données, mise à jour ou expiration de session.

## Extraction

- Attendre que la conversation soit entièrement visible.
- Appuyer sur **Extraire**.
- Si le résultat est vide, faire défiler la page jusqu’en bas puis recommencer.
- Utiliser **Copier question**, **Copier réponse**, **Exporter Markdown** ou **Exporter TXT**.

## Diagnostic

Lancer `diagnostics.py` si l’extraction échoue. Le fichier affiche les méthodes disponibles sur `pyto_ui.WebView`. Copier le résultat pour adapter l’ordre des moteurs JavaScript.

## Limites

- Le script ne peut pas reprendre automatiquement la session de Safari ou de l’application ChatGPT.
- L’authentification Apple peut être refusée par un fournisseur OAuth dans certaines WebViews embarquées.
- La structure HTML de Codex peut évoluer. Les sélecteurs sont volontairement multiples et tolérants, mais pourront nécessiter une mise à jour.
