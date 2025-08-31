"""User API routes.

This module contains all User-related API endpoints.
"""

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status

from app.api.dtos.user_dto import (
    UserCreateDTO,
    UserResponseDTO,
    UserUpdateDTO,
)
from app.composition.di import (
    get_create_user_usecase,
    get_delete_user_usecase,
    get_get_user_by_id_usecase,
    get_get_users_usecase,
    get_update_user_usecase,
)
from app.usecases.user.create_user_usecase import CreateUserUseCase
from app.usecases.user.delete_user_usecase import DeleteUserUseCase
from app.usecases.user.get_user_by_id_usecase import GetUserByIdUseCase
from app.usecases.user.get_users_usecase import GetUsersUseCase
from app.usecases.user.update_user_usecase import UpdateUserUseCase

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/", response_model=list[UserResponseDTO])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    usecase: GetUsersUseCase = Depends(get_get_users_usecase),
) -> list[UserResponseDTO]:
    """Get all users with optional pagination."""
    users = await usecase.execute(skip=skip, limit=limit)
    return [UserResponseDTO.from_domain_entity(user) for user in users]


@router.post(
    "/", response_model=UserResponseDTO, status_code=http_status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreateDTO,
    usecase: CreateUserUseCase = Depends(get_create_user_usecase),
) -> UserResponseDTO:
    """Create a new user."""
    user = await usecase.execute(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
    )
    return UserResponseDTO.from_domain_entity(user)


@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_user(
    user_id: int,
    usecase: GetUserByIdUseCase = Depends(get_get_user_by_id_usecase),
) -> UserResponseDTO:
    """Get a specific user by ID."""
    user = await usecase.execute(user_id=user_id)
    return UserResponseDTO.from_domain_entity(user)


@router.put("/{user_id}", response_model=UserResponseDTO)
async def update_user(
    user_id: int,
    user_data: UserUpdateDTO,
    usecase: UpdateUserUseCase = Depends(get_update_user_usecase),
) -> UserResponseDTO:
    """Update a specific user."""
    user = await usecase.execute(
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
    )
    return UserResponseDTO.from_domain_entity(user)


@router.delete("/{user_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    usecase: DeleteUserUseCase = Depends(get_delete_user_usecase),
) -> None:
    """Delete a specific user."""
    deleted = usecase.execute(user_id=user_id)
    if not deleted:
        from app.domain.exceptions import UserNotFoundException

        raise UserNotFoundException(user_id)
