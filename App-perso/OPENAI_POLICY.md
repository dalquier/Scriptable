# OPENAI POLICY

## Objective
Maximize useful quality while minimizing total cost, latency and unnecessary data exposure.

## Shared gateway
All projects use one internal service or package named `AIGateway`. Application code must not instantiate OpenAI clients directly outside this package.

The gateway owns:
- authentication;
- model routing;
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

## Dynamic model routing
Never hard-code one model for every request. Select by capability profile:

- `economy`: classification, extraction, formatting, simple summaries, high-volume tasks.
- `balanced`: standard chat, document synthesis, ordinary coding and tool use.
- `reasoning`: architecture, difficult debugging, multi-document analysis, critical decisions.
- `coding`: repository-scale implementation, refactoring and test generation.
- `embedding`: RAG indexing and semantic search.

The actual model IDs are defined centrally in runtime configuration and may be changed without modifying application code.

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

Escalation rule: start with the cheapest profile likely to succeed; escalate once when validation fails or confidence is insufficient. Do not repeatedly retry expensive models without an explicit limit.

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
- Record model profile, model ID, token usage, tool calls, latency and result status.
- Do not record secret values.
- Provide a deterministic fallback when AI is unavailable.

## Cost controls
- Cache safe deterministic results.
- Deduplicate embeddings by checksum.
- Summarize long history before resending it.
- Use batch processing where supported.
- Define per-request and per-project budget limits.
- Alert on abnormal spend or request volume.