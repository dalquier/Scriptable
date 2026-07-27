# AGENTS

## Autonomous execution mode
Treat every request as a complete task to carry through to the most usable result possible.

Do not stop after analysis, a plan, a first draft or an intermediate implementation. Continue autonomously through the necessary cycles:
1. inspect the request and existing state;
2. define the solution;
3. implement all coherent changes;
4. verify consistency across files;
5. run available formatting, linting, type checks and tests;
6. diagnose failures;
7. correct detected problems;
8. repeat verification until the result is usable;
9. deliver the files, patch, branch, pull request or final document;
10. report exactly what was completed, tested and left unresolved.

Do not ask the user to reply `continue`. Do not finish with work described as merely in progress. Make reasonable secondary decisions from the project context and conventions. Ask only when missing information makes progress materially impossible or when an explicitly sensitive action requires approval.

Do not present an intention as a completed action. Report a check as passed only when it was actually executed. If a technical limitation prevents full completion, deliver the most advanced coherent functional result immediately and identify the exact remaining items.

User-facing communication should normally contain only the final completion report. Avoid intermediate progress messages unless a safety issue, required approval or material blocking ambiguity makes interruption necessary.

## Mandatory sequence
Before changing code:
1. Read governance and project rules.
2. Inspect the existing tree and tests.
3. Record assumptions in the delivery notes.
4. Make the smallest coherent complete change.
5. Run formatting, linting, type checks and tests.
6. Document changed configuration and migrations.
7. Inspect the final diff.

## Write boundaries
- Work only inside the instructed project path.
- Never modify `main` directly.
- Use a dedicated branch for repository changes.
- Never create a second canonical copy of a file.
- Reuse shared services before creating duplicates.
- Do not change public interfaces without documenting migration impact.

## Required engineering behavior
- Prefer established libraries and native platform capabilities.
- Keep domain logic independent of UI and external providers.
- Use dependency injection for OpenAI, storage, database and web connectors.
- Validate external data at boundaries.
- Add timeouts, bounded retries and useful error messages.
- Keep functions and modules focused.
- Remove dead code rather than commenting it out.

## AI-specific instructions
- Use `AIGateway`; do not construct provider clients in feature modules.
- Ask the router for a capability profile, not a hard-coded model ID.
- Retrieval must be selective and source-aware.
- Current public facts require web tools.
- Repository or document questions require retrieval from the relevant source before answering.
- Do not claim access to a file or source that was not successfully retrieved.

## GitHub delivery behavior
- Inspect the existing repository before coding.
- Preserve compatibility with the established architecture.
- Add or update tests and documentation.
- Verify the final diff.
- Create a Pull Request when requested or when the project rules require one.

## Delivery report
Every delivery reports:
- files created, changed, renamed or deleted;
- tests and checks actually executed;
- known limitations;
- configuration or secret names required;
- database migrations;
- security implications;
- exact remaining actions requiring the user.

## Stop conditions
Stop and report rather than guessing only when:
- required credentials or permissions are missing and no useful partial delivery is possible;
- data migration could destroy information;
- instructions conflict with governance or security;
- the target path or source of truth remains materially ambiguous after inspection.
