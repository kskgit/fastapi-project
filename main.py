from fastapi import FastAPI, HTTPException, Request

from app.api.endpoints import todo as todo_routes
from app.api.endpoints import user as user_routes

# Service layer has been removed - now using UseCase pattern

app = FastAPI(title="FastAPI Todo Management", version="0.1.0")


# Service layer dependencies removed - now using UseCase pattern with
# dependency injection


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


app.include_router(todo_routes.router)
app.include_router(user_routes.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
