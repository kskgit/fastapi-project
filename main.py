from fastapi import FastAPI

from app.api.endpoints import todo as todo_routes
from app.api.endpoints import user as user_routes
from app.core.middleware.exception_handlers import (
    custom_exception_handler_adapter,
)
from app.domain.exceptions.base import BaseCustomException

app = FastAPI(title="FastAPI Todo Management", version="0.1.0")

# Register exception handler for BaseCustomException with adapter
app.add_exception_handler(BaseCustomException, custom_exception_handler_adapter)


app.include_router(todo_routes.router)
app.include_router(user_routes.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
