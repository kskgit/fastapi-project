"""Delete User UseCase implementation."""

from app.domain.repositories.user_repository import UserRepository
from app.domain.services.transaction_manager import TransactionManager


class DeleteUserUseCase:
    """UseCase for deleting a User.

    Single Responsibility: Handle the deletion of a user with proper
    validation and error handling.

    Dependencies:
    - Only depends on Domain layer (UserRepository interface)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(
        self, transaction_manager: TransactionManager, user_repository: UserRepository
    ):
        """Initialize with transaction manager and repository dependencies.

        Args:
            transaction_manager: Transaction manager for database operations
            user_repository: UserRepository interface implementation
        """
        self.transaction_manager = transaction_manager
        self.user_repository = user_repository

    async def execute(self, user_id: int) -> bool:
        """Execute the delete user use case.

        Args:
            user_id: ID of the user to delete

        Returns:
            bool: True if deleted successfully, False if not found

        Raises:
            RuntimeError: If user deletion fails

        Note:
            This is a soft delete operation - the user is marked as deleted
            but not physically removed from the database.
            Transaction management is handled explicitly within this method.
        """
        async with (
            self.transaction_manager.begin_transaction()
        ):  # Explicit transaction boundary
            # Check if user exists
            user = await self.user_repository.find_by_id(user_id)
            if not user:
                return False  # User doesn't exist

            return await self.user_repository.delete(user_id)
        # Transaction automatically commits on success or rolls back on exception
