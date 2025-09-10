"""Base repository class with automatic exception handling."""

import inspect
import traceback

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.system import DataPersistenceException


class BaseRepository:
    """Base repository class providing common exception handling functionality.

    This class provides automatic method name detection and standardized
    exception handling to reduce boilerplate code in concrete repository
    implementations.
    """

    def __init__(self, db: AsyncSession):
        """Initialize with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    def _get_current_method_name(self) -> str:
        """Get the name of the calling method automatically.

        Uses inspect.stack() to determine the method that called _handle_exception.
        This eliminates the need to manually specify operation names.

        Returns:
            Name of the calling method
        """
        # stack[0] = _get_current_method_name
        # stack[1] = _handle_exception
        # stack[2] = calling repository method
        stack = inspect.stack()
        if len(stack) >= 3:
            return stack[2].function
        return "unknown_method"

    def _handle_exception(
        self,
        e: Exception,
        message: str,
        entity_type: str,
        entity_id: int | str | None = None,
    ) -> None:
        """Handle repository exceptions with automatic method detection.

        This method provides standardized exception handling that:
        - Automatically detects the calling method name
        - Captures stack traces for debugging
        - Wraps all exceptions in DataPersistenceException format
        - Provides consistent error structure across repositories

        Args:
            e: Original exception that occurred
            message: Human-readable error message
            entity_type: Type of entity being operated on (user, todo, etc.)
            entity_id: ID of the specific entity (optional)

        Raises:
            DataPersistenceException: Standardized exception with context
        """
        method_name = self._get_current_method_name()

        raise DataPersistenceException(
            message=message,
            method_name=method_name,
            entity_type=entity_type,
            entity_id=entity_id,
            details={
                "original_exception_type": e.__class__.__name__,
                "original_message": str(e),
                "stack_trace": traceback.format_exc(),
            },
        )
