"""Todo Domain Service - Business logic for Todo entity operations."""

from app.domain.entities import Todo
from app.domain.exceptions import (
    TodoNotFoundException,
    UserNotFoundException,
    ValidationException,
)
from app.domain.repositories import UserRepository


class TodoDomainService:
    """Domain Service for Todo business logic.

    Handles complex business rules that involve multiple entities
    or require repository interactions while keeping the Entity pure.
    """

    async def validate_user(
        self, user_id: int, user_repository: UserRepository
    ) -> None:
        """Todo操作前のユーザチェック.

        Args:
            user_id: User ID to validate
            user_repository: Repository for user data access

        Raises:
            UserNotFoundException: If user does not exist

        Note:
            This is a domain rule: Todo operations require valid users.
        """
        if not await user_repository.exists(user_id):
            raise UserNotFoundException(user_id)

    def validate_todo_ownership(self, todo: Todo, user_id: int) -> None:
        """Validate that user owns the todo.

        Args:
            todo: Todo entity to check ownership
            user_id: User ID claiming ownership

        Raises:
            TodoNotFoundException: If user doesn't own the todo

        Note:
            This is a domain rule: Users can only access their own todos.
            We use TodoNotFoundException instead of a permission error
            to avoid revealing existence of other users' todos.
        """
        if todo.user_id != user_id:
            raise TodoNotFoundException(todo.id or 0)

    def validate_pagination_parameters(self, skip: int, limit: int) -> None:
        """Validate pagination parameters.

        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return

        Raises:
            ValueError: If parameters are invalid

        Note:
            This is a domain rule: System pagination limits for performance.
        """
        if limit > 1000:
            raise ValidationException("Limit cannot exceed 1000", field_name="limit")
        if skip < 0:
            raise ValidationException("Skip cannot be negative", field_name="skip")

    def validate_update_fields_provided(self, *fields: object) -> None:
        """Validate that at least one field is provided for update.

        Args:
            *fields: Variable number of field values to check

        Raises:
            ValueError: If no fields are provided for update

        Note:
            This is a domain rule: Update operations must modify at least one field.
        """
        if all(field is None for field in fields):
            raise ValidationException("At least one field must be provided for update")
