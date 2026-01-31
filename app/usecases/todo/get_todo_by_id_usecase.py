from dataclasses import dataclass

from app.domain.entities import SubTask, Todo
from app.domain.exceptions import TodoNotFoundException
from app.domain.repositories import SubTaskRepository, TodoRepository, UserRepository
from app.domain.services import TodoDomainService


@dataclass
class TodoWithSubtasks:
    """Result of GetTodoByIdUseCase containing todo and its subtasks."""

    todo: Todo
    subtasks: list[SubTask]


class GetTodoByIdUseCase:
    """UseCase for retrieving a specific todo by ID.

    Single Responsibility: Handle the retrieval of a single todo with
    proper ownership validation.

    Dependencies:
    - Only depends on Domain layer (TodoRepository and UserRepository interfaces)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(
        self,
        todo_repository: TodoRepository,
        user_repository: UserRepository,
        subtask_repository: SubTaskRepository,
    ):
        """Initialize with repository dependencies.

        Args:
            todo_repository: TodoRepository interface implementation
            user_repository: UserRepository interface implementation
            subtask_repository: SubTaskRepository interface implementation
        """
        self.todo_repository = todo_repository
        self.user_repository = user_repository
        self.subtask_repository = subtask_repository
        self.todo_domain_service = TodoDomainService()

    async def execute(self, todo_id: int, user_id: int) -> TodoWithSubtasks:
        """Execute the get todo by ID use case.

        Args:
            todo_id: ID of the todo to retrieve
            user_id: User ID for ownership validation

        Returns:
            TodoWithSubtasks: The requested todo entity with its subtasks

        Raises:
            TodoNotFoundException: If todo not found or user doesn't own the todo
            UserNotFoundException: If user not found

        Note:
            Domain exceptions are handled by FastAPI exception handlers in main.py.
        """
        todo = await self.todo_repository.find_by_id(todo_id)
        if not todo:
            raise TodoNotFoundException(todo_id)

        # Validate that user exists
        await self.todo_domain_service.validate_user(user_id, self.user_repository)

        # Validate todo ownership
        self.todo_domain_service.validate_todo_ownership(todo, user_id)

        # Fetch subtasks only after validation passes
        subtasks = await self.subtask_repository.find_by_todo_id(todo_id)

        return TodoWithSubtasks(todo=todo, subtasks=subtasks)
