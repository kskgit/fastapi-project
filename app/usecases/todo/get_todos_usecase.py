from app.domain.entities import Todo, TodoPriority, TodoStatus
from app.domain.repositories import TodoRepository, UserRepository
from app.domain.services import TodoDomainService


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
        self.todo_domain_service = TodoDomainService()

    async def execute(
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
            UserNotFoundException: If user not found
            ValueError: If invalid pagination parameters

        Note:
            Pagination validation is handled here as business logic.
            Domain exceptions are handled by FastAPI exception handlers in main.py.
        """
        # Validate that user exists
        await self.todo_domain_service.validate_user(user_id, self.user_repository)

        # Validate pagination parameters
        self.todo_domain_service.validate_pagination_parameters(skip, limit)

        return await self.todo_repository.find_with_pagination(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
        )
