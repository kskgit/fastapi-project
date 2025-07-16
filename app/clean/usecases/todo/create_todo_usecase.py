from datetime import datetime

from app.clean.domain.entities.todo import Todo, TodoPriority
from app.clean.domain.repositories.todo_repository import TodoRepository
from app.clean.domain.repositories.user_repository import UserRepository


class CreateTodoUseCase:
    """UseCase for creating a new Todo.

    Single Responsibility: Handle the creation of a new Todo with proper
    business logic validation and error handling.

    Dependencies:
    - Only depends on Domain layer (TodoRepository and UserRepository interfaces)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(
        self, todo_repository: TodoRepository, user_repository: UserRepository
    ):
        """Initialize with repository dependencies.

        Args:
            todo_repository: TodoRepository interface implementation
            user_repository: UserRepository interface implementation
        """
        self.todo_repository = todo_repository
        self.user_repository = user_repository

    def execute(
        self,
        title: str,
        user_id: int,
        description: str | None = None,
        due_date: datetime | None = None,
        priority: TodoPriority = TodoPriority.medium,
    ) -> Todo:
        """Execute the create todo use case.

        Args:
            title: Todo title (required)
            user_id: User ID for the todo owner
            description: Optional todo description
            due_date: Optional due date
            priority: Todo priority (defaults to medium)

        Returns:
            Todo: Created todo entity

        Raises:
            RuntimeError: If todo creation fails

        Note:
            Basic validation (title length, etc.) is handled by API DTOs.
            This method focuses on business logic only.
        """
        try:
            # Validate that user exists
            if not self.user_repository.exists(user_id):
                raise ValueError(f"User with id {user_id} not found")

            todo = Todo.create(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
            )
            return self.todo_repository.save(todo)
        except ValueError:
            # Re-raise ValueError as-is for proper API error handling
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to create todo: {str(e)}") from e
