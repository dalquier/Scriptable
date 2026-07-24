# AssistantIA v5

AssistantIA v5 est une refonte complète de l'application Pyto avec une interface iPhone repensée.

## Objectifs

- barre supérieure respectant la zone sûre ;
- bouton Web correctement positionné ;
- conversation défilante ;
- champ de saisie remontant au-dessus du clavier ;
- bouton Envoyer intégré à la barre de composition ;
- architecture séparant interface, logique, stockage et client OpenAI ;
- compatibilité avec plusieurs versions de `pyto_ui`.

## Lancement

1. Copier `projet/config_local.example.py` vers `projet/config_local.py`.
2. Renseigner la clé OpenAI.
3. Exécuter `projet/diagnostic.py`.
4. Exécuter `projet/main.py`.

## Point d'entrée

`projet/main.py`
