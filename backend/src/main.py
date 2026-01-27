"""
FastAPI application entry point for PRD Reviewer.

This module sets up the FastAPI application with CORS middleware,
error handling, and API routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.middleware.error_handler import (
    PRDReviewerError,
    error_handler,
    http_exception_handler,
    prd_reviewer_error_handler,
    validation_exception_handler,
)
from src.config import settings
from src.utils.logger import setup_logging
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Setup logging
logger = setup_logging()

# Create FastAPI application
app = FastAPI(
    title="PRD Reviewer API",
    description="AI-powered PRD analysis and review service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
app.add_exception_handler(PRDReviewerError, prd_reviewer_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, error_handler)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "PRD Reviewer API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Include API routes (will be added in later phases)
# from backend.src.api.routes import analyze, analysis, export
# app.include_router(analyze.router, prefix="/api", tags=["analyze"])
# app.include_router(analysis.router, prefix="/api", tags=["analysis"])
# app.include_router(export.router, prefix="/api", tags=["export"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
