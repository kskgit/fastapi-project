"""System-related domain exceptions.

This module contains exceptions related to system operations
that affect domain functionality, such as data persistence failures,
external service connectivity issues, etc.

These exceptions abstract away technical implementation details
while preserving the essential error information for domain operations.
"""

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
        trace: str,
    ) -> None:
        """Initialize system exception.

        Args:
            message: Human-readable error message describing the system issue
            error_code: Unique error code (defaults to class name)
            details: Additional context information about the system failure
        """
        details = {"stack_trace": trace}
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
        trace: str,
        message: str | None = None,
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
            trace=trace,
        )

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        """Connection errors indicate service unavailable."""
        return ExceptionStatusCode.SERVICE_UNAVAILABLE


class DataOperationException(SystemException):
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
        trace: str,
        operation_context: object | None = None,
        operation_name: str | None = None,
    ) -> None:
        """Initialize data persistence exception.

        Args:
            trace: Stack trace information for debugging
            operation_context: Object context (typically self) to extract class and
                method names
            operation_name: Optional manual specification of operation name
        """
        context_info = self._extract_context_info(operation_context, operation_name)
        message = f"Failed to execute data operation in {context_info}"

        super().__init__(
            message=message,
            trace=trace,
        )

    def _extract_context_info(
        self, operation_context: object | None, operation_name: str | None
    ) -> str:
        """Extract context information from operation context or name.

        Args:
            operation_context: Object context (typically self)
            operation_name: Manual operation name specification

        Returns:
            str: Context information for error message
        """
        if operation_name:
            return operation_name

        if operation_context:
            try:
                import inspect

                class_name = operation_context.__class__.__name__

                # Get caller method name by traversing stack frames
                frame = inspect.currentframe()
                if frame and frame.f_back and frame.f_back.f_back:
                    method_name = frame.f_back.f_back.f_code.co_name
                    return f"{class_name}.{method_name}"
                else:
                    return class_name
            except Exception:
                # Fallback to class name only if frame inspection fails
                return operation_context.__class__.__name__

        return "unknown operation"
