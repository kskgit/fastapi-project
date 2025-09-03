"""Domain layer exceptions.

This module contains all domain-specific exceptions used throughout the application.
All exceptions are defined here to maintain consistency and enable centralized
error handling.
"""

from .business import (
    BaseUserException,
    ResourceNotFoundException,
    StateTransitionException,
    TodoNotFoundException,
    UniqueConstraintException,
    UserNotFoundException,
    ValidationException,
)
from .system import (
    ConnectionException,
    SystemException,
)

__all__ = [
    "BaseException",
    "ValidationException",
    "ResourceNotFoundException",
    "UniqueConstraintException",
    "StateTransitionException",
    "UserNotFoundException",
    "TodoNotFoundException",
    "SystemException",
    "ConnectionException",
    "BaseUserException",
]
