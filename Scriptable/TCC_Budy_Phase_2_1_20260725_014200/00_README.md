# TCC Budy — Phase 2.1

Généré le 25 juillet 2026 à 01:42, heure de Paris.

## Objectif

Faire évoluer la Phase 2 vers une interface plus travaillée, équilibrée et simple, tout en intégrant une fermeture native fiable dans Pyto.

## Résumé

- conversation OpenAI ou simulateur local ;
- historique SQLite local ;
- accueil inspiré d’Apple Journal et de ChatGPT ;
- cartes d’accès rapide ;
- barre de navigation claire ;
- conversation centrée et aérée ;
- bouton natif `Fermer` hors WebView ;
- fermeture via `sender.superview.superview.close()` avec replis de compatibilité ;
- adaptation clair/sombre et clavier iOS.

## Environnement

Pyto sur iPhone ou iPad. Aucune dépendance pip.

## Point d’entrée

`projet/app.py`

## Démarrage

1. Récupérer le dossier avec Working Copy.
2. Facultativement créer `projet/secrets.json`.
3. Lancer `projet/run_tests.py`.
4. Lancer `projet/app.py`.

## Limitations

La fermeture native dépend de la hiérarchie de vues de la version de Pyto installée. Une stratégie de repli appelle aussi `close()` sur la vue racine.

## Actions manuelles

Tester sur l’iPhone réel le bouton Fermer, le clavier, le mode sombre et un appel OpenAI.