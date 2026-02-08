ADR 006: Rejection of HATEOAS Implementation
Date: 2026-02-08

Author: Luis H. Barros

Status: accepted

## Context
The Orchestra Planner is a backend-heavy system designed for high-precision task management and seamless integration with LLM Agents. As the project evolves using Hexagonal Architecture and FastAPI, we evaluated whether implementing **HATEOAS** (Hypermedia as the Engine of Application State) would provide significant value in terms of client-server decoupling and discoverability.

## Decision
We have decided against the implementation of **HATEOAS**. The API will remain a standard RESTful API using static Pydantic schemas and OpenAPI (Swagger) documentation. Instead of hypermedia links, we will utilize a "Capabilities/Permissions" pattern within the resource payloads to guide the frontend and agents on valid state transitions.

## Benefits / Trade-offs
- **Benefit 1**: Reduced Complexity: Eliminates the need for complex link-generation logic in the API Adapters, keeping the codebase cleaner.

- **Benefit 2**: Developer Experience (DX): Provides a more predictable contract for Frontend developers using TypeScript, who prefer static type definitions over dynamic link parsing.

- **Benefit 3**: LLM Efficiency: AI Agents perform better when consuming structured schemas (OpenAPI) rather than navigating a graph of hypermedia links in real-time.

- **Trade-off 1**: Increased Coupling: The frontend will have hardcoded URL patterns (mitigated by automated client generation from OpenAPI).

- **Trade-off 2**: Client-side State Logic: The client may need to know more about the business rules to determine if an action is valid, although this is partially offset by the "Capabilities" pattern.

## Alternatives
- **Alternative A**: Full HATEOAS: Using JSON-HAL or Siren. Pros: Maximum decoupling. Cons: High implementation overhead, larger payloads, and poor integration with modern frontend tooling.

- **Alternative B**: Capabilities Pattern: Returning a list of allowed actions (e.g., can_edit: true) in the response. Pros: Lightweight, easy for the frontend to consume, and maintains clear business logic boundaries. (This is our chosen path).
