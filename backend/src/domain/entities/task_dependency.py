"""TaskDependency entity definition."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID


@dataclass(frozen=True)
class TaskDependency:
    """
    Represents a Finish-to-Start dependency between tasks.
    
    BR-DEP-001: Dependencies are strict "Finish-to-Start". Task B cannot start 
                until Task A is Done.
    BR-DEP-002: Circular dependencies are strictly prohibited.
    BR-DEP-003: If a parent task is not Done, the child task status is Blocked.
    
    Attributes:
        blocking_task_id: The parent task that must be completed first.
        blocked_task_id: The child task that depends on the parent.
    """
    blocking_task_id: UUID  # Parent task (must finish first)
    blocked_task_id: UUID   # Child task (waits for parent)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate dependency."""
        if self.blocking_task_id == self.blocked_task_id:
            raise ValueError("A task cannot depend on itself")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaskDependency):
            return NotImplemented
        return (
            self.blocking_task_id == other.blocking_task_id
            and self.blocked_task_id == other.blocked_task_id
        )

    def __hash__(self) -> int:
        return hash((self.blocking_task_id, self.blocked_task_id))


def detect_circular_dependency(
    new_dependency: TaskDependency,
    existing_dependencies: list[TaskDependency],
) -> bool:
    """
    Detect if adding a new dependency would create a circular reference.
    
    BR-DEP-002: Circular dependencies are strictly prohibited.
    
    Uses DFS to detect cycles in the dependency graph.
    
    Args:
        new_dependency: The new dependency to add.
        existing_dependencies: List of existing dependencies.
    
    Returns:
        True if a cycle would be created, False otherwise.
    """
    # Build adjacency list (blocking_task -> list of blocked_tasks)
    graph: dict[UUID, list[UUID]] = {}
    for dep in existing_dependencies:
        if dep.blocking_task_id not in graph:
            graph[dep.blocking_task_id] = []
        graph[dep.blocking_task_id].append(dep.blocked_task_id)
    
    # Add the new dependency to the graph
    if new_dependency.blocking_task_id not in graph:
        graph[new_dependency.blocking_task_id] = []
    graph[new_dependency.blocking_task_id].append(new_dependency.blocked_task_id)
    
    # DFS to detect cycle starting from the blocked task of new dependency
    # We need to check if we can reach the blocking task from the blocked task
    visited: set[UUID] = set()
    stack: set[UUID] = set()
    
    def has_cycle(node: UUID) -> bool:
        if node in stack:
            return True
        if node in visited:
            return False
        
        visited.add(node)
        stack.add(node)
        
        for neighbor in graph.get(node, []):
            if has_cycle(neighbor):
                return True
        
        stack.remove(node)
        return False
    
    # Check all nodes for cycles
    all_nodes = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)
    
    for node in all_nodes:
        if node not in visited:
            if has_cycle(node):
                return True
    
    return False
