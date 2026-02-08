# ADR 004: Schedule Recalculation Architecture

- **Date:** 2026-02-05
- **Author:** luishbarros
- **Status:** accepted

## Context
Orchestra Planner calculates task schedules based on dependencies, story points, and assignee seniority. Schedule recalculation must occur after various events:
- Task creation or deletion
- Dependency changes (add/remove)
- Assignment changes (task assignee_id)
- Task completion

The question arises: where should the schedule recalculation logic live, and how should it be triggered from use cases like `CompleteTaskUseCase`, `CreateTaskUseCase`, etc.?

This decision impacts:
- Code duplication across use cases
- Separation of concerns
- Testability and maintainability
- Future extensibility (e.g., adding notifications after recalculation)

## Decision
Schedule calculation is centralized in a Domain Service (`ScheduleCalculator`), orchestrated by a dedicated Use Case (`RecalculateProjectScheduleUseCase`). Individual use cases do not embed recalculation logic.

The architecture is:
1. **Domain Service** (`ScheduleCalculator`): Pure calculation logic with no I/O.
2. **Use Case** (`RecalculateProjectScheduleUseCase`): Fetches data, calls calculator, persists results.
3. **Triggering Use Cases** (e.g., `CompleteTaskUseCase`): Focus on their primary responsibility only.
4. **Orchestration**: External layer (API/Controller or future Event System) triggers recalculation after relevant operations.

```
┌─────────────────────────────────────────────────────────────┐
│                     API / Controller                        │
│  (orchestrates: CompleteTask → RecalculateProjectSchedule)   │
└─────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          ▼                                   ▼
┌──────────────────────┐          ┌───────────────────────────┐
│  CompleteTaskUseCase │          │ RecalculateProjectSchedule │
│  (status + logging)  │          │       Use Case             │
└──────────────────────┘          └───────────────────────────┘
                                              │
                                              ▼
                                  ┌───────────────────────────┐
                                  │    ScheduleCalculator     │
                                  │    (Domain Service)       │
                                  └───────────────────────────┘
```

## Benefits
- Single responsibility: each use case does one thing well.
- DRY principle: calculation logic exists in exactly one place (`ScheduleCalculator`).
- Testability: `ScheduleCalculator` can be unit tested with pure inputs/outputs.
- Flexibility: recalculation can be triggered selectively (not every operation needs it).
- Performance: batch recalculation can be deferred or debounced at the orchestration layer.

## Trade-offs
- Orchestration complexity: callers must know to trigger recalculation after certain operations.
- Potential for missed triggers: a new use case might forget to trigger recalculation.
- Two-step operations: some flows require two use case calls instead of one.
- No automatic consistency: schedule may be temporarily stale between operations.

## Alternatives
### Alternative A: Embed Recalculation in Each Use Case
Pros: Automatic consistency after every operation, simpler orchestration (single call).
Cons: Code duplication across use cases, harder to test use cases in isolation, performance overhead (recalculation on every operation), violates Single Responsibility Principle.

### Alternative B: Domain Events with Handlers
Pros: Decoupled and extensible, easy to add more handlers (notifications, analytics), use cases stay focused.
Cons: Added infrastructure complexity, eventual consistency concerns, harder to debug (implicit flow), overkill for current MVP scope.

### Alternative C: Inject RecalculateUseCase into Other Use Cases (Composition)
Pros: Keeps logic centralized, preserves single-call API for callers.
Cons: Implicit coupling between use cases, can still be missed in new use cases, complicates testing.

## Consequences
- A dedicated `RecalculateProjectScheduleUseCase` must be maintained and invoked after relevant operations.
- The API/controller (or future event system) owns orchestration for recalculation triggers.
- Schedule calculation remains pure and isolated in `ScheduleCalculator`.

## References
- None.
