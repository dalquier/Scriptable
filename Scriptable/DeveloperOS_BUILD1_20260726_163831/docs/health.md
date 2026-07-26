# Health

Health statuses are `HEALTHY`, `WARNING`, `DEGRADED`, `CRITICAL` and `UNKNOWN`. Checks return typed results. Aggregation selects the highest severity; an exception is converted into an `UNKNOWN` result instead of crashing reporting. Reports include an ISO-8601 UTC timestamp and serialize to plain dictionaries.
