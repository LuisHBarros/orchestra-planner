# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Orchestra Planner is a project task management and workload planning application for teams. Key features include:
- Magic link authentication (passwordless)
- Project-based workspaces with roles and seniority levels
- Task management with finish-to-start dependencies
- Workload calculation based on story points and capacity multipliers
- Optional LLM integration for difficulty estimation

## Architecture

This project follows **Hexagonal Architecture (Ports and Adapters)** with strict layer separation:

```
backend/src/
├── domain/                  # THE CORE (zero external dependencies)
│   ├── entities/            # User, Task, Project, etc.
│   ├── services/            # Domain services (ScheduleCalculator, etc.)
│   ├── ports/               # Interfaces for external systems
│   │   ├── repositories/    # Data persistence interfaces
│   │   └── services/        # External service interfaces
│   └── errors/              # Domain-specific exceptions
├── application/
│   └── use_cases/           # Application logic orchestrating domain
└── infrastructure/          # Configuration, DI, DB models
    └── db/
        ├── models/          # SQLAlchemy models (map to domain entities)
        ├── base.py          # Declarative base
        └── session.py       # Session management
```

**Key principles:**
- Domain layer has zero external dependencies - it's framework-agnostic
- Ports (interfaces) belong to Domain layer - they define what domain needs from outside
- Adapters implement ports and can be swapped without affecting domain
- Dependencies flow inward: Adapters → Application → Domain
- Business rules are referenced by ID (e.g., BR-TASK-003) linking to `business_rules.md`
- Schedule calculation is centralized in `ScheduleCalculator` domain service, triggered via `RecalculateProjectScheduleUseCase` (see ADR-004)

## Technology Stack

- **Framework:** FastAPI with Uvicorn
- **Database:** PostgreSQL with SQLAlchemy 2.0+ (async), Alembic for migrations
- **Python:** 3.14+ with dataclasses for domain entities
- **Validation:** Pydantic 2.x for API layer
- **Testing:** pytest with pytest-asyncio

## Development Commands

```bash
# Activate virtual environment
source backend/venv/bin/activate

# Run the application
uvicorn backend.src.main:app --reload

# Run all tests
cd backend && pytest

# Run a single test file
cd backend && pytest tests/application/task_management/test_create_task.py

# Run a specific test
cd backend && pytest tests/application/task_management/test_create_task.py::TestCreateTaskUseCase::test_creates_task_when_requester_is_manager

# Run tests with verbose output
cd backend && pytest -v

# Health check endpoint
curl http://localhost:8000/health
```

## Implementation Order

When building new features, follow this order:

1. `domain/entities/` → Define data structures first
2. `domain/errors/` → Define what can go wrong
3. `domain/ports/` → Define interfaces for external systems
4. `application/use_cases/` → Orchestrate domain logic
5. `infrastructure/db/models/` → SQLAlchemy models with `from_entity`/`to_entity` methods
6. `adapters/db/` → Implement repository ports
7. `adapters/api/` → REST endpoints (inbound)

## Domain Patterns

**Entities** use Python dataclasses with:
- UUID-based identifiers with `field(default_factory=uuid4)`
- `__post_init__` for validation and normalization
- Enum-based status with explicit valid transitions
- `__eq__` and `__hash__` based on ID for identity equality

**Ports** use Python Protocol for structural subtyping:
```python
class UserRepository(Protocol):
    async def find_by_id(self, user_id: UUID) -> Optional[User]: ...
```

**Errors** inherit from `DomainError` with `rule_id` linking to business rules:
```python
class UserNotFoundError(AuthError):
    def __init__(self, identifier: str):
        super().__init__(f"User not found: {identifier}", rule_id="BR-AUTH-001")
```

## Database Model Patterns

SQLAlchemy models in `infrastructure/db/models/` follow this pattern:
- Inherit from `Base` (in `infrastructure/db/base.py`)
- Use `Mapped[]` type hints with `mapped_column()`
- UUIDs use `PG_UUID(as_uuid=True)` from `sqlalchemy.dialects.postgresql`
- Include `from_entity(cls, entity) -> Self` classmethod for domain → model
- Include `to_entity(self) -> Entity` method for model → domain
- Timestamps use `DateTime(timezone=True)` with `server_default=func.now()`

## Business Rules Reference

The `business_rules.md` file contains all domain rules organized by category:
- **BR-AUTH**: Authentication (magic links, 15-min expiration)
- **BR-TASK**: Task lifecycle and status transitions
- **BR-DEP**: Finish-to-start dependencies, circular dependency prevention
- **BR-ASSIGN**: Self-selection, workload constraints
- **BR-WORK**: Workload calculation (score / capacity * seniority multiplier)
- **BR-LLM**: Optional AI integration for difficulty/progress estimation
- **BR-NOTIF**: Notifications (daily reports, alerts, toasts)

Workload thresholds: Idle (≤0.3), Relaxed (0.3-0.7), Healthy (0.7-1.2), Tight (1.2-1.5), Impossible (>1.5)

Seniority multipliers: Junior 0.6x, Mid 1.0x, Senior 1.3x, Specialist 1.2x, Lead 1.1x

## Testing Strategy

- **Unit tests:** Domain and use cases with mocked ports (AsyncMock for repositories)
- **Integration tests:** Adapters with real DB/APIs
- **E2E tests:** Full user flows

Tests use `pytest.fixture` for dependencies and `@pytest.mark.asyncio` for async tests. Write tests first (TDD), mock all external dependencies in unit tests.
