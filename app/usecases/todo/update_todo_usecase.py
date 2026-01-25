from datetime import datetime

from app.core import TransactionManager
from app.domain.entities import Todo, TodoPriority, TodoStatus
from app.domain.exceptions import TodoNotFoundException
from app.domain.repositories import TodoRepository, UserRepository
from app.domain.services import TodoDomainService


class UpdateTodoUseCase:
    """UseCase for updating an existing Todo.

    Single Responsibility: Handle the update of a todo with proper
    business logic validation, ownership checks, and user existence validation.

    Dependencies:
    - Only depends on Domain layer (TodoRepository and UserRepository interfaces)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(
        self,
        transaction_manager: TransactionManager,
        todo_repository: TodoRepository,
        user_repository: UserRepository,
    ):
        """Initialize with transaction manager and repository dependencies.

        Args:
            transaction_manager: Transaction manager for database operations
            todo_repository: TodoRepository interface implementation
            user_repository: UserRepository interface implementation
        """
        self.transaction_manager = transaction_manager
        self.todo_repository = todo_repository
        self.user_repository = user_repository
        self.todo_domain_service = TodoDomainService()

    async def execute(
        self,
        todo_id: int,
        user_id: int,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> Todo:
        """Execute the update todo use case.

        Args:
            todo_id: ID of the todo to update
            user_id: ID of the user requesting the update
            title: Optional new title
            description: Optional new description
            due_date: Optional new due date
            status: Optional new status
            priority: Optional new priority

        Returns:
            Todo: Updated todo entity

        Raises:
            UserNotFoundException: If user not found
            TodoNotFoundException: If todo not found or ownership validation fails
            ValueError: If validation fails (no fields to update)

        Note:
            Only the todo owner can update their todos.
            At least one field must be provided for update.
            Domain exceptions are handled by FastAPI exception handlers in main.py.
            Transaction management is handled explicitly within this method.
        """
        async with self.transaction_manager.begin_transaction():
            await self.todo_domain_service.validate_user(
                user_id=user_id,
                user_repository=self.user_repository,
            )

            todo = await self.todo_repository.find_by_id(todo_id)
            if not todo:
                raise TodoNotFoundException(todo_id)

            todo.update(
                user_id,
                self.user_repository,
                self.todo_domain_service,
                title,
                description,
                due_date,
                status,
                priority,
            )
            return await self.todo_repository.update(todo)
