"""Transaction Manager interface for UseCase layer."""

from abc import ABC, abstractmethod
from typing import Any


class TransactionManager(ABC):
    """Abstract Transaction Manager for UseCase layer.

    Provides transaction management without exposing SQLAlchemy details
    to maintain Clean Architecture boundaries.
    """

    @abstractmethod
    def begin_transaction(self) -> Any:
        """Begin a database transaction.

        Returns:
            Async context manager for transaction scope

        Usage:
            async with transaction_manager.begin_transaction():
                # Business logic operations
                pass
        """
        pass
