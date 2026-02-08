# ADR 006: Rejection of HATEOAS Implementation

- **Date:** 2026-02-08
- **Author:** Luis H. Barros
- **Status:** accepted

## Context
The Orchestra Planner is a backend-heavy system designed for high-precision task management and seamless integration with LLM Agents. As the project evolves using Hexagonal Architecture and FastAPI, we evaluated whether implementing **HATEOAS** (Hypermedia as the Engine of Application State) would provide significant value in terms of client-server decoupling and discoverability.

## Decision
Do not implement **HATEOAS**. The API will remain a standard RESTful API using static Pydantic schemas and OpenAPI (Swagger) documentation. Instead of hypermedia links, use a "Capabilities/Permissions" pattern within resource payloads to guide the frontend and agents on valid state transitions.

## Benefits
- Reduced complexity: eliminates the need for complex link-generation logic in the API adapters, keeping the codebase cleaner.
- Developer experience: provides a more predictable contract for frontend developers using TypeScript, who prefer static type definitions over dynamic link parsing.
- LLM efficiency: AI agents perform better when consuming structured schemas (OpenAPI) rather than navigating a graph of hypermedia links in real time.

## Trade-offs
- Increased coupling: the frontend will have hardcoded URL patterns (mitigated by automated client generation from OpenAPI).
- Client-side state logic: the client may need to know more about the business rules to determine if an action is valid, partially offset by the "Capabilities" pattern.

## Alternatives
### Alternative A: Full HATEOAS (JSON-HAL or Siren)
Pros: Maximum decoupling.
Cons: High implementation overhead, larger payloads, and poor integration with modern frontend tooling.

### Alternative B: Capabilities Pattern
Pros: Lightweight, easy for the frontend to consume, and maintains clear business logic boundaries.
Cons: Still requires the API to define and expose allowed actions explicitly.

## Consequences
- API responses must include a capabilities/permissions shape for relevant resources.
- OpenAPI schemas become the primary contract for clients and agents.

## References
- None.
