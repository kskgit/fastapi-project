from fastapi import APIRouter

from app.todo.api.v1 import todo

api_router = APIRouter()

api_router.include_router(todo.router, prefix="/todos", tags=["todos"])
