from fastapi import APIRouter, Depends

from app.controller.dto.subtask_dto import CreateSubTaskDTO, SubtaskResponseDTO
from app.di.subtask import get_create_subtask_usecase
from app.usecases.subtask.create_subtask_usecase import CreateSubTaskUseCase

router = APIRouter(prefix="/api/v1/subtask", tags=["subtask"])


@router.post("/", response_model=SubtaskResponseDTO)
async def create_subtask(
    request: CreateSubTaskDTO,
    usecase: CreateSubTaskUseCase = Depends(get_create_subtask_usecase),
) -> list[SubtaskResponseDTO]:
    """Get all users with optional pagination."""
    return await usecase.execute()
