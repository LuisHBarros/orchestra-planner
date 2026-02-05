# ADR 005: Transaction Safety for Multi-Entity Operations

- **Date:** 2026-02-05
- **Author:** luishbarros
- **Status:** proposed

## Context

Orchestra Planner has use cases that modify multiple entities in a single operation. For example:

- **FireEmployeeUseCase (UC-051)**: Removes 1 ProjectMember + unassigns N Tasks
- **ResignFromProjectUseCase (UC-052)**: Same pattern as FireEmployee
- **CompleteTaskUseCase**: Marks task done + may unblock dependent tasks
- **RecalculateProjectScheduleUseCase**: Updates multiple task schedules

Without proper transaction boundaries, these operations risk **partial failure**:

### Example: Ghost Tasks Scenario

1. Manager fires "John"
2. System removes John from ProjectMember (Success)
3. System tries to unassign John's 5 tasks
4. Task #3 fails to save (DB error)
5. **Result**: John is gone, but Tasks #3, #4, #5 are still assigned to a non-existent member

This violates data integrity and creates "ghost assignments" that break queries and business rules.

### Current Implementation Risk

Looking at `FireEmployeeUseCase`:

```python
# Save all affected tasks
if affected_tasks:
    await self.task_repository.save_many(affected_tasks)

# Remove the member from the project
await self.project_member_repository.delete(member.id)
```

These are separate repository calls with no shared transaction context. If `delete()` fails after `save_many()` succeeds, we have inconsistent state.

## Decision

**All multi-entity operations MUST execute within a single database transaction, managed at the use case level via a Unit of Work pattern.**

The architecture is:

1. **Unit of Work (UoW)** port in domain layer defines the transaction boundary interface
2. **SQLAlchemy implementation** provides the concrete UoW with session/transaction management
3. **Use cases** receive UoW and call `commit()` only after all operations succeed
4. **Repositories** operate on the session provided by the active UoW

```
┌─────────────────────────────────────────────────────────────┐
│                      Use Case                               │
│  async with uow:                                            │
│      await task_repo.save_many(tasks)                       │
│      await member_repo.delete(member_id)                    │
│      await uow.commit()  # All-or-nothing                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Unit of Work                              │
│  - Manages transaction lifecycle                            │
│  - Provides repositories scoped to transaction              │
│  - Rollback on exception                                    │
└─────────────────────────────────────────────────────────────┘
```

### Domain Port Definition

```python
# domain/ports/unit_of_work.py
from typing import Protocol

class UnitOfWork(Protocol):
    task_repository: TaskRepository
    project_member_repository: ProjectMemberRepository
    # ... other repositories

    async def __aenter__(self) -> "UnitOfWork": ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

### Use Case Pattern

```python
class FireEmployeeUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, input: FireEmployeeInput) -> list[Task]:
        async with self.uow:
            # All operations use repositories from UoW
            project = await self.uow.project_repository.find_by_id(input.project_id)
            # ... validation ...
            
            await self.uow.task_repository.save_many(affected_tasks)
            await self.uow.project_member_repository.delete(member.id)
            
            await self.uow.commit()  # Atomic commit
            
        return affected_tasks
```

## Benefits / Trade-offs

### Benefits

1. **Data Integrity**: All-or-nothing semantics prevent partial failures
2. **Consistency**: No ghost assignments, orphaned records, or broken references
3. **Explicit Boundaries**: Transaction scope is visible in code
4. **Testability**: UoW can be mocked to test rollback scenarios
5. **Hexagonal Alignment**: UoW is a port; implementation is an adapter

### Trade-offs

1. **Refactoring Required**: Existing use cases need UoW injection
2. **Longer Transactions**: Holding transactions open during multiple operations
3. **Complexity**: Additional abstraction layer to understand and maintain
4. **Connection Pool Pressure**: Long transactions may hold connections longer

## Alternatives

### Alternative A: Repository-Level Transactions (Current State)

Each repository method handles its own transaction.

**Pros:**
- Simple implementation
- No additional abstractions

**Cons:**
- Cannot guarantee atomicity across multiple repository calls
- Leads to partial failure scenarios (the problem we're solving)
- Inconsistent data states possible

### Alternative B: Saga Pattern with Compensation

Use eventual consistency with compensating transactions on failure.

```python
try:
    await task_repository.save_many(affected_tasks)
    await member_repository.delete(member.id)
except Exception:
    # Compensate: restore tasks to original state
    await task_repository.save_many(original_tasks)
    raise
```

**Pros:**
- Works in distributed systems
- No long-running transactions

**Cons:**
- Complex compensation logic for every operation
- Temporary inconsistent state is visible
- Compensation can also fail
- Overkill for a single-database system

### Alternative C: Database-Level Triggers

Use PostgreSQL triggers to cascade deletions and updates.

**Pros:**
- Guaranteed atomicity at DB level
- No application code changes

**Cons:**
- Business logic in database (violates hexagonal architecture)
- Hard to test and debug
- Tight coupling to PostgreSQL
- Complex trigger chains are maintenance nightmares

## Consequences

1. **New Port Required**: Add `UnitOfWork` protocol to `domain/ports/`

2. **Infrastructure Implementation**: Create SQLAlchemy-based UoW in `infrastructure/db/`

3. **Use Case Refactoring**: Update multi-entity use cases to use UoW:
   - `FireEmployeeUseCase`
   - `ResignFromProjectUseCase`
   - `CompleteTaskUseCase` (if it unblocks dependents)
   - `RecalculateProjectScheduleUseCase`

4. **Dependency Injection Changes**: DI container must provide UoW instances

5. **Testing Updates**: 
   - Unit tests mock the UoW
   - Integration tests verify actual transaction behavior
   - Add specific tests for rollback scenarios

6. **Performance Consideration**: Monitor transaction duration in production; consider read-only operations outside transactions where safe

## Implementation Priority

High priority for use cases with clear multi-entity mutation:

| Use Case | Entities Modified | Priority |
|----------|-------------------|----------|
| FireEmployeeUseCase | Member + N Tasks | High |
| ResignFromProjectUseCase | Member + N Tasks | High |
| RecalculateProjectScheduleUseCase | N Tasks | High |
| CompleteTaskUseCase | Task + Dependents | Medium |

## References

- [Unit of Work Pattern - Martin Fowler](https://martinfowler.com/eaaCatalog/unitOfWork.html)
- [SQLAlchemy Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- `backend/src/application/use_cases/project_management/fire_employee.py`
- `backend/src/application/use_cases/project_management/resign_from_project.py`
