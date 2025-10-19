from datetime import datetime

from app.domain.entities.todo import Todo, TodoPriority
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.transaction_manager import TransactionManager
from app.domain.services.user_domain_service import UserDomainService


class CreateTodoUseCase:
    """UseCase for creating a new Todo.

    Single Responsibility: Handle the creation of a new Todo with proper
    business logic validation and error handling using async/await.

    Dependencies:
    - Only depends on Domain layer (TodoRepository and UserRepository interfaces)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(
        self,
        transaction_manager: TransactionManager,
        todo_repository: TodoRepository,
        user_repository: UserRepository,
        user_domain_service: UserDomainService,
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
        self.user_domain_service = user_domain_service

    async def execute(
        self,
        title: str,
        user_id: int,
        description: str | None = None,
        due_date: datetime | None = None,
        priority: TodoPriority = TodoPriority.medium,
    ) -> Todo:
        """Execute the create todo use case asynchronously.

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
            RuntimeError: If todo creation fails

        Note:
            Domain exceptions are handled by FastAPI exception handlers in main.py.

        Note:
            Basic validation (title length, etc.) is handled by API DTOs.
            This method focuses on business logic only.
            Transaction management is handled by SQLAlchemy autobegin.
        """
        async with self.transaction_manager.begin_transaction():
            await self.user_domain_service.validate_user_exists(
                user_id, user_repository=self.user_repository
            )

            todo = Todo.create(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
            )
            return await self.todo_repository.create(todo)
