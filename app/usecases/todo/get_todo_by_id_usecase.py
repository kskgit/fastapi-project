from app.domain.entities import Todo
from app.domain.exceptions import TodoNotFoundException
from app.domain.repositories import TodoRepository, UserRepository
from app.domain.services import TodoDomainService


class GetTodoByIdUseCase:
    """UseCase for retrieving a specific todo by ID.

    Single Responsibility: Handle the retrieval of a single todo with
    proper ownership validation.

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

    async def execute(self, todo_id: int, user_id: int) -> Todo:
        """Execute the get todo by ID use case.

        Args:
            todo_id: ID of the todo to retrieve
            user_id: Optional user ID for ownership validation

        Returns:
            Todo: The requested todo entity

        Raises:
            TodoNotFoundException: If todo not found or user doesn't own the todo
            UserNotFoundException: If user not found

        Note:
            If user_id is provided, ownership validation is performed.
            If user_id is None, returns todo regardless of ownership (admin access).
            Domain exceptions are handled by FastAPI exception handlers in main.py.
        """
        todo = await self.todo_repository.find_by_id(todo_id)
        if not todo:
            raise TodoNotFoundException(todo_id)

        # Validate that user exists
        await self.todo_domain_service.validate_user(user_id, self.user_repository)

        # Validate todo ownership
        self.todo_domain_service.validate_todo_ownership(todo, user_id)

        return todo
