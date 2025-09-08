import logging
import traceback

from fastapi import FastAPI, HTTPException, Request

from app.api.endpoints import todo as todo_routes
from app.api.endpoints import user as user_routes
from app.domain.exceptions import BaseCustomException

app = FastAPI(title="FastAPI Todo Management", version="0.1.0")


@app.exception_handler(BaseCustomException)
async def domain_exception_handler(
    request: Request, exc: BaseCustomException
) -> HTTPException:
    """Handle all domain exceptions with unified logging and monitoring.

    This handler provides centralized handling for all domain-level exceptions
    including business rule violations and system errors, with appropriate
    logging levels and monitoring based on the exception type.
    """

    # Log with appropriate level based on exception type
    logger = logging.getLogger(__name__)
    log_level = getattr(logging, exc.get_log_level())

    # Add structured logging context
    extra_context = {
        "exception_type": exc.__class__.__name__,
        "error_category": exc.get_error_category(),
        "should_trigger_alert": exc.should_trigger_alert(),
        "request_path": request.url.path,
        "stack_trace": traceback.format_exc(),  # Always include stack trace in logs
    }

    # Include details if available (for SystemException)
    if hasattr(exc, "details") and exc.details:
        extra_context["details"] = exc.details
    if hasattr(exc, "error_code"):
        extra_context["error_code"] = exc.error_code

    logger.log(level=log_level, msg=f"Exception occurred: {exc}", extra=extra_context)

    # Use the specific HTTP status code from the exception
    # API response contains only clean, user-friendly message (no stack trace)
    raise HTTPException(status_code=exc.http_status_code.value, detail=str(exc))


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
