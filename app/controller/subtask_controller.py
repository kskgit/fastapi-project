from fastapi import APIRouter, Depends
from fastapi import status as http_status

from app.controller.dto import CreateSubTaskDTO, SubtaskResponseDTO
from app.di import get_create_subtask_usecase
from app.usecases.subtask import CreateSubTaskUseCase

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
    subtask = await usecase.execute(
        user_id=request.user_id,
        todo_id=todo_id,
        title=request.title,
    )

    return SubtaskResponseDTO.from_domain_entity(subtask)
