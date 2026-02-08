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

Without proper transaction boundaries, these operations risk partial failure.

Example: Ghost Tasks Scenario
1. Manager fires "John"
2. System removes John from ProjectMember (Success)
3. System tries to unassign John's 5 tasks
4. Task #3 fails to save (DB error)
5. Result: John is gone, but Tasks #3, #4, #5 are still assigned to a non-existent member

This violates data integrity and creates "ghost assignments" that break queries and business rules.

Current implementation risk (from `FireEmployeeUseCase`):

```python
# Save all affected tasks
if affected_tasks:
    await self.task_repository.save_many(affected_tasks)

# Remove the member from the project
await self.project_member_repository.delete(member.id)
```

These are separate repository calls with no shared transaction context. If `delete()` fails after `save_many()` succeeds, we have inconsistent state.

## Decision
All multi-entity operations must execute within a single database transaction, managed at the use case level via a Unit of Work pattern.

The architecture is:
1. **Unit of Work (UoW)** port in domain layer defines the transaction boundary interface.
2. **SQLAlchemy implementation** provides the concrete UoW with session/transaction management.
3. **Use cases** receive UoW and call `commit()` only after all operations succeed.
4. **Repositories** operate on the session provided by the active UoW.

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

Domain port definition:

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

Use case pattern:

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

## Benefits
- Data integrity: all-or-nothing semantics prevent partial failures.
- Consistency: no ghost assignments, orphaned records, or broken references.
- Explicit boundaries: transaction scope is visible in code.
- Testability: UoW can be mocked to test rollback scenarios.
- Hexagonal alignment: UoW is a port; implementation is an adapter.

## Trade-offs
- Refactoring required: existing use cases need UoW injection.
- Longer transactions: holding transactions open during multiple operations.
- Complexity: additional abstraction layer to understand and maintain.
- Connection pool pressure: long transactions may hold connections longer.

## Alternatives
### Alternative A: Repository-Level Transactions (Current State)
Pros: Simple implementation, no additional abstractions.
Cons: Cannot guarantee atomicity across multiple repository calls, leads to partial failure scenarios, inconsistent data states possible.

### Alternative B: Saga Pattern with Compensation
Pros: Works in distributed systems, no long-running transactions.
Cons: Complex compensation logic for every operation, temporary inconsistent state is visible, compensation can also fail, overkill for a single-database system.

### Alternative C: Database-Level Triggers
Pros: Guaranteed atomicity at DB level, no application code changes.
Cons: Business logic in database (violates hexagonal architecture), hard to test and debug, tight coupling to PostgreSQL, complex trigger chains are maintenance nightmares.

## Consequences
- Add a `UnitOfWork` protocol to `domain/ports/`.
- Create a SQLAlchemy-based UoW implementation in infrastructure.
- Refactor multi-entity use cases to use UoW:
  - `FireEmployeeUseCase`
  - `ResignFromProjectUseCase`
  - `CompleteTaskUseCase` (if it unblocks dependents)
  - `RecalculateProjectScheduleUseCase`
- Update dependency injection to provide UoW instances.
- Add tests for rollback scenarios and UoW usage.

## References
- None.
