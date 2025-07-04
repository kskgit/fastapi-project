from fastapi import APIRouter

from app.common.response.response_code import CustomResponseCode
from app.common.response.response_schema import ResponseModel, response_base
from app.tier.todo.schemas.todo import TodoCreate

router = APIRouter()


@router.post("", summary="Create todo")
async def create_todo(obj: TodoCreate) -> ResponseModel:
    return response_base.success_empty(res=CustomResponseCode.HTTP_200)
