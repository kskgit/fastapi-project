"""User Data Transfer Objects for API layer.

This module contains DTOs for User-related API operations.
These DTOs handle serialization/deserialization between API and Domain layers.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.domain.entities.user import User, UserRole


class UserCreateDTO(BaseModel):
    """DTO for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: str | None = Field(None, max_length=100, description="Full name")
    role: UserRole = Field(
        default=UserRole.MEMBER,
        description="User role (e.g., viewer/member/admin)",
    )


class UserUpdateDTO(BaseModel):
    """DTO for updating an existing user."""

    username: str | None = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    email: EmailStr | None = Field(None, description="Email address")
    full_name: str | None = Field(None, max_length=100, description="Full name")


class UserResponseDTO(BaseModel):
    """DTO for user response data."""

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str | None = Field(None, description="Full name")
    role: UserRole = Field(
        default=UserRole.MEMBER,
        description="User role (e.g., viewer/member/admin)",
    )
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    @classmethod
    def from_domain_entity(cls, user: User) -> "UserResponseDTO":
        """Create DTO from domain entity.

        Args:
            user: User domain entity

        Returns:
            UserResponseDTO: DTO representation of the user
        """
        return cls(
            id=user.id or 0,  # Default to 0 if id is None
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            # TODO 実装次第修正する
            role=UserRole.VIEWER,
            is_active=user.is_active,
            created_at=user.created_at or datetime.now(),  # Default to now if None
            updated_at=user.updated_at,
        )

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
