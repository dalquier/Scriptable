# Checklist de validation sur iPhone (Pyto)

Préparer `projet/config_local.py` localement, sans jamais le committer, puis cocher chaque étape.

## Prévol
- [ ] Exécuter `projet/diagnostic.py`; confirmer le bilan **PRÊT** (l'absence de `config_local.py` est une information non bloquante).
- [ ] Confirmer que la base temporaire de diagnostic est supprimée.
- [ ] Exécuter `projet/main.py`; vérifier nom, version, conversation, statut et boutons Nouveau/Web/Écrire/Fermer.
- [ ] Vérifier que l'en-tête est sous l'encoche/Dynamic Island et que rien ne déborde.
- [ ] Tester lisibilité et contraste en modes clair puis sombre.

## Conversation et clavier
- [ ] Toucher **Écrire…**, ouvrir le clavier et vérifier que champ, Annuler et Envoyer restent visibles.
- [ ] Envoyer un premier message; voir immédiatement le message utilisateur puis « AssistantIA réfléchit… ».
- [ ] Vérifier que les boutons sont désactivés pendant l'attente puis réactivés.
- [ ] Recevoir la première réponse sans doublon.
- [ ] Envoyer un deuxième puis un troisième message sans crash.
- [ ] Vérifier que les réponses tiennent compte des messages précédents et que la conversation défile en bas.

## Web et persistance
- [ ] Activer **Web**; vérifier libellé et statut « Recherche Web activée ».
- [ ] Poser une question récente; vérifier « Réponse avec recherche Web » et, si disponibles, le nombre de sources.
- [ ] Désactiver **Web** et vérifier son état explicite.
- [ ] Toucher **Nouveau**; vérifier une conversation vide.
- [ ] Envoyer un message, fermer, relancer `main.py`; vérifier la restauration de cette dernière conversation.

## Erreurs et arrêt
- [ ] Couper le réseau, envoyer et vérifier une erreur compréhensible; le message utilisateur reste présent et aucune réponse assistant factice n'apparaît.
- [ ] Tester sans `config_local.py`; vérifier que la clé absente est expliquée sans crash ni fuite.
- [ ] Tester une clé refusée et un modèle non autorisé; vérifier les erreurs HTTP lisibles.
- [ ] Tester un délai d'attente (réseau très lent); vérifier la réactivation des boutons et la possibilité de réessayer.
- [ ] Toucher **Fermer** avec puis sans clavier; vérifier le retour à Pyto.
- [ ] Vérifier qu'aucun thread/processus visible ne reste bloqué et qu'un nouveau lancement fonctionne.
