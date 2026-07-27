# APP-PERSO GOVERNANCE

## 1. Scope
These rules apply to every project generated, modified or deployed under `App-perso/`.
No Replit App topology is fixed by this document.

## 2. Sources of truth
- Code, migrations, prompts, tests, technical docs: GitHub.
- Functional documents, PDFs, Word files, project records, reference corpus: Google Drive `/App-perso`.
- Structured runtime data: project database hosted by Replit or another approved database.
- Generated binaries, images, exports and uploads: Replit Object Storage or another approved object store.
- AI inference, embeddings and tool use: OpenAI API through the shared AI gateway.
- Secrets: environment secret manager only. Never GitHub, Drive, database, logs or source files.

## 3. Mandatory project startup
Before coding, every agent must read:
1. `App-perso/GOVERNANCE.md`
2. `App-perso/AGENTS.md`
3. `App-perso/OPENAI_POLICY.md`
4. `App-perso/STORAGE_POLICY.md`
5. the project's `PROJECT_RULES.md`

No project may start without a problem statement, acceptance criteria, data classification and storage map.

## 4. Git rules
- All code is stored under `App-perso/` in GitHub.
- Never develop directly on `main`.
- Use branches: `feature/*`, `fix/*`, `refactor/*`, `docs/*`, `release/*`.
- Every material change requires tests and a clear commit.
- Secrets and generated files are forbidden in Git.
- Every project must be reproducible from Git plus documented environment variables.

## 5. Code quality baseline
- Clear separation of UI, domain, data and integrations.
- Typed interfaces where supported.
- Centralized configuration.
- Structured logging without sensitive data.
- Explicit error handling, retries, timeouts and cancellation.
- Input validation and least privilege.
- Unit, integration and startup tests.
- Versioned database migrations.
- Automated formatting, linting and CI.
- Minimal docs: README, ARCHITECTURE, CHANGELOG, SECURITY, `.env.example`, tests.

## 6. AI and retrieval
- Applications call a shared AI gateway; direct scattered OpenAI calls are forbidden.
- Model selection is dynamic and cost-aware.
- Web access is enabled for tasks requiring current public information.
- Retrieval access to GitHub, Google Drive, Replit storage and any approved source is provided through explicit connectors.
- The model never receives unrestricted credentials or direct filesystem access.
- Every retrieved answer preserves source, version, timestamp and access scope.

## 7. RAG
- Google Drive `/App-perso/02_Base_documentaire_RAG` is the default document corpus.
- Index only approved folders and supported files.
- Store document IDs, checksums, versions and timestamps.
- Re-index changed files and deactivate obsolete versions.
- Never present an older version as current when a newer valid version exists.

## 8. Security non-negotiables
- `OPENAI_API_KEY` exists only in the runtime secret manager.
- No secret in Markdown, Python, JavaScript, JSON, Drive, GitHub or database rows.
- Never log prompts or files containing sensitive data unless explicitly approved and redacted.
- All connectors use minimum required permissions.

## 9. Definition of done
A delivery is complete only when code runs, tests pass, configuration is documented, storage rules are respected, security checks are complete, and the change is committed on a non-main branch.