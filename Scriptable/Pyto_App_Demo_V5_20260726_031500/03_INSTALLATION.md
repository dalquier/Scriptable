# Installation dans Pyto

## Méthode recommandée

1. Ouvrir le dossier de livraison dans GitHub.
2. Télécharger le dossier `projet` ou cloner/copier le dépôt dans iCloud Drive.
3. Placer le dossier dans un emplacement accessible à Pyto, par exemple :

```text
Sur mon iPhone/Pyto/Pyto_App_Demo_V5/
```

4. Dans Pyto, ouvrir `main.py`.
5. Exécuter le script.

## Structure obligatoire

Ne séparez pas les fichiers. `main.py`, les modules Python et le dossier `ui` doivent rester dans la même arborescence.

## Lancement depuis Raccourcis

1. Ouvrir l'application Raccourcis.
2. Créer un nouveau raccourci.
3. Ajouter l'action Pyto « Run Script ».
4. Sélectionner `projet/main.py`.
5. Activer l'affichage de Pyto pour voir l'interface.
6. Ajouter le raccourci à l'écran d'accueil avec une icône personnalisée.

## Dépannage

- Si la page est blanche, vérifier que `ui/index.html`, `ui/app.css` et `ui/app.js` sont présents.
- Si une fonction native échoue, lire le journal affiché dans l'onglet Activité.
- La feuille de partage et les alertes doivent être exécutées au premier plan dans Pyto.
