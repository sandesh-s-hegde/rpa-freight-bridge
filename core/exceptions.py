import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from core.context import correlation_id_ctx

logger = logging.getLogger("rpa-bridge")


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        logger.warning(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "type": "https://example.com/probs/validation-error",
                "title": "Unprocessable Entity",
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "detail": "The request payload failed strict schema validation.",
                "instance": request.url.path,
                "trace_id": correlation_id_ctx.get(),
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database Fault: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "https://example.com/probs/database-fault",
                "title": "Database Connection Error",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": "The system encountered a fatal error communicating with the persistence layer.",
                "instance": request.url.path,
                "trace_id": correlation_id_ctx.get(),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.critical(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "https://example.com/probs/internal-error",
                "title": "Internal Server Error",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": "An unexpected system fault occurred.",
                "instance": request.url.path,
                "trace_id": correlation_id_ctx.get(),
            },
        )
