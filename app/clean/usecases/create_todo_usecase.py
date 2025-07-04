from datetime import datetime

from app.clean.domain.entities.todo import Todo, TodoPriority
from app.clean.domain.repositories.todo_repository import TodoRepository


class CreateTodoUseCase:
    """UseCase for creating a new Todo.

    Single Responsibility: Handle the creation of a new Todo with proper
    business logic validation and error handling.

    Dependencies:
    - Only depends on Domain layer (TodoRepository interface)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(self, repository: TodoRepository):
        """Initialize with TodoRepository dependency.

        Args:
            repository: TodoRepository interface implementation
        """
        self.repository = repository

    def execute(
        self,
        title: str,
        description: str | None = None,
        due_date: datetime | None = None,
        priority: TodoPriority = TodoPriority.medium,
        user_id: int | None = None,
    ) -> Todo:
        """Execute the create todo use case.

        Args:
            title: Todo title (required)
            description: Optional todo description
            due_date: Optional due date
            priority: Todo priority (defaults to medium)
            user_id: Optional user ID (for future multi-user support)

        Returns:
            Todo: Created todo entity

        Raises:
            RuntimeError: If todo creation fails

        Note:
            Basic validation (title length, etc.) is handled by API DTOs.
            This method focuses on business logic only.
        """
        try:
            todo = Todo.create(
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
            )
            return self.repository.save(todo)
        except Exception as e:
            raise RuntimeError(f"Failed to create todo: {str(e)}") from e
