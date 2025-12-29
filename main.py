from fastapi import FastAPI

from app.controller import subtask_controller, todo_controller, user_controller
from app.core.middleware.exception_handlers import register_exception_handlers

app = FastAPI(title="FastAPI Todo Management", version="0.1.0")

register_exception_handlers(app)
app.include_router(todo_controller.router)
app.include_router(user_controller.router)
app.include_router(subtask_controller.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
