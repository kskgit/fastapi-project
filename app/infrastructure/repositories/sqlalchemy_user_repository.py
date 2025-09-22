"""SQLAlchemy implementation of UserRepository."""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.exceptions.system import DataOperationException
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository.

    Handles database operations using SQLAlchemy ORM with async/await support.
    Converts between domain entities and SQLAlchemy models.
    """

    def __init__(self, db: AsyncSession):
        """Initialize with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    def _to_domain_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            full_name=model.full_name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to SQLAlchemy model."""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            full_name=entity.full_name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def save(self, user: User) -> User:
        """Save a user (create or update).

        Note: Transaction management is handled by the UseCase layer.
        Always flushes to ensure ID is available for return value.
        """
        try:
            if user.id is None:
                # Create new user
                model = self._to_model(user)
                model.created_at = datetime.now()
                model.updated_at = datetime.now()
                self.db.add(model)
                await self.db.flush()
                await self.db.refresh(model)
            else:
                # Update existing user
                result = await self.db.execute(
                    select(UserModel).where(UserModel.id == user.id)
                )
                model_or_none = result.scalar_one_or_none()
                if model_or_none is None:
                    raise ValueError(f"User with id {user.id} not found")
                model = model_or_none

                # Update fields
                model.username = user.username
                model.email = user.email
                model.full_name = user.full_name
                model.is_active = user.is_active
                model.updated_at = datetime.now()
                await self.db.flush()
                await self.db.refresh(model)

            return self._to_domain_entity(model)

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while saving user: {str(e)}")

    async def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID."""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()
            return self._to_domain_entity(model) if model else None

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding user by id: {str(e)}")

    async def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.username == username)
            )
            model = result.scalar_one_or_none()
            return self._to_domain_entity(model) if model else None

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while finding user by username: {str(e)}"
            )

    async def find_by_email(self, email: str) -> User | None:
        """Find user by email."""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )
            model = result.scalar_one_or_none()
            return self._to_domain_entity(model) if model else None

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding user by email: {str(e)}")

    async def find_all(self) -> list[User]:
        """Find all users."""
        try:
            result = await self.db.execute(select(UserModel))
            models: Sequence[UserModel] = result.scalars().all()
            return [self._to_domain_entity(model) for model in models]

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding all users: {str(e)}")

    async def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()

            if model is None:
                return False

            await self.db.delete(model)
            return True

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while deleting user: {str(e)}")

    async def exists(self, user_id: int) -> bool:
        """Check if user exists."""
        try:
            result = await self.db.execute(
                select(UserModel.id).where(UserModel.id == user_id)
            )
            return result.scalar_one_or_none() is not None

        except (OSError, SQLAlchemyError):
            raise DataOperationException(
                operation_context=self,
            )

    async def count_total(self) -> int:
        """Count total users."""
        try:
            from sqlalchemy import func

            result = await self.db.execute(select(func.count(UserModel.id)))
            return result.scalar() or 0

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while counting total users: {str(e)}")
