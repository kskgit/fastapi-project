"""Base domain exception classes.

This module defines the base exception classes for the domain layer.
All domain exceptions should inherit from DomainException to enable
unified error handling across the application.
"""

from datetime import datetime
from typing import Any


class DomainException(Exception):
    """Base exception for all domain-related errors.

    This class provides common functionality for all domain exceptions:
    - Error classification and handling
    - Structured error information
    - Debugging support
    - Future extensibility (logging, metrics, etc.)
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize domain exception.

        Args:
            message: Human-readable error message
            error_code: Unique error code (defaults to class name)
            details: Additional error context information
        """
        super().__init__(message)
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary format.

        Useful for API responses and structured logging.

        Returns:
            Dictionary containing exception information
        """
        return {
            "error_code": self.error_code,
            "message": str(self),
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self) -> str:
        """Return string representation of the exception."""
        return super().__str__()

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"message='{str(self)}', "
            f"error_code='{self.error_code}', "
            f"details={self.details})"
        )
