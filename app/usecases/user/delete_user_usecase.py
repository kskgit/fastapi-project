"""Delete User UseCase implementation."""

from app.core import TransactionManager
from app.domain.repositories import TodoRepository, UserRepository


class DeleteUserUseCase:
    """UseCase for deleting a User.

    Single Responsibility: Handle the deletion of a user with proper
    validation and error handling. Also handles cascade deletion of
    related todos in the same transaction.

    Dependencies:
    - Only depends on Domain layer (UserRepository, TodoRepository interfaces)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(
        self,
        transaction_manager: TransactionManager,
        user_repository: UserRepository,
        todo_repository: TodoRepository,
    ):
        """Initialize with transaction manager and repository dependencies.

        Args:
            transaction_manager: Transaction manager for database operations
            user_repository: UserRepository interface implementation
            todo_repository: TodoRepository interface implementation
        """
        self.transaction_manager = transaction_manager
        self.user_repository = user_repository
        self.todo_repository = todo_repository

    async def execute(self, user_id: int) -> bool:
        """Execute the delete user use case.

        Args:
            user_id: ID of the user to delete

        Returns:
            bool: True if deleted successfully, False if not found

        Raises:
            RuntimeError: If user or todo deletion fails

        Note:
            This operation deletes the user and all related todos in a single
            transaction.
            Transaction management is handled explicitly within this method.
            If any operation fails, all changes are rolled back.
        """
        async with (
            self.transaction_manager.begin_transaction()
        ):  # Explicit transaction boundary
            # Check if user exists
            user = await self.user_repository.find_by_id(user_id)
            if not user:
                return False  # User doesn't exist

            # First, delete all todos associated with the user
            await self.todo_repository.delete_all_by_user_id(user_id)

            # Then delete the user
            user_deleted = await self.user_repository.delete(user_id)

            if not user_deleted:
                raise RuntimeError(f"Failed to delete user with id {user_id}")

            return True
        # Transaction automatically commits on success or rolls back on exception
