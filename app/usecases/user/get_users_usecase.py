"""Get Users UseCase implementation."""

from app.domain.entities.user import User
from app.domain.exceptions import ValidationException
from app.domain.repositories.user_repository import UserRepository


class GetUsersUseCase:
    """UseCase for retrieving users with pagination.

    Single Responsibility: Handle the retrieval of users with
    proper pagination and filtering options.

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

    async def execute(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Execute the get users use case.

        Args:
            skip: Number of users to skip for pagination
            limit: Maximum number of users to return

        Returns:
            list[User]: List of users matching the criteria

        Raises:
            ValueError: If invalid pagination parameters
            RuntimeError: If user retrieval fails

        Note:
            Pagination validation is handled here as business logic.
        """
        try:
            # Validate pagination parameters
            if limit > 1000:
                raise ValidationException(
                    "Limit cannot exceed 1000", field_name="limit"
                )
            if skip < 0:
                raise ValidationException("Skip cannot be negative", field_name="skip")

            all_users = await self.user_repository.find_all()
            # Apply pagination manually
            return all_users[skip : skip + limit]
        except ValueError:
            # Re-raise ValueError as-is for proper API error handling
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to get users: {str(e)}") from e
