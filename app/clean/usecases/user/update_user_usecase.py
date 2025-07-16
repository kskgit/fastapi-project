"""Update User UseCase implementation."""

from app.clean.domain.entities.user import User
from app.clean.domain.repositories.user_repository import UserRepository


class UpdateUserUseCase:
    """UseCase for updating an existing User.

    Single Responsibility: Handle the update of a user with proper
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

    def execute(
        self,
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        full_name: str | None = None,
    ) -> User:
        """Execute the update user use case.

        Args:
            user_id: ID of the user to update
            username: Optional new username
            email: Optional new email
            full_name: Optional new full name

        Returns:
            User: Updated user entity

        Raises:
            ValueError: If user not found or validation fails
            RuntimeError: If user update fails

        Note:
            At least one field must be provided for update.
        """
        try:
            # Get the existing user
            user = self.user_repository.find_by_id(user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            # Check that at least one field is being updated
            if all(param is None for param in [username, email, full_name]):
                raise ValueError("At least one field must be provided for update")

            # Check uniqueness constraints if username or email are being updated
            if username is not None and username != user.username:
                existing_user = self.user_repository.find_by_username(username)
                if existing_user and existing_user.id != user_id:
                    raise ValueError(f"Username '{username}' already exists")

            if email is not None and email != user.email:
                existing_user = self.user_repository.find_by_email(email)
                if existing_user and existing_user.id != user_id:
                    raise ValueError(f"Email '{email}' already exists")

            # Update fields if provided
            if username is not None:
                user.username = username
            if email is not None:
                user.email = email
            if full_name is not None:
                user.full_name = full_name

            return self.user_repository.save(user)
        except ValueError:
            # Re-raise ValueError as-is for proper API error handling
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to update user: {str(e)}") from e
