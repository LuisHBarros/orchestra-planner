# ADR 003: Manager-as-Member Modeling

- **Date:** 2026-02-04
- **Author:** luishbarros
- **Status:** accepted

## Context
Orchestra Planner distinguishes between two actor roles within a project:
- **Manager**: The project creator with administrative rights (planning, inviting, unblocking)
- **Employee**: A user invited to the project who executes tasks

The question arises: should the Manager be modeled as a special type of ProjectMember, or should Manager and Member be completely separate concepts?

This decision impacts:
- How we enforce BR-PROJ-002 (managers cannot be assigned tasks)
- Authorization checks throughout the application
- Data model complexity and query patterns

## Decision
Managers are represented as ProjectMembers with special constraints enforced at the use-case level.

Specifically:
1. The `Project` entity has a `manager_id` field pointing to a `User`.
2. Managers may also exist as `ProjectMember` records (for role/seniority tracking).
3. Task selection rules (via `TaskSelectionPolicy`) prevent managers from selecting tasks.
4. The `Project.is_manager(user_id)` method provides the authoritative check.

This is a "Manager-as-Special-Member" pattern rather than completely separate hierarchies.

## Benefits
- Simpler data model: no need for a separate Manager entity or inheritance hierarchy.
- Unified membership queries: query all project participants through ProjectMember.
- Flexibility: manager can have a role/seniority if needed for reporting or future features.
- Consistent authorization: single `is_manager()` check works everywhere.

## Trade-offs
- Defensive checks required: every task-related operation must check `is_manager()` to prevent violations of BR-PROJ-002.
- Conceptual blurring: the boundary between "administrative role" and "execution role" is implicit rather than explicit in the type system.
- Potential for bugs: forgetting to add the manager check in a new use case could allow rule violations.
- No compile-time safety: the constraint is runtime-enforced, not type-enforced.

## Alternatives
### Alternative A: Separate Manager and Member Hierarchies
Pros: Type-safe separation of concerns, impossible to accidentally assign tasks to managers, clearer domain model.
Cons: More complex data model, queries must join multiple tables, code duplication for shared behaviors.

### Alternative B: Role-Based Discrimination
Pros: Single entity with explicit discrimination, easy to query all members, type field makes role explicit.
Cons: Optional fields based on type (code smell), still requires runtime checks, enum coupling.

## Consequences
- Task selection policies must always check `project.is_manager(member.user_id)`.
- New use cases involving task assignment must include manager checks.
- Tests must cover manager-attempts-to-select-task scenarios for relevant use cases.
- If manager roles become more complex (e.g., multiple manager roles, delegated permissions), this decision should be revisited.

## References
- BR-PROJ-002 (Managers cannot select tasks)
