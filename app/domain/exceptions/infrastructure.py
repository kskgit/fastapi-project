"""Infrastructure-related domain exceptions.

This module contains exceptions related to infrastructure operations
that affect domain functionality, such as data persistence failures,
external service connectivity issues, etc.

These exceptions abstract away technical implementation details
while preserving the essential error information for domain operations.
"""

from typing import Any

from .base import DomainException


class InfrastructureException(DomainException):
    """Base exception for infrastructure-related errors affecting domain operations.

    This exception is raised when infrastructure layer problems prevent
    domain operations from completing successfully. It abstracts away
    technical implementation details while providing meaningful error
    information to the domain layer.

    Examples:
        - Data persistence connection failures
        - External service unavailability
        - Configuration service errors
        - File system access problems
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize infrastructure exception.

        Args:
            message: Human-readable error message describing the infrastructure issue
            error_code: Unique error code (defaults to class name)
            details: Additional context information about the infrastructure failure
        """
        super().__init__(
            message=message,
            error_code=error_code or "infrastructure_error",
            details=details,
        )


class ConnectionException(InfrastructureException):
    """Exception raised when data persistence connection fails.

    This exception is raised when the application cannot establish or maintain
    a connection to the data persistence layer. It abstracts away specific
    storage technology details (database, file system, cloud storage, etc.)
    and focuses on the domain-level impact: data cannot be persisted or retrieved.

    Note:
        This exception does not reference specific technologies like "database",
        "SQL", or vendor-specific terms. It represents the abstract concept of
        data persistence connection failure from a domain perspective.
    """

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize connection exception.

        Args:
            message: Optional custom error message.
            If not provided, uses default message.
            details: Additional context information about the connection failure
        """
        default_message = "Failed to establish connection to data persistence layer"
        final_message = message or default_message

        super().__init__(
            message=final_message,
            error_code="connection_failed",
            details=details,
        )
