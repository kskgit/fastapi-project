from fastapi import APIRouter

from app.todo.api.router import api_router as todo_router

main_router = APIRouter()

main_router.include_router(todo_router, prefix="/api/v1")
