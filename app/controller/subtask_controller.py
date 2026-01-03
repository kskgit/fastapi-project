from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from app.controller.dto.subtask_dto import CreateSubTaskDTO, SubtaskResponseDTO
from app.di.subtask import get_create_subtask_usecase
from app.usecases.subtask.create_subtask_usecase import CreateSubTaskUseCase

router = APIRouter(prefix="/todos", tags=["subtasks"])


@router.post(
    "/{todo_id}/subtasks",
    response_model=SubtaskResponseDTO,
    status_code=http_status.HTTP_201_CREATED,
    summary="Todo配下のサブタスク作成",
    description="指定したTodoの子サブタスクを作成し、作成済みデータを返す。",
)
async def create_subtask(
    todo_id: int,
    request: CreateSubTaskDTO,
    usecase: CreateSubTaskUseCase = Depends(get_create_subtask_usecase),
) -> SubtaskResponseDTO:
    await usecase.execute(
        user_id=request.user_id,
        todo_id=todo_id,
        title=request.title,
    )

    # TODO UseCaseから返却された値に変更する
    now = datetime.now()
    return SubtaskResponseDTO(
        id=1,
        todo_id=todo_id,
        user_id=request.user_id,
        title=request.title,
        is_completed=False,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )
