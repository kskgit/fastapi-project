"""Get User by ID UseCase implementation."""

from app.domain.entities.user import User
from app.domain.exceptions import UserNotFoundException
from app.domain.repositories.user_repository import UserRepository


class GetUserByIdUseCase:
    """UseCase for retrieving a specific user by ID.

    Single Responsibility: Handle the retrieval of a single user with
    proper validation and error handling.

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

    def execute(self, user_id: int) -> User:
        """Execute the get user by ID use case.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            User: The requested user entity

        Raises:
            UserNotFoundException: If user not found

        Note:
            Exceptions are handled by FastAPI exception handlers in main.py.
        """
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)

        return user
