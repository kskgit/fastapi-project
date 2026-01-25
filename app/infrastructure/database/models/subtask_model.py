"""SQLAlchemy model definition for subtasks table."""

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column

from app.infrastructure.database import Base


class SubTaskModel(Base):  # type: ignore[misc]
    """SQLAlchemy Model for SubTask - Infrastructure layer concern only."""

    __tablename__ = "subtasks"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    todo_id = mapped_column(Integer, ForeignKey("todos.id"), nullable=False, index=True)
    title = mapped_column(String(100), nullable=False)
    is_compleated = mapped_column(Boolean, default=False, nullable=False)
