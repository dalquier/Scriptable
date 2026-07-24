# TCC Budy — livraison GitHub

- Généré le : 24 juillet 2026 à 19:38:59 (Europe/Paris)
- Dépôt : `dalquier/Scriptable`
- Branche : `main`
- Environnement cible : Pyto sur iPhone/iOS
- Point d’entrée : `projet/app.py`

## Objectif

Livrer le projet complet TCC Budy Sprint 0.2.2 avec historique SQLite, interface WebView, fournisseur simulé, gestion des erreurs et correction renforcée du bouton **Fermer**.

## Résumé fonctionnel

L’application permet de créer, reprendre et supprimer des conversations locales. Le serveur HTTP local relie la WebView aux services Python. Les réponses sont simulées tant que l’intégration OpenAI n’est pas activée.

## Dépendances

- Pyto sur iOS ;
- modules Python standards uniquement ;
- `pyto_ui` et `mainthread`, fournis par Pyto.

## Démarrage

1. Copier `projet/` dans `iCloud Drive/Pyto/TCC Budy/`.
2. Ouvrir `app.py` dans Pyto.
3. Exécuter le script.

## Limitations connues

- aucun appel OpenAI dans cette livraison ;
- mono-utilisateur et mono-appareil ;
- la fermeture repose sur `close()` ou `dismiss()` selon la version de Pyto installée.

## Actions manuelles restantes

- tester le bouton **Fermer** sur l’iPhone cible ;
- valider le Sprint 0.2 avant d’activer OpenAI ;
- ne jamais enregistrer une vraie clé API dans GitHub.
