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
├── domain/          # Pure business logic (entities, value objects, rules)
├── application/     # Use cases & port interfaces
├── adapters/        # External system implementations (REST, DB, LLM)
└── infrastructure/  # Configuration, DI, framework setup
```

**Key principles:**
- Domain layer has zero external dependencies - it's framework-agnostic
- All external interactions go through port interfaces
- Adapters implement ports and can be swapped without affecting domain
- Business rules are referenced by ID (e.g., BR-TASK-003) in code comments linking to `business_rules.md`

## Technology Stack

- **Framework:** FastAPI with Uvicorn
- **Database:** PostgreSQL (per ADR-002)
- **Python:** 3.14+ with dataclasses for domain entities
- **Validation:** Pydantic for API layer

## Development Commands

```bash
# Activate virtual environment
source backend/venv/bin/activate

# Run the application
uvicorn backend.src.main:app --reload

# Health check endpoint
curl http://localhost:8000/health
```

## Domain Entities Pattern

Domain entities use Python dataclasses with:
- UUID-based identifiers with `field(default_factory=uuid4)`
- `__post_init__` for validation and normalization
- Enum-based status with explicit valid transitions
- Business methods that enforce rules (e.g., `task.can_be_selected()`)
- `__eq__` and `__hash__` based on ID for identity equality
- UTC timezone-aware datetimes

Example pattern from `task.py`:
```python
VALID_STATUS_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.TODO: {TaskStatus.DOING, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    # ...
}
```

## Business Rules Reference

The `business_rules.md` file contains all domain rules organized by category:
- **BR-AUTH**: Authentication (magic links, 15-min expiration)
- **BR-TASK**: Task lifecycle and status transitions
- **BR-DEP**: Finish-to-start dependencies, circular dependency prevention
- **BR-ASSIGN**: Self-selection, workload constraints
- **BR-WORK**: Workload calculation (score / capacity * seniority multiplier)

Workload status thresholds: Idle (≤0.3), Relaxed (0.3-0.7), Healthy (0.7-1.2), Tight (1.2-1.5), Impossible (>1.5)

Seniority capacity multipliers: Junior 0.6x, Mid 1.0x, Senior 1.3x, Specialist 1.2x, Lead 1.1x

## Testing Strategy

- **Unit tests:** Domain and use cases with mocked ports
- **Integration tests:** Adapters with real DB/APIs
- **E2E tests:** Full user flows

Write tests first (TDD), mock all external dependencies in unit tests.
