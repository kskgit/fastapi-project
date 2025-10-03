"""Business rule related exceptions.

This module contains exceptions for business logic violations,
providing unified logging and monitoring capabilities while allowing
specific HTTP response codes for different types of business rules.
"""

from typing import Any

from app.domain.exceptions.base import BaseCustomException, ExceptionStatusCode


class BusinessRuleException(BaseCustomException):
    """Base exception for business rule violations.

    This exception provides unified handling for user-caused business logic
    errors with consistent WARNING level logging and monitoring behavior.
    """

    def get_log_level(self) -> str:
        """Business rule violations are logged at WARNING level."""
        return "WARNING"

    def should_trigger_alert(self) -> bool:
        """Business rule violations should not trigger operational alerts."""
        return False

    def get_error_category(self) -> str:
        """Get error category for business rule violations."""
        return "business_rule_violation"


class ValidationException(BusinessRuleException):
    """Exception raised for input validation errors.

    This exception is raised when input data fails validation rules
    such as format constraints, length limits, or required field checks.
    It represents client-side errors that can be fixed by providing
    correct input data.

    Usage:
        - API layer input validation
        - DTO field validation
        - Parameter validation
        - Format validation

    Examples:
        - Empty required fields
        - Invalid email format
        - String length violations
        - Numeric range violations
    """

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize validation exception.

        Args:
            message: Human-readable error message describing the validation failure
            field_name: Optional name of the field that failed validation
            details: Additional context information about the validation failure
        """
        # Include field name in details if provided
        exception_details = details or {}
        if field_name:
            exception_details["field_name"] = field_name

        super().__init__(message=message, details=exception_details)
        self.field_name = field_name

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        """Get HTTP status code for validation errors.

        Returns:
            BusinessRuleExceptionStatusCode: 400 Bad Request for validation errors
        """
        return ExceptionStatusCode.VALIDATION_ERR


class UniqueConstraintException(BusinessRuleException):
    """Exception raised for uniqueness constraint violations.

    This represents a business rule where certain fields or combinations
    must be unique across the system.
    """

    def __init__(
        self,
        message: str,
        constraint_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize unique constraint exception.

        Args:
            message: Human-readable error message
            constraint_name: Name of the constraint that was violated
            details: Additional context information
        """
        exception_details = details or {}
        if constraint_name:
            exception_details["constraint_name"] = constraint_name

        super().__init__(message=message, details=exception_details)
        self.constraint_name = constraint_name

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        return ExceptionStatusCode.UNPROCESSABLE_ENTITY


class StateTransitionException(BusinessRuleException):
    """Exception raised for invalid state transitions.

    This represents a business rule where entities can only transition
    between certain states according to business logic.
    """

    def __init__(
        self,
        message: str,
        current_state: str | None = None,
        attempted_state: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize state transition exception.

        Args:
            message: Human-readable error message
            current_state: Current state of the entity
            attempted_state: State that was attempted to transition to
            details: Additional context information
        """
        exception_details = details or {}
        if current_state:
            exception_details["current_state"] = current_state
        if attempted_state:
            exception_details["attempted_state"] = attempted_state

        super().__init__(message=message, details=exception_details)
        self.current_state = current_state
        self.attempted_state = attempted_state

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        """Get HTTP status code for state transition violations.

        Returns:
            BusinessRuleExceptionStatusCode: 422 Unprocessable
            Entity for business logic violations
        """
        return ExceptionStatusCode.UNPROCESSABLE_ENTITY


class ResourceNotFoundException(BusinessRuleException):
    """Exception raised when a requested resource cannot be found.

    This represents a business rule violation where operations can only
    be performed on existing resources in the system.
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
        super().__init__(message=message)

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        """Get HTTP status code for resource not found errors.

        Returns:
            BusinessRuleExceptionStatusCode: 404 Not Found for missing resources
        """
        return ExceptionStatusCode.NOT_FOUND


class UserNotFoundException(ResourceNotFoundException):
    """Exception raised when a user is not found."""

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
    """Exception raised when a todo is not found."""

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
