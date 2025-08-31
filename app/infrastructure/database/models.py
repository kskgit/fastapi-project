from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func

from app.domain.entities.todo import TodoPriority, TodoStatus
from app.infrastructure.database.connection import Base


class UserModel(Base):
    """SQLAlchemy Model for User - Infrastructure layer concern only."""

    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True)
    username = mapped_column(String(50), unique=True, index=True, nullable=False)
    email = mapped_column(String(100), unique=True, index=True, nullable=False)
    full_name = mapped_column(String(100), nullable=True)
    is_active = mapped_column(Boolean, default=True, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship to todos
    todos = relationship(
        "TodoModel", back_populates="user", cascade="all, delete-orphan"
    )


class TodoModel(Base):
    """SQLAlchemy Model for Todo - Infrastructure layer concern only."""

    __tablename__ = "todos"

    id = mapped_column(Integer, primary_key=True, index=True)
    title = mapped_column(String(100), index=True, nullable=False)
    description = mapped_column(String(500), nullable=True)
    due_date = mapped_column(DateTime(timezone=True), nullable=True)
    status = mapped_column(Enum(TodoStatus), default=TodoStatus.pending, index=True)
    priority = mapped_column(Enum(TodoPriority), default=TodoPriority.medium)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship to user
    user = relationship("UserModel", back_populates="todos")
