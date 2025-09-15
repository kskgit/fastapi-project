"""System-related domain exceptions.

This module contains exceptions related to system operations
that affect domain functionality, such as data persistence failures,
external service connectivity issues, etc.

These exceptions abstract away technical implementation details
while preserving the essential error information for domain operations.
"""

from typing import Any

from app.domain.exceptions.base import BaseCustomException, ExceptionStatusCode


class SystemException(BaseCustomException):
    """Base exception for system-related errors affecting domain operations.

    This exception is raised when system layer problems prevent
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
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize system exception.

        Args:
            message: Human-readable error message describing the system issue
            error_code: Unique error code (defaults to class name)
            details: Additional context information about the system failure
        """
        super().__init__(message, details)

    def get_log_level(self) -> str:
        """Get log level for system exceptions."""
        return "ERROR"

    def should_trigger_alert(self) -> bool:
        """System errors should trigger operational alerts."""
        return True

    def get_error_category(self) -> str:
        """Get error category for system exceptions."""
        return "system_error"

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        """System errors default to 500 Internal Server Error."""
        return ExceptionStatusCode.INTERNAL_SERVER_ERROR


class ConnectionException(SystemException):
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
            details=details,
        )

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        """Connection errors indicate service unavailable."""
        return ExceptionStatusCode.SERVICE_UNAVAILABLE


class DataPersistenceException(SystemException):
    """Exception raised when data persistence operations fail.

    This exception is raised when the application cannot successfully
    perform data persistence operations such as save, update, delete, or find.
    It abstracts away specific storage technology details and focuses on
    the domain-level impact: data operation could not be completed.

    Examples:
        - Failed to save entity due to database constraint violation
        - Failed to update entity due to connection timeout
        - Failed to delete entity due to foreign key constraints
        - Failed to retrieve entity due to query execution error
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize data persistence exception.

        Args:
            message: Human-readable error message describing the persistence failure
            method_name: The method name that failed (automatically detected)
            entity_type: The type of entity involved in the operation
            entity_id: The ID of the specific entity (if applicable)
            details: Additional context information about the persistence failure
        """
        # Build structured details
        structured_details = details or {}

        super().__init__(
            message=message,
            details=structured_details,
        )
