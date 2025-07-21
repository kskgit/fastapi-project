from fastapi import FastAPI, HTTPException, Request

from app.api.endpoints import todo as todo_routes
from app.api.endpoints import user as user_routes
from app.domain.exceptions import (
    DomainException,
    InfrastructureException,
    ResourceNotFoundException,
)

# Service layer has been removed - now using UseCase pattern

app = FastAPI(title="FastAPI Todo Management", version="0.1.0")


# Service layer dependencies removed - now using UseCase pattern with
# dependency injection


@app.exception_handler(ResourceNotFoundException)
async def resource_not_found_handler(
    request: Request, exc: ResourceNotFoundException
) -> HTTPException:
    """Handle ResourceNotFoundException exceptions.

    ResourceNotFoundException (and its subclasses) are used for resource
    not found errors:
    - UserNotFoundException -> 404
    - TodoNotFoundException -> 404
    """
    raise HTTPException(status_code=404, detail=str(exc))


@app.exception_handler(DomainException)
async def domain_exception_handler(
    request: Request, exc: DomainException
) -> HTTPException:
    """Handle general DomainException exceptions.

    DomainException is used for business logic errors -> 400
    """
    raise HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> HTTPException:
    """Handle ValueError exceptions.

    ValueError is used for remaining business logic errors:
    - Invalid business rules -> 400

    Note: Resource not found errors now use specific domain exceptions.
    """
    raise HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(InfrastructureException)
async def infrastructure_error_handler(
    request: Request, exc: InfrastructureException
) -> HTTPException:
    """Handle InfrastructureException exceptions.

    InfrastructureException is used for infrastructure layer failures:
    - ConnectionException (data persistence failures) -> 503
    - Other infrastructure errors -> 503

    HTTP 503 indicates service temporarily unavailable, suggesting retry.
    """
    raise HTTPException(
        status_code=503,
        detail="Service temporarily unavailable. Please try again later.",
    )


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
