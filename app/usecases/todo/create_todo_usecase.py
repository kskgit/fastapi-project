from datetime import datetime

from app.domain.entities.todo import Todo, TodoPriority
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.todo_domain_service import TodoDomainService


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
        self.todo_domain_service = TodoDomainService()

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
            UserNotFoundException: If user does not exist
            RuntimeError: If todo creation fails (handled by exception handler)

        Note:
            Basic validation (title length, etc.) is handled by API DTOs.
            This method focuses on business logic only.
        """
        # Validate that user exists
        self.todo_domain_service.validate_user_exists_for_todo_operation(
            user_id, self.user_repository
        )

        todo = Todo.create(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
        )
        return self.todo_repository.save(todo)
