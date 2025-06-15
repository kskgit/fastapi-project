from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from app.core.database import Base
from app.todo.schemas.todo import TodoPriority, TodoStatus


class Todo(Base):
    __tablename__ = "todos"

    id = mapped_column(Integer, primary_key=True, index=True)
    title = mapped_column(String(100), index=True, nullable=False)
    description = mapped_column(String(500), nullable=True)
    due_date = mapped_column(DateTime(timezone=True), nullable=True)
    status = mapped_column(Enum(TodoStatus), default=TodoStatus.pending, index=True)
    priority = mapped_column(Enum(TodoPriority), default=TodoPriority.medium)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
