"""SQLAlchemy model definition for users table."""

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.database.connection import Base


class UserModel(Base):  # type: ignore[misc]
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
