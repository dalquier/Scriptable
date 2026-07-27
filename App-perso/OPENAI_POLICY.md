# OPENAI POLICY

## Objective
Maximize useful quality while minimizing total cost, latency and unnecessary data exposure.

## Shared gateway
All projects use one internal service or package named `AIGateway`. Application code must not instantiate OpenAI clients directly outside this package.

The gateway owns:
- authentication;
- model routing;
- reasoning effort;
- web search and tool configuration;
- file retrieval connectors;
- timeouts, retries and rate limits;
- structured outputs;
- usage and cost telemetry;
- redaction and audit metadata.

## Secret
The only canonical key name is:

`OPENAI_API_KEY`

The value is stored once per runtime environment in Replit Secrets or the approved secret manager. Scripts read it through the environment. There is deliberately no document containing the key.

Allowed:
```python
api_key = os.environ["OPENAI_API_KEY"]
```

Forbidden:
- hard-coded keys;
- `.env` committed to Git;
- keys in Google Drive;
- keys in database records;
- keys copied between scripts.

`.env.example` may contain only `OPENAI_API_KEY=` with no value.

## Current default model routing
The model IDs remain runtime configuration, but the approved starting defaults are:

| Profile | Default model | Default reasoning | Purpose |
|---|---|---:|---|
| `economy` | `gpt-5.6-luna` | `none` | extraction, classification, formatting, high-volume simple work |
| `balanced` | `gpt-5.6-terra` | `low` | normal chat, document synthesis, routine tool use and ordinary coding |
| `reasoning` | `gpt-5.6-sol` | `medium` | architecture, difficult debugging, multi-document analysis and important decisions |
| `coding` | `gpt-5.6-sol` | `high` | repository-scale implementation, refactoring, review and test generation |
| `embedding` | `text-embedding-3-small` | not applicable | economical RAG indexing and semantic search |

Use `text-embedding-3-large` only when representative retrieval evaluations demonstrate a material quality gain worth the additional cost.

The `gpt-5.6` alias resolves to `gpt-5.6-sol`, but explicit family IDs are preferred in configuration so cost intent is visible.

## Dynamic model routing
Never hard-code one model for every request. Select by capability profile.

Routing inputs:
- task type;
- expected complexity;
- context size;
- tool requirements;
- latency target;
- quality target;
- data sensitivity;
- budget ceiling;
- previous attempt failure.

Escalation rule:
1. Start with the cheapest profile likely to meet the acceptance criteria.
2. Validate the result when the task is machine-checkable or high impact.
3. Escalate at most one profile level when validation fails or confidence is insufficient.
4. Do not repeatedly retry expensive models without an explicit bounded policy.
5. Benchmark model and reasoning choices on representative project tasks before changing the shared defaults.

Reasoning effort is selected independently from the model. Prefer `none` or `low` for routine work, `medium` for difficult analysis, and `high` only for complex coding or high-value reasoning. Higher effort is not automatically better value.

## Responses API
Use the Responses API for new text, reasoning, tool-calling and multi-turn workflows. Preserve tool outputs and response identifiers when continuation semantics are used.

## Web access
Web capability is available through an approved search/browse tool. Use it automatically when information may be current, external verification is needed, or the user explicitly requests it. Do not browse for stable local transformations.

"Always available" means the gateway can invoke web tools when needed; it does not mean every request must perform a paid web search.

## Access to files
OpenAI accesses files only through retrieval tools implemented by the application:
- GitHub connector for repository files and metadata;
- Google Drive connector for authorized folders and documents;
- Replit database connector for structured records;
- Replit Object Storage connector for approved objects;
- additional storage connectors registered in the source catalog.

The model must not receive storage credentials. Connectors enforce authorization, file size limits, supported formats and audit logging.

## Context strategy
Never send every file on every request.
1. Search metadata and indexes.
2. Retrieve only relevant files or chunks.
3. Preserve source identifiers and versions.
4. Fit within an explicit token budget.
5. Cite sources in the response when applicable.

## Reliability
- Prefer structured outputs validated against schemas for machine-consumed responses.
- Set explicit timeouts and bounded retries.
- Record model profile, model ID, reasoning effort, token usage, tool calls, latency and result status.
- Do not record secret values.
- Provide a deterministic fallback when AI is unavailable.
- Send a stable privacy-preserving safety identifier for end-user applications when appropriate.

## Cost controls
- Cache safe deterministic results.
- Deduplicate embeddings by checksum.
- Summarize long history before resending it.
- Use batch processing where supported.
- Track cached tokens and cache-write tokens before enabling explicit prompt caching broadly.
- Define per-request and per-project budget limits.
- Alert on abnormal spend or request volume.
