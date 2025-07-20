from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository


class GetTodosUseCase:
    """UseCase for retrieving todos with pagination and filtering.

    Single Responsibility: Handle the retrieval of todos for a specific user
    with proper pagination and filtering options.

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
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> list[Todo]:
        """Execute the get todos use case.

        Args:
            user_id: User ID to get todos for
            skip: Number of todos to skip for pagination
            limit: Maximum number of todos to return
            status: Optional status filter
            priority: Optional priority filter

        Returns:
            list[Todo]: List of todos matching the criteria

        Raises:
            ValueError: If user not found or invalid pagination parameters
            RuntimeError: If todo retrieval fails

        Note:
            Pagination validation is handled here as business logic.
        """
        try:
            # Validate that user exists
            if not self.user_repository.exists(user_id):
                raise ValueError(f"User with id {user_id} not found")

            # Validate pagination parameters
            if limit > 1000:
                raise ValueError("Limit cannot exceed 1000")
            if skip < 0:
                raise ValueError("Skip cannot be negative")

            return self.todo_repository.find_with_pagination(
                user_id=user_id,
                skip=skip,
                limit=limit,
                status=status,
                priority=priority,
            )
        except ValueError:
            # Re-raise ValueError as-is for proper API error handling
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to get todos: {str(e)}") from e
