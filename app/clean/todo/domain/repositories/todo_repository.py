from abc import ABC, abstractmethod

from app.clean.todo.domain.entities.todo import Todo, TodoPriority, TodoStatus


class TodoRepository(ABC):
    """Abstract Repository Interface for Todo operations.

    Service layer depends only on this interface, not on implementation details.
    This ensures complete separation from database concerns.
    """

    @abstractmethod
    def save(self, todo: Todo) -> Todo:
        """Save a todo (create or update).

        Args:
            todo: Todo domain entity to save

        Returns:
            Saved todo with updated fields (id, timestamps)
        """
        pass

    @abstractmethod
    def find_by_id(self, todo_id: int) -> Todo | None:
        """Find todo by ID.

        Args:
            todo_id: ID of the todo to find

        Returns:
            Todo domain entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_all_by_user_id(self, user_id: int) -> list[Todo]:
        """Find all todos for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List of todo domain entities
        """
        pass

    @abstractmethod
    def find_active_todos(self, user_id: int) -> list[Todo]:
        """Find active todos (pending or in_progress) for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of active todo domain entities
        """
        pass

    @abstractmethod
    def find_by_status(
        self, status: TodoStatus, user_id: int | None = None
    ) -> list[Todo]:
        """Find todos by status.

        Args:
            status: Status to filter by
            user_id: Optional user ID to filter by

        Returns:
            List of todo domain entities matching the status
        """
        pass

    @abstractmethod
    def find_by_priority(
        self, priority: TodoPriority, user_id: int | None = None
    ) -> list[Todo]:
        """Find todos by priority.

        Args:
            priority: Priority to filter by
            user_id: Optional user ID to filter by

        Returns:
            List of todo domain entities matching the priority
        """
        pass

    @abstractmethod
    def find_overdue_todos(self, user_id: int | None = None) -> list[Todo]:
        """Find overdue todos.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of overdue todo domain entities
        """
        pass

    @abstractmethod
    def find_with_pagination(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
        user_id: int | None = None,
    ) -> list[Todo]:
        """Find todos with pagination and optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter
            priority: Optional priority filter
            user_id: Optional user ID filter

        Returns:
            List of todo domain entities
        """
        pass

    @abstractmethod
    def delete(self, todo_id: int) -> bool:
        """Delete todo by ID.

        Args:
            todo_id: ID of the todo to delete

        Returns:
            True if deleted successfully, False if not found
        """
        pass

    @abstractmethod
    def count_by_status(self, status: TodoStatus, user_id: int | None = None) -> int:
        """Count todos by status.

        Args:
            status: Status to count
            user_id: Optional user ID to filter by

        Returns:
            Number of todos with the specified status
        """
        pass

    @abstractmethod
    def count_total(self, user_id: int | None = None) -> int:
        """Count total todos.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            Total number of todos
        """
        pass

    @abstractmethod
    def exists(self, todo_id: int) -> bool:
        """Check if todo exists.

        Args:
            todo_id: ID of the todo to check

        Returns:
            True if todo exists, False otherwise
        """
        pass
