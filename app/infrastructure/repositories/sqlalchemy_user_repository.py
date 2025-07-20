from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository.

    Handles all database-specific concerns including:
    - SQLAlchemy model ↔ Domain entity conversion
    - Query optimization and lazy loading prevention
    - Transaction management
    - Error handling (SQLAlchemy exceptions → domain exceptions)
    """

    def __init__(self, db: Session):
        self.db = db

    def _to_domain_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to SQLAlchemy model."""
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def save(self, user: User) -> User:
        """Save a user (create or update)."""
        try:
            if user.id is None:
                model = UserModel(
                    username=user.username,
                    email=user.email,
                )
                self.db.add(model)
            else:
                existing_model = (
                    self.db.query(UserModel).filter(UserModel.id == user.id).first()
                )
                if not existing_model:
                    raise ValueError(f"User with id {user.id} not found")

                existing_model.username = user.username
                existing_model.email = user.email
                model = existing_model

            self.db.commit()
            self.db.refresh(model)
            return self._to_domain_entity(model)

        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Database error while saving user: {str(e)}")

    def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID."""
        try:
            model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            return self._to_domain_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding user: {str(e)}")

    def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        try:
            model = (
                self.db.query(UserModel).filter(UserModel.username == username).first()
            )
            return self._to_domain_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while finding user by username: {str(e)}"
            )

    def find_by_email(self, email: str) -> User | None:
        """Find user by email address."""
        try:
            model = self.db.query(UserModel).filter(UserModel.email == email).first()
            return self._to_domain_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding user by email: {str(e)}")

    def find_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Find all users with pagination."""
        try:
            models = self.db.query(UserModel).offset(skip).limit(limit).all()
            return [self._to_domain_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding all users: {str(e)}")

    def find_with_pagination(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Find users with pagination.

        Args:
            skip: Number of users to skip for pagination
            limit: Maximum number of users to return

        Returns:
            List of user domain entities
        """
        return self.find_all(skip=skip, limit=limit)

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        try:
            model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if not model:
                return False

            self.db.delete(model)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Database error while deleting user: {str(e)}")

    def exists(self, user_id: int) -> bool:
        """Check if user exists."""
        try:
            return (
                self.db.query(UserModel.id).filter(UserModel.id == user_id).first()
                is not None
            )
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while checking user existence: {str(e)}"
            )

    def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        try:
            return (
                self.db.query(UserModel.id)
                .filter(UserModel.username == username)
                .first()
                is not None
            )
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while checking username existence: {str(e)}"
            )

    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        try:
            return (
                self.db.query(UserModel.id).filter(UserModel.email == email).first()
                is not None
            )
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while checking email existence: {str(e)}"
            )

    def count_total(self) -> int:
        """Count total users."""
        try:
            return self.db.query(UserModel).count()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while counting total users: {str(e)}")
