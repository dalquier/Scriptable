# AssistantIA V2

Généré le 24 juillet 2026 à 19:41:33 (Europe/Paris).

## Objectif

Application Pyto iOS modulaire combinant :

- conversations avec l’API OpenAI Responses ;
- recherche Web OpenAI ;
- base documentaire locale RAG ;
- affichage des sources Web et documentaires ;
- index SQLite ;
- import de documents depuis l’app Fichiers ;
- interface moderne adaptée à l’iPhone.

## Environnement cible

- iPhone ou iPad ;
- Pyto ;
- Python 3.10 ou version compatible fournie par Pyto ;
- connexion Internet pour OpenAI et la recherche Web.

## Dépendances

Aucune dépendance externe obligatoire pour les formats texte, Markdown, CSV, JSON, DOCX, XLSX et PPTX. L’extraction PDF tente d’utiliser `pypdf` puis `PyPDF2` si l’un de ces modules est installé.

## Point d’entrée

`projet/main.py`

## Démarrage

1. Récupérer cette livraison avec Working Copy ou l’application GitHub.
2. Copier le dossier `projet` dans un emplacement accessible à Pyto.
3. Ouvrir `projet/config.py` et renseigner une clé OpenAI locale.
4. Lancer `projet/main.py`.
5. Utiliser le bouton d’import pour copier les documents à indexer dans `projet/data/knowledge/`.

## Sécurité

Aucun secret réel n’est enregistré dans cette livraison. La clé OpenAI doit être ajoutée localement dans `config.py` ou dans un fichier `secrets.py` non versionné.

## Limitations connues

- L’accès direct et persistant à un dossier Google Drive n’est pas fiable depuis le sélecteur de dossiers iOS ; l’application importe donc des fichiers vers un dossier local.
- Les fichiers Google Docs, Sheets et Slides natifs doivent être exportés vers un format standard avant import.
- Le rendu Markdown est volontairement léger afin de rester compatible avec Pyto.
- L’indexation des gros corpus peut prendre du temps et consommer des crédits d’embeddings.

## Actions manuelles restantes

- renseigner la clé OpenAI ;
- éventuellement installer `pypdf` ;
- importer les documents TCC Budy ;
- vérifier le nom exact du modèle disponible sur le projet API OpenAI.
