from app.domain.entities.todo import Todo
from app.domain.exceptions import TodoNotFoundException, UserNotFoundException
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository


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

    def execute(self, todo_id: int, user_id: int | None = None) -> Todo:
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
            Exceptions are handled by FastAPI exception handlers in main.py.
        """
        todo = self.todo_repository.find_by_id(todo_id)
        if not todo:
            raise TodoNotFoundException(todo_id)

        # If user_id is provided, validate ownership
        if user_id is not None:
            # Validate that user exists
            if not self.user_repository.exists(user_id):
                raise UserNotFoundException(user_id)

            # Validate todo ownership
            if todo.user_id != user_id:
                raise TodoNotFoundException(todo_id)  # Don't reveal existence

        return todo
