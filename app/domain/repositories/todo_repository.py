from abc import ABC, abstractmethod

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus


class TodoRepository(ABC):
    """Abstract Repository Interface for Todo operations.

    Service layer depends only on this interface, not on implementation details.
    This ensures complete separation from database concerns with async support.
    """

    @abstractmethod
    async def create(self, todo: Todo) -> Todo:
        """Persist a new todo entity.

        Args:
            todo: Todo domain entity to create (must not have id assigned)

        Returns:
            Todo entity with generated ID and timestamps
        """
        pass

    @abstractmethod
    async def update(self, todo: Todo) -> Todo:
        """Update an existing todo entity.

        Args:
            todo: Todo entity with an existing ID to update

        Returns:
            Updated Todo entity reflecting persisted changes
        """
        pass

    @abstractmethod
    async def find_by_id(self, todo_id: int) -> Todo | None:
        """Find todo by ID.

        Args:
            todo_id: ID of the todo to find

        Returns:
            Todo domain entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_with_pagination(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> list[Todo]:
        """Find todos with pagination and optional filters for a specific user.

        Args:
            user_id: User ID to filter by (required)
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter
            priority: Optional priority filter

        Returns:
            List of todo domain entities
        """
        pass

    @abstractmethod
    async def delete(self, todo_id: int) -> bool:
        """Delete todo by ID.

        Args:
            todo_id: ID of the todo to delete

        Returns:
            True if deleted successfully, False if not found
        """
        pass

    @abstractmethod
    async def delete_all_by_user_id(self, user_id: int) -> int:
        """Delete all todos for a specific user.

        Args:
            user_id: ID of the user whose todos should be deleted

        Returns:
            Number of todos deleted
        """
        pass
