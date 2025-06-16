from fastapi import APIRouter

from app.core.config import settings
from app.todo.api.todo import router as todo_router

main_router = APIRouter(prefix=settings.FASTAPI_API_PATH)

main_router.include_router(todo_router, prefix="/todo", tags=["todo"])
