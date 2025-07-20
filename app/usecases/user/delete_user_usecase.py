"""Delete User UseCase implementation."""

from app.domain.repositories.user_repository import UserRepository


class DeleteUserUseCase:
    """UseCase for deleting a User.

    Single Responsibility: Handle the deletion of a user with proper
    validation and error handling.

    Dependencies:
    - Only depends on Domain layer (UserRepository interface)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(self, user_repository: UserRepository):
        """Initialize with repository dependencies.

        Args:
            user_repository: UserRepository interface implementation
        """
        self.user_repository = user_repository

    def execute(self, user_id: int) -> bool:
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
        """
        try:
            # Check if user exists
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return False  # User doesn't exist

            return self.user_repository.delete(user_id)
        except Exception as e:
            raise RuntimeError(f"Failed to delete user: {str(e)}") from e
