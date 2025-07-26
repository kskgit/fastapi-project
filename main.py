from fastapi import FastAPI, HTTPException, Request

from app.api.endpoints import todo as todo_routes
from app.api.endpoints import user as user_routes
from app.domain.exceptions import (
    BusinessRuleException,
    InfrastructureException,
)

app = FastAPI(title="FastAPI Todo Management", version="0.1.0")


@app.exception_handler(BusinessRuleException)
async def business_rule_error_handler(
    request: Request, exc: BusinessRuleException
) -> HTTPException:
    """Handle BusinessRuleException and its subclasses.

    This handler provides unified logging and monitoring for all business
    rule violations while allowing each exception to define its specific
    HTTP status code.

    Business rule violations are logged at WARNING level and do not
    trigger operational alerts as they are user-caused errors.
    """
    import logging

    # Log business rule violations at WARNING level
    logger = logging.getLogger(__name__)
    logger.log(
        level=getattr(logging, exc.get_log_level()),
        msg=f"Business rule violation: {exc} | Category: {exc.get_error_category()}",
    )

    # Use the specific HTTP status code from the exception
    raise HTTPException(status_code=exc.get_http_status_code(), detail=str(exc))


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> HTTPException:
    """Handle ValueError exceptions (legacy support).

    ValueError is kept for backward compatibility and unexpected cases.
    New code should use ValidationException or BusinessRuleException.
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
