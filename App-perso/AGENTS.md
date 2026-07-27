# AGENTS

## Mandatory sequence
Before changing code:
1. Read governance and project rules.
2. Inspect the existing tree and tests.
3. State assumptions in the delivery notes.
4. Make the smallest coherent change.
5. Run formatting, linting, type checks and tests.
6. Document changed configuration and migrations.

## Write boundaries
- Work only inside the instructed project path.
- Never modify `main` directly.
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

## Delivery report
Every delivery reports:
- files created, changed, renamed or deleted;
- tests and checks executed;
- known limitations;
- configuration or secret names required;
- database migrations;
- security implications;
- recommended next action.

## Stop conditions
Stop and report rather than guessing when:
- required credentials or permissions are missing;
- data migration could destroy information;
- instructions conflict with governance or security;
- the target path or source of truth is ambiguous.