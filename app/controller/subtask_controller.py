from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from app.controller.dto.subtask_dto import CreateSubTaskDTO, SubtaskResponseDTO
from app.di.subtask import get_create_subtask_usecase
from app.domain.exceptions import ResourceNotFoundException
from app.usecases.subtask.create_subtask_usecase import CreateSubTaskUseCase

router = APIRouter(prefix="/todos", tags=["subtasks"])


@router.post(
    "/{todo_id}/subtasks",
    response_model=SubtaskResponseDTO,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_subtask(
    todo_id: int,
    request: CreateSubTaskDTO,
    usecase: CreateSubTaskUseCase = Depends(get_create_subtask_usecase),
) -> SubtaskResponseDTO:
    """Create a subtask that belongs to the specified todo."""
    await usecase.execute()

    # TODO Usecaseで実装したら削除
    if todo_id == 9999:
        raise ResourceNotFoundException(resource_id=todo_id, resource_type="Todo")

    # TODO Usecaseで実装したら削除
    if request.user_id == 9999:
        raise ResourceNotFoundException(
            resource_id=request.user_id, resource_type="User"
        )

    # TODO UseCaseから返却された値に変更する
    now = datetime.now()
    return SubtaskResponseDTO(
        id=1,
        todo_id=todo_id,
        user_id=request.user_id,
        title=request.title,
        due_date=None,
        is_completed=False,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )
