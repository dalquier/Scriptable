# Codex Reader v8.1

Version reconstruite à partir des captures réelles de l’interface Codex mobile.

## Principe

1. Vérifie la session ChatGPT dans la WebView Pyto.
2. Demande une connexion Apple uniquement si nécessaire.
3. Charge un lien `chatgpt.com/s/...`.
4. Repère la dernière paire de boutons pouce haut / pouce bas.
5. Remonte au bloc complet de la réponse.
6. Cherche juste avant ce bloc le dernier encadré gris de question.
7. Clique automatiquement sur l’encadré pour l’agrandir.
8. Affiche une vue dédiée avec deux cartes et deux boutons Copier.

## Installation

Copier tout le dossier `projet/` dans Pyto puis lancer `app.py`.

## Compatibilité validée

Cette version utilise directement `pyto_ui.WebView.evaluate_js`, présent sur l’installation testée.