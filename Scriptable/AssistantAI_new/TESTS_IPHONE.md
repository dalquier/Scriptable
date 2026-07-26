# Checklist de validation sur iPhone

Préparer `projet/config_local.py` localement, sans jamais le committer.

## Prévol

- [ ] Exécuter `projet/diagnostic.py` et confirmer le bilan **PRÊT**.
- [ ] Vérifier que `mainthread=True` est indiqué dans le contrôle `pyto_ui`.
- [ ] Exécuter `projet/main.py`.
- [ ] Vérifier le titre, la version 5.0.1, les boutons et la zone sûre.
- [ ] Tester les modes clair et sombre.

## Conversation et clavier

- [ ] Ouvrir **Écrire…** et vérifier que le champ et les boutons restent visibles.
- [ ] Envoyer un premier message et recevoir une réponse sans doublon.
- [ ] Envoyer un deuxième puis un troisième message sans crash.
- [ ] Vérifier la conservation du contexte.
- [ ] Vérifier que les boutons sont désactivés pendant l’attente puis réactivés.

## Web et persistance

- [ ] Activer **Web** et vérifier le statut.
- [ ] Poser une question récente et vérifier l’indication de recherche Web.
- [ ] Désactiver **Web**.
- [ ] Créer une nouvelle conversation.
- [ ] Fermer et relancer l’application ; vérifier la restauration de la dernière conversation.

## Erreurs et arrêt

- [ ] Couper le réseau et vérifier une erreur lisible sans blocage.
- [ ] Tester sans `config_local.py`.
- [ ] Tester une clé refusée et un modèle non autorisé.
- [ ] Toucher **Fermer** avec puis sans clavier.
- [ ] Relancer immédiatement l’application et vérifier qu’aucun processus ne reste bloqué.
