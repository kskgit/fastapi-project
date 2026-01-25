"""Get Users UseCase implementation."""

from app.domain.entities import User
from app.domain.repositories import UserRepository
from app.domain.services import UserDomainService


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
        self.user_domain_service = UserDomainService()

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
            Pagination validation is handled by domain service as business logic.
        """
        # Validate pagination parameters using domain service
        self.user_domain_service.validate_pagination_parameters(skip, limit)

        all_users = await self.user_repository.find_all()
        # Apply pagination manually
        return all_users[skip : skip + limit]
