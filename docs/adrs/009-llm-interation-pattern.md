# ADR 009: LLM Interaction Pattern — Hybrid Provider Strategy

- **Date:** 2026-02-08
- **Author:** luishbarros
- **Status:** accepted

## Context
Orchestra Planner relies on LLMs for estimation and automation. Model costs and availability vary, and some users may prefer to use their own API keys for privacy or budget reasons.

## Decision
Implement a Hybrid Provider pattern with fallback for AI interactions.

Global fallback:
- The system defines a "House Model" (e.g., GPT-4o-mini or a local Ollama instance) via environment variables for general use.

Project override:
- Each project can configure its own provider and key (BYOK — Bring Your Own Key) in the `ProjectConfig` entity.

Validation:
- LLM output must always be validated against Pydantic schemas (Structured Outputs) before persisting data in the domain.

## Benefits
- Cost control: allows system administrators to limit usage of the global API key.
- Flexibility: facilitates migration between OpenAI, Anthropic, or local models without changing use case logic.
- Resilience: if a project-specific provider fails, the system can (optionally) fall back to the global provider.

## Trade-offs
- Configuration complexity: requires more sophisticated provider resolution logic in the app factory.
- Prompt drift: different models may interpret the same prompts in slightly different ways.

## Alternatives
- None documented.

## Consequences
- Provider resolution logic must support both global and project-level configurations.
- Validation of LLM outputs becomes a required step in all AI-related flows.

## References
- None.
