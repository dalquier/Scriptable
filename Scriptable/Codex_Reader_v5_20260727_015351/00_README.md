# Codex Reader v5

Codex Reader v5 est une mini-application Pyto destinée à ouvrir une page Codex authentifiée, extraire la question et la réponse visibles, préserver au mieux la structure Markdown, puis permettre leur copie ou leur export.

## Objectifs

- champ URL natif, distinct de la zone de conversation ChatGPT ;
- authentification manuelle avec Apple dans une WebView dédiée ;
- réutilisation de la session tant que les cookies de Pyto sont conservés ;
- ouverture directe des liens `https://chatgpt.com/s/...` ;
- extraction via plusieurs moteurs JavaScript compatibles Pyto ;
- fallback WKWebView via Rubicon lorsque l’API simplifiée de Pyto est insuffisante ;
- vue résultat dédiée avec question, réponse et boutons de copie ;
- export Markdown et texte dans le dossier Documents de Pyto ;
- interface fermable, non bloquée en plein écran.

## Point de sécurité

Le projet ne récupère pas les cookies de Safari, de l’application ChatGPT ou du trousseau Apple. La connexion doit être réalisée dans la WebView de l’application. Aucun mot de passe ni jeton n’est enregistré par le projet.

## Démarrage rapide

1. Copier le dossier `projet/` dans Pyto.
2. Ouvrir `projet/app.py`.
3. Lancer le script.
4. Appuyer sur **Connexion** et utiliser **Continuer avec Apple**.
5. Coller un lien Codex dans le champ URL.
6. Appuyer sur **Ouvrir**, attendre le chargement, puis **Extraire**.

Voir `03_INSTALLATION.md` pour les détails et le diagnostic de compatibilité.