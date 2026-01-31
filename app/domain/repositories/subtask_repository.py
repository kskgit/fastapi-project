from abc import ABC, abstractmethod

from app.domain.entities import SubTask


class SubTaskRepository(ABC):
    """Abstract Repository Interface for SubTask operations.

    Service layer depends only on this interface, not on implementation details.
    This ensures complete separation from database concerns with async support.
    """

    @abstractmethod
    async def create(self, subtask: SubTask) -> SubTask:
        """Persist a new subtask entity.

        Args:
            subtask: SubTask domain entity to create (must not have id assigned)

        Returns:
            SubTask entity with generated ID and timestamps
        """
        pass

    @abstractmethod
    async def find_by_todo_id(self, todo_id: int) -> list[SubTask]:
        """Find all subtasks belonging to a specific todo.

        Args:
            todo_id: ID of the parent todo

        Returns:
            List of SubTask entities (empty list if none found)
        """
        pass
