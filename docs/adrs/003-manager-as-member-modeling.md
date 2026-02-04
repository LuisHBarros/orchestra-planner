# ADR 003: Manager-as-Member Modeling

- **Date:** 2026-02-04
- **Author:** Development Team
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

**Managers ARE represented as ProjectMembers with special constraints enforced at the use-case level.**

Specifically:
1. The `Project` entity has a `manager_id` field pointing to a `User`
2. Managers MAY also exist as `ProjectMember` records (for role/seniority tracking)
3. Task selection rules (via `TaskSelectionPolicy`) prevent managers from selecting tasks
4. The `Project.is_manager(user_id)` method provides the authoritative check

This is a "Manager-as-Special-Member" pattern rather than completely separate hierarchies.

## Benefits / Trade-offs

### Benefits

1. **Simpler Data Model**: No need for separate Manager entity or inheritance hierarchy
2. **Unified Membership Queries**: Can query all project participants through ProjectMember
3. **Flexibility**: Manager can have a role/seniority if needed for reporting or future features
4. **Consistent Authorization**: Single `is_manager()` check works everywhere

### Trade-offs

1. **Defensive Checks Required**: Every task-related operation must check `is_manager()` to prevent violations of BR-PROJ-002
2. **Conceptual Blurring**: The boundary between "administrative role" and "execution role" is implicit rather than explicit in the type system
3. **Potential for Bugs**: Forgetting to add the manager check in a new use case could allow rule violations
4. **No Compile-Time Safety**: The constraint is runtime-enforced, not type-enforced

## Alternatives

### Alternative A: Separate Manager and Member Hierarchies

```python
class ProjectManager:
    project_id: UUID
    user_id: UUID
    
class ProjectMember:  # Only employees
    project_id: UUID
    user_id: UUID
    role_id: UUID
```

**Pros:**
- Type-safe separation of concerns
- Impossible to accidentally assign tasks to managers
- Clearer domain model

**Cons:**
- More complex data model
- Queries must join multiple tables
- Code duplication for shared behaviors

### Alternative B: Role-Based Discrimination

```python
class ProjectMember:
    project_id: UUID
    user_id: UUID
    member_type: MemberType  # MANAGER | EMPLOYEE
    role_id: UUID | None  # Only for employees
```

**Pros:**
- Single entity with explicit discrimination
- Easy to query all members
- Type field makes role explicit

**Cons:**
- Optional fields based on type (code smell)
- Still requires runtime checks
- Enum coupling

## Consequences

1. **TaskSelectionPolicy** must always check `project.is_manager(member.user_id)` before allowing task selection

2. **New use cases** involving task assignment must include manager checks - this is documented in the policy pattern

3. **Testing** must cover manager-attempts-to-select-task scenarios for all relevant use cases

4. **Future consideration**: If the distinction becomes more complex (e.g., multiple manager roles, delegated permissions), we may need to revisit this decision and introduce a more explicit role hierarchy

## Implementation Notes

The `TaskSelectionPolicy` class centralizes all task selection rules including:

```python
def _check_manager_restriction(self, context) -> Optional[SelectionViolation]:
    """BR-PROJ-002: Manager cannot select tasks."""
    if context.project.is_manager(context.member.user_id):
        return SelectionViolation(
            rule_id="BR-PROJ-002",
            message="Managers cannot select tasks.",
        )
    return None
```

This ensures the rule is:
- Enforced consistently
- Easy to test in isolation
- Documented with business rule reference
- Configurable via `ProjectConfig.managers_cannot_select_tasks`

## References

- BR-PROJ-002: "A Manager cannot be assigned Tasks. Their role is strictly administrative."
- `backend/src/domain/services/task_selection_policy.py`
- `backend/src/domain/entities/project_config.py`
