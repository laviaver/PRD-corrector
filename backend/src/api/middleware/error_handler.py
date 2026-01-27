"""
Error handling middleware for FastAPI application.

This module provides centralized error handling and custom exception classes.
"""

from typing import Any, Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PRDReviewerError(Exception):
    """Base exception for PRD Reviewer application errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(PRDReviewerError):
    """Exception for validation errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class NotFoundError(PRDReviewerError):
    """Exception for resource not found errors."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class InternalServerError(PRDReviewerError):
    """Exception for internal server errors."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global error handler for unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Exception that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "type": type(exc).__name__,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler for HTTP exceptions.

    Args:
        request: FastAPI request object
        exc: HTTPException that was raised

    Returns:
        JSONResponse with error details
    """
    # Support both "error" and "detail" for client compatibility
    detail = exc.detail if isinstance(exc.detail, (str, type(None))) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": detail,
            "detail": detail,
            "status_code": exc.status_code,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for request validation errors.

    Args:
        request: FastAPI request object
        exc: RequestValidationError that was raised

    Returns:
        JSONResponse with validation error details
    """
    errors = exc.errors()
    logger.warning(f"Validation error: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "message": "Request validation failed",
            "details": errors,
        },
    )


async def prd_reviewer_error_handler(request: Request, exc: PRDReviewerError) -> JSONResponse:
    """
    Handler for PRD Reviewer custom exceptions.

    Args:
        request: FastAPI request object
        exc: PRDReviewerError that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"PRD Reviewer error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "status_code": exc.status_code,
        },
    )
