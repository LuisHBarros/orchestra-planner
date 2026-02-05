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

**Schedule calculation is centralized in a Domain Service (`ScheduleCalculator`), orchestrated by a dedicated Use Case (`RecalculateProjectScheduleUseCase`). Individual use cases do NOT embed recalculation logic.**

The architecture is:

1. **Domain Service** (`ScheduleCalculator`): Pure calculation logic with no I/O
2. **Use Case** (`RecalculateProjectScheduleUseCase`): Fetches data, calls calculator, persists results
3. **Triggering Use Cases** (e.g., `CompleteTaskUseCase`): Focus on their primary responsibility only
4. **Orchestration**: External layer (API/Controller or future Event System) triggers recalculation after relevant operations

```
┌─────────────────────────────────────────────────────────────┐
│                     API / Controller                        │
│  (orchestrates: CompleteTask → RecalculateProjectSchedule)  │
└─────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          ▼                                   ▼
┌──────────────────────┐          ┌───────────────────────────┐
│  CompleteTaskUseCase │          │ RecalculateProjectSchedule│
│  (status + logging)  │          │       UseCase             │
└──────────────────────┘          └───────────────────────────┘
                                              │
                                              ▼
                                  ┌───────────────────────────┐
                                  │    ScheduleCalculator     │
                                  │    (Domain Service)       │
                                  └───────────────────────────┘
```

## Benefits / Trade-offs

### Benefits

1. **Single Responsibility**: Each use case does one thing well
2. **DRY Principle**: Calculation logic exists in exactly one place (`ScheduleCalculator`)
3. **Testability**: `ScheduleCalculator` can be unit tested with pure inputs/outputs
4. **Flexibility**: Recalculation can be triggered selectively (not every operation needs it)
5. **Performance**: Batch recalculation can be deferred or debounced at the orchestration layer

### Trade-offs

1. **Orchestration Complexity**: Callers must know to trigger recalculation after certain operations
2. **Potential for Missed Triggers**: A new use case might forget to trigger recalculation
3. **Two-Step Operations**: Some flows require two use case calls instead of one
4. **No Automatic Consistency**: Schedule may be temporarily stale between operations

## Alternatives

### Alternative A: Embed Recalculation in Each Use Case

```python
class CompleteTaskUseCase:
    def execute(self, input):
        task.complete()
        # Embedded recalculation
        self._recalculate_schedule(task.project_id)
```

**Pros:**
- Automatic consistency after every operation
- Simpler orchestration (single call)

**Cons:**
- Code duplication across use cases
- Harder to test use cases in isolation
- Performance overhead (recalculation on every operation)
- Violates Single Responsibility Principle

### Alternative B: Domain Events with Handlers

```python
class CompleteTaskUseCase:
    def execute(self, input):
        task.complete()
        self.event_bus.publish(TaskCompleted(task))

class ScheduleRecalculationHandler:
    def handle(self, event: TaskCompleted):
        self.recalculate_use_case.execute(event.task.project_id)
```

**Pros:**
- Decoupled and extensible
- Easy to add more handlers (notifications, analytics)
- Use cases stay focused

**Cons:**
- Added infrastructure complexity
- Eventual consistency concerns
- Harder to debug (implicit flow)
- Overkill for current MVP scope

### Alternative C: Inject RecalculateUseCase into Other Use Cases (Composition)

```python
class CompleteTaskUseCase:
    def __init__(self, ..., recalculate_use_case: RecalculateProjectScheduleUseCase):
        self.recalculate_use_case = recalculate_use_case

    def execute(self, input):
        task.complete()
        self.recalculate_use_case.execute(task.project_id)
```

**Pros:**
- Explicit dependency
- Single call from API layer
- Still testable (mock the injected use case)

**Cons:**
- Tight coupling between use cases
- Circular dependency risks
- Harder to make recalculation optional

## Consequences

1. **API Layer Responsibility**: Controllers/routers must orchestrate multi-step flows:
   ```python
   @router.post("/tasks/{task_id}/complete")
   async def complete_task(task_id: UUID):
       task = await complete_task_use_case.execute(input)
       await recalculate_schedule_use_case.execute(task.project_id)
       return task
   ```

2. **Documentation Required**: New use cases affecting schedule must document the need for recalculation trigger

3. **Future Migration Path**: If complexity grows, we can introduce Domain Events (Alternative B) without changing the domain service

4. **Testing Strategy**:
   - Unit test `ScheduleCalculator` with pure inputs
   - Unit test use cases with mocked repositories
   - Integration test the full flow at API level

## Future Considerations

If the number of schedule-triggering operations grows significantly, consider:

1. **Domain Events**: Migrate to event-driven recalculation for better decoupling
2. **Debounced Recalculation**: Batch multiple changes before recalculating
3. **Background Processing**: Move recalculation to async workers for large projects

For MVP, the current architecture is sufficient and provides a clear path for evolution.

## References

- `backend/src/domain/services/schedule_calculator.py`
- `backend/src/application/use_cases/project_management/recalculate_project_schedule.py`
- `backend/src/application/use_cases/task_management/complete_task.py`
- BR-SCHED-003: "Schedule is recalculated when dependencies change"
