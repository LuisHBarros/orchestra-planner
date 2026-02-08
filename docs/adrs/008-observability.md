# ADR 008: Observability — Structured Logging & Request ID

- **Date:** 2026-02-08
- **Author:** luishbarros
- **Status:** accepted

## Context
In asynchronous and distributed systems, plain-text logs (print) become ineffective for debugging failures that span multiple layers or concurrent requests. We need full traceability.

## Decision
Adopt structured logging using the `structlog` library with a mandatory correlation identifier.

Format:
- All production logs will be emitted in JSON format.

Correlation ID:
- A FastAPI middleware captures or generates an `X-Request-Id` for each request.

Context:
- The `request_id` is automatically injected into all logs generated during the request lifecycle using context variables.

## Benefits
- Cloud-ready: JSON logs are natively indexable by tools such as Grafana Loki, ELK, and Datadog.
- Precise debugging: it is possible to filter all logs for a specific request or user in seconds.
- Decoupling: the domain layer does not need to be aware of logging; context is injected via infrastructure.

## Trade-offs
- Human readability: JSON logs are harder to read in the terminal without formatting tools.
- Overhead: small computational cost due to JSON serialization for every log entry.

## Alternatives
- None documented.

## Consequences
- Middleware must ensure a correlation ID exists on every request.
- Log processing infrastructure must handle JSON log ingestion.

## References
- None.
