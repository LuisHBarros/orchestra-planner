# Hexagonal Architecture with SOLID & TDD

## Overview
This project uses **Hexagonal Architecture** (Ports and Adapters) to separate business logic from infrastructure, following **SOLID principles** and **TDD**.

## Core Layers
1. **Domain Core**: Business logic, entities, value objects, and use cases.
2. **Ports**: Interfaces for input/output (e.g., `UserRepository`, `CreateUserUseCase`).
3. **Adapters**: Implementations for external systems (REST, DB, etc.).

## Key Principles
- **SOLID**: Each class has a single responsibility, depends on abstractions.
- **TDD**: Write tests first, then implement.

## Project Structure

src/
├── domain/          # Business logic
├── application/     # Use cases & ports
├── adapters/        # REST, DB, etc.
└── infrastructure/  # Config, DI

## Testing Strategy
- **Unit**: Domain & use cases (mock ports).
- **Integration**: Adapters (real DB, APIs).
- **E2E**: Full user flows.

## Resources
- [ADRs](/docs/adr) for decision rationale.
- [Patterns](/docs/patterns) for code examples.
- [Configuration](/docs/configuration.md) for environment variables.

**Goal:** Keep domain pure, adapters pluggable, and tests fast.
