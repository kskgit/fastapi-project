"""SQLAlchemy implementation of SubTaskRepository."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import SubTask
from app.domain.repositories import SubTaskRepository
from app.infrastructure.database.models import SubTaskModel


class SQLAlchemySubTaskRepository(SubTaskRepository):
    """SQLAlchemy implementation of SubTaskRepository.

    Handles database operations using SQLAlchemy ORM with async/await support.
    Converts between domain entities and SQLAlchemy models.
    """

    def __init__(self, db: AsyncSession):
        """Initialize with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    def _to_domain_entity(self, model: SubTaskModel) -> SubTask:
        """Convert SQLAlchemy model to domain entity."""
        return SubTask(
            id=model.id,
            user_id=model.user_id,
            todo_id=model.todo_id,
            title=model.title,
            is_compleated=model.is_compleated,
        )

    def _to_model(self, entity: SubTask) -> SubTaskModel:
        """Convert domain entity to SQLAlchemy model."""
        return SubTaskModel(
            id=entity.id,
            user_id=entity.user_id,
            todo_id=entity.todo_id,
            title=entity.title,
            is_compleated=entity.is_compleated,
        )

    async def create(self, subtask: SubTask) -> SubTask:
        """Persist a new subtask.

        Note: Transaction management is handled by the caller.
        Always flushes to ensure ID is available for return value.
        """
        if subtask.id is not None:
            raise ValueError("Cannot create subtask with existing id")

        try:
            model = self._to_model(subtask)
            self.db.add(model)
            await self.db.flush()
            await self.db.refresh(model)
            return self._to_domain_entity(model)
        except SQLAlchemyError as e:
            raise e
