"""Create User UseCase implementation."""

from app.clean.domain.entities.user import User
from app.clean.domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    """UseCase for creating a new User.

    Single Responsibility: Handle the creation of a new User with proper
    business logic validation and error handling.

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

    def execute(self, username: str, email: str, full_name: str | None = None) -> User:
        """Execute the create user use case.

        Args:
            username: User's username (required, unique)
            email: User's email address (required, unique)
            full_name: User's full name (optional)

        Returns:
            User: Created user entity

        Raises:
            ValueError: If username or email already exists
            RuntimeError: If user creation fails
        """
        try:
            # Check if username already exists
            if self.user_repository.find_by_username(username):
                raise ValueError(f"Username '{username}' already exists")

            # Check if email already exists
            if self.user_repository.find_by_email(email):
                raise ValueError(f"Email '{email}' already exists")

            # Create new user
            user = User.create(username=username, email=email, full_name=full_name)

            return self.user_repository.save(user)
        except ValueError:
            # Re-raise ValueError as-is for proper API error handling
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to create user: {str(e)}") from e
