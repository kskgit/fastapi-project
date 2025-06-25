from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.clean.todo.api.endpoints import todos
from app.clean.todo.core.database import get_db
from app.clean.todo.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)
from app.clean.todo.services.todo_service import TodoService

app = FastAPI(title="FastAPI Todo Management", version="0.1.0")


def get_todo_repository(db: Session = Depends(get_db)) -> SQLAlchemyTodoRepository:
    """Dependency injection for TodoRepository."""
    return SQLAlchemyTodoRepository(db)


def get_todo_service(
    repository: SQLAlchemyTodoRepository = Depends(get_todo_repository),
) -> TodoService:
    """Dependency injection for TodoService."""
    return TodoService(repository)


todos.get_todo_service = get_todo_service

app.include_router(todos.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
