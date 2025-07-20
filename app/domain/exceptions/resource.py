"""Resource-related domain exceptions.

This module contains exceptions related to resource operations
such as not found errors, access denied, etc.
"""

from typing import Any

from .base import DomainException


class ResourceNotFoundException(DomainException):
    """Base exception for resource not found errors.

    This exception is raised when a requested resource cannot be found.
    It provides a consistent format for "not found" errors across all resources.
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize resource not found exception.

        Args:
            resource_type: Type of resource (e.g., "User", "Todo")
            resource_id: ID of the resource that was not found
            details: Additional context information
        """
        message = f"{resource_type} with id {resource_id} not found"
        error_code = f"{resource_type.lower()}_not_found"

        # Include resource information in details
        exception_details = details or {}
        exception_details.update(
            {
                "resource_type": resource_type,
                "resource_id": resource_id,
            }
        )

        super().__init__(
            message=message,
            error_code=error_code,
            details=exception_details,
        )

        self.resource_type = resource_type
        self.resource_id = resource_id


class UserNotFoundException(ResourceNotFoundException):
    """Exception raised when a user is not found.

    This exception is raised when attempting to access or modify a user
    that does not exist in the system.
    """

    def __init__(
        self,
        user_id: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize user not found exception.

        Args:
            user_id: ID of the user that was not found
            details: Additional context information
        """
        super().__init__(
            resource_type="User",
            resource_id=user_id,
            details=details,
        )


class TodoNotFoundException(ResourceNotFoundException):
    """Exception raised when a todo is not found.

    This exception is raised when attempting to access or modify a todo
    that does not exist in the system.
    """

    def __init__(
        self,
        todo_id: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize todo not found exception.

        Args:
            todo_id: ID of the todo that was not found
            details: Additional context information
        """
        super().__init__(
            resource_type="Todo",
            resource_id=todo_id,
            details=details,
        )
