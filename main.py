from fastapi import Depends, FastAPI, HTTPException, Request
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


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> HTTPException:
    """Handle ValueError exceptions.

    ValueError is used for business logic errors:
    - Todo not found -> 404
    - Invalid business rules -> 400
    """
    error_message = str(exc)
    if "not found" in error_message.lower():
        raise HTTPException(status_code=404, detail=error_message)
    raise HTTPException(status_code=400, detail=error_message)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError) -> HTTPException:
    """Handle RuntimeError exceptions.

    RuntimeError is used for unexpected system errors -> 500
    """
    raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}")


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
