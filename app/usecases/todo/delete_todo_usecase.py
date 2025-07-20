from app.domain.exceptions import UserNotFoundException
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository


class DeleteTodoUseCase:
    """UseCase for deleting a Todo.

    Single Responsibility: Handle the deletion of a todo with proper
    ownership validation and user existence checks.

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

    def execute(self, todo_id: int, user_id: int) -> bool:
        """Execute the delete todo use case.

        Args:
            todo_id: ID of the todo to delete
            user_id: ID of the user requesting the deletion

        Returns:
            bool: True if deleted successfully, False if not found

        Raises:
            UserNotFoundException: If user not found

        Note:
            Only the todo owner can delete their todos.
            Exceptions are handled by FastAPI exception handlers in main.py.
        """
        # Validate that user exists
        if not self.user_repository.exists(user_id):
            raise UserNotFoundException(user_id)

        # Get the existing todo to validate ownership
        todo = self.todo_repository.find_by_id(todo_id)
        if not todo:
            return False  # Todo doesn't exist

        # Validate ownership
        if todo.user_id != user_id:
            return False  # Don't reveal existence of other users' todos

        return self.todo_repository.delete(todo_id)
