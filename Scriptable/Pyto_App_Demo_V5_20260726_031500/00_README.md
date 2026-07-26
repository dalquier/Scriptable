# Pyto App Demo V5

Exemple complet d'interface Pyto ressemblant à une véritable application iPhone.

## Concept

Cette V5 utilise une architecture hybride :

- **Python** pour la logique, le stockage et l'orchestration ;
- **WKWebView** pour l'interface moderne HTML/CSS/JavaScript ;
- **UIKit** pour les fonctions natives iOS : alertes, partage et ouverture d'URL ;
- **pont JavaScript → Python** par schéma d'URL interne `pytoapp://action?...`.

## Fonctions démontrées

- interface plein écran de type application ;
- barre supérieure et navigation par onglets ;
- cartes, statistiques, activités et réglages ;
- mode clair/sombre automatique ;
- persistance JSON des compteurs et préférences ;
- bouton d'action principal ;
- alerte native UIKit ;
- feuille de partage iOS ;
- ouverture d'une URL externe ;
- remise à zéro des données ;
- journal technique ;
- gestion d'erreur visible.

## Point d'entrée

Lancer :

`projet/main.py`

## Version

- Version : 5.0.0
- Cible : Pyto sur iPhone/iPad
- Livraison : branche `main`
