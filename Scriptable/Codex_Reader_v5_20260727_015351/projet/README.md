# Projet Pyto — Codex Reader v5

Lancer `app.py`.

## Flux recommandé

1. **Connexion** : authentification ChatGPT avec Apple dans la WebView.
2. **Ouvrir** : chargement direct de l’URL indiquée dans le champ natif.
3. **Extraire** : lecture du DOM par l’adaptateur JavaScript.
4. **Retour** : réaffichage de la page Codex après la vue résultat.
5. **Exporter** : création simultanée d’un fichier Markdown et d’un fichier texte.

Les exports sont écrits dans :

```text
Documents/CodexReader/Exports/
```

## En cas d’erreur JavaScript

Lancer `diagnostics.py`. Le projet tente successivement plusieurs noms de méthodes connus, puis recherche un WKWebView natif accessible. Certaines éditions de Pyto peuvent ne fournir aucun pont d’exécution JavaScript. Dans ce cas, le rapport de diagnostic est indispensable pour ajouter le mécanisme exact disponible dans cette version.
