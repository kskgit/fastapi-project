from app.core.transaction_manager import TransactionManager
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.todo_domain_service import TodoDomainService


class DeleteTodoUseCase:
    """UseCase for deleting a Todo.

    Single Responsibility: Handle the deletion of a todo with proper
    ownership validation and user existence checks.

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

    async def execute(self, todo_id: int, user_id: int) -> bool:
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
            Domain exceptions are handled by FastAPI exception handlers in main.py.
            Transaction management is handled explicitly within this method.
        """
        async with (
            self.transaction_manager.begin_transaction()
        ):  # Explicit transaction boundary
            # Validate that user exists
            await self.todo_domain_service.validate_user_exists_for_todo_operation(
                user_id, self.user_repository
            )

            # Get the existing todo to validate ownership
            todo = await self.todo_repository.find_by_id(todo_id)
            if not todo:
                return False  # Todo doesn't exist

            # Validate ownership
            self.todo_domain_service.validate_todo_ownership(todo, user_id)

            return await self.todo_repository.delete(todo_id)
        # Transaction automatically commits on success or rolls back on exception
