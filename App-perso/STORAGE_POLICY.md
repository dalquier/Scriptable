# STORAGE POLICY

## Canonical locations
- GitHub `App-perso/`: source code, tests, migrations, prompts and technical documentation.
- Google Drive `/App-perso`: project documents and approved RAG corpus.
- Runtime database: structured application state and metadata.
- Object storage: generated files, uploaded binaries, images and exports.
- Secret manager: credentials and API keys.

## Google Drive layout
Existing root folders:
- `00_Gouvernance`
- `01_Projets`
- `02_Base_documentaire_RAG`
- `03_Modeles`
- `04_Archives`

Per-project documents belong in `01_Projets/<project_slug>/`.
RAG-approved sources belong in `02_Base_documentaire_RAG/` and carry project, type, status, version and confidentiality metadata.

## Source catalog
Every connected source is registered with:
- stable source ID;
- provider;
- allowed roots or repositories;
- read/write permissions;
- authentication method;
- supported formats;
- indexing policy;
- retention policy;
- sensitivity level.

## GitHub
- Code is canonical only in GitHub.
- Google Drive and object storage must not contain competing code copies.
- Repository file references use repository, ref, path and commit SHA.

## Database
Store structured state, links and metadata, not canonical documents or source code.
All schema changes use versioned migrations committed to GitHub.

## Object storage
Every stored object has:
- immutable object ID;
- project ID;
- MIME type and size;
- checksum;
- creation timestamp;
- retention status;
- database reference.

Generated output intended as a durable project document must be copied or exported to the correct Google Drive project folder.

## RAG indexing
For each source file store:
- provider file ID and location;
- checksum and modified timestamp;
- project and document type;
- version and validity status;
- confidentiality classification;
- chunk IDs and embedding version.

Index changes incrementally. Delete or deactivate chunks when their source is deleted, moved outside an approved root or superseded.

## Access control
- Connectors receive minimum required scopes.
- Retrieval respects project and user authorization.
- Sensitive sources are excluded from logs and analytics.
- No storage credential is passed to the model.

## Backup and portability
Projects must document export and restore procedures for database and object storage data. Vendor-specific runtime data must be exportable in an open format where practical.