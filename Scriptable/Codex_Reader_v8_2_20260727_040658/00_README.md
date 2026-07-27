# Codex Reader v8.2

Version corrigée après diagnostic réel de la page Codex.

## Correction principale

Le HTML brut de Codex n'est plus injecté directement dans la vue de résultat. Il est nettoyé puis reconstruit avec une liste blanche de balises sémantiques. Les boutons de feedback, de copie, de partage et les conteneurs interactifs sont supprimés.

## Utilisation

1. Copier le dossier `projet` dans Pyto.
2. Lancer `app.py`.
3. Se connecter si nécessaire.
4. Coller le lien Codex.
5. Appuyer sur **Analyser**.

Le diagnostic fourni montre que les pouces ont les libellés `Donner un avis positif` et `Donner un avis négatif`. La v8.2 utilise ces attributs comme borne de fin de réponse.