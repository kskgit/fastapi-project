"""Domain layer exceptions.

This module contains all domain-specific exceptions used throughout the application.
All exceptions are defined here to maintain consistency and enable centralized
error handling.
"""

from .base import DomainException
from .infrastructure import (
    ConnectionException,
    InfrastructureException,
)
from .resource import (
    ResourceNotFoundException,
    TodoNotFoundException,
    UserNotFoundException,
)

__all__ = [
    "DomainException",
    "InfrastructureException",
    "ConnectionException",
    "ResourceNotFoundException",
    "TodoNotFoundException",
    "UserNotFoundException",
]
