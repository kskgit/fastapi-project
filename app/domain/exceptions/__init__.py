"""Domain layer exceptions.

This module contains all domain-specific exceptions used throughout the application.
All exceptions are defined here to maintain consistency and enable centralized
error handling.
"""

from .base import BaseCustomException, ExceptionStatusCode
from .business import (
    BusinessRuleException,
    ResourceNotFoundException,
    StateTransitionException,
    TodoNotFoundException,
    UniqueConstraintException,
    UserNotFoundException,
    UserPermissionDeniedException,
    ValidationException,
)
from .system import (
    ConnectionException,
    DataOperationException,
    SystemException,
)

__all__ = [
    "BaseCustomException",
    "BusinessRuleException",
    "ConnectionException",
    "DataOperationException",
    "ExceptionStatusCode",
    "ResourceNotFoundException",
    "StateTransitionException",
    "SystemException",
    "TodoNotFoundException",
    "UniqueConstraintException",
    "UserNotFoundException",
    "UserPermissionDeniedException",
    "ValidationException",
]
