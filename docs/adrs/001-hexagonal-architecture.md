# ADR 001: Hexagonal Architecture

- **Date:** 2026-01-31
- **Author:** luishbarros
- **Status:** accepted

## Context
The Orchestra Planner is a web application that requires complex business rules (tasks, dependencies, workload, LLM integration) and high testability.  
It is necessary to ensure that the core business (domain logic) remains independent of frameworks, databases, or external interfaces, allowing flexibility, maintenance, and efficient testing.

## Decision

Adapt the **Hexagonal Architecture** (Ports and Adapters) to separate the domain from external layers.  
The system will be organized into:
- **Domain Core**: entities, value objects, use cases, and business rules.  
- **Ports**: interfaces defining input contracts (use cases) and output contracts (repositories, notifications, LLM services).  
- **Adapters**: concrete implementations for databases, REST API, LLM provider, and notifications.  
- **Infrastructure**: configuration, dependency injection, and framework integration.

## Benefits
- Testability: domain can be tested in isolation using mocks.
- Flexibility: changes in frameworks, databases, or APIs don’t affect core logic.
- Clarity: separation of responsibilities improves readability and maintainability.
- Preparation for LLM/Notifications: adding new adapters is straightforward.

## Trade-offs
- Initial complexity: more layers and abstractions may seem excessive for prototypes.
- Development overhead: creating interfaces and mocks increases initial effort.


## Alternatives

- **MVC (Model-View-Controller)**
  - **Pros:** Simplest, easy to implement, low learning curve, widely known pattern.
  - **Cons:** Mixes business logic with presentation and control, difficult to test in isolation, limited flexibility for changes in databases, external APIs, or LLM. For the Orchestra Planner, which has complex rules and optional integration with AI, MVC increases the risk of coupling and technical debt.

- **Microservices**
  - **Pros:** Independent services, horizontal scalability, isolated deployments.
  - **Cons:** Higher operational and integration complexity; communication overhead between services; need for distributed transactions; not justified for the current size of the project. For the Orchestra Planner, which is still a medium-sized system, the monolithic modular architecture with Hexagonal offers simplicity without losing flexibility.

**References**
- Alistair Cockburn, "Hexagonal Architecture" – https://alistair.cockburn.us/hexagonal-architecture/  
- SOLID Principles – https://en.wikipedia.org/wiki/SOLID  
- Mozilla Developer Network (MDN) – https://developer.mozilla.org/en-US/docs/Glossary/MVC
- Microservices Patterns – https://microservices.io/patterns/index.html
