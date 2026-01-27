"""
Analyze endpoint for PRD upload and text paste.

This endpoint handles file uploads and text paste, creates PRD, and initiates analysis.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.services.prd_service import prd_service
from src.services.analysis_service import analysis_service
from src.services.validation import ValidationError
from src.utils.file_parser import FileParseError
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class TextInputRequest(BaseModel):
    """Request model for text paste input."""

    content: str


class AnalyzeResponse(BaseModel):
    """Response model for analyze endpoint."""

    prd_id: str
    analysis_id: str | None = None
    message: str


@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_201_CREATED)
async def analyze_prd(
    file: UploadFile | None = File(None, description="PRD file to upload"),
    text: str | None = Form(None, description="PRD text content to paste"),
):
    """
    Upload PRD file or paste text content for analysis.

    Accepts either:
    - File upload (multipart/form-data with 'file' field)
    - Text paste (multipart/form-data with 'text' field)

    Returns:
        PRD ID and analysis ID (if analysis initiated)
    """
    # Validate that exactly one input method is provided
    if file and text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either file upload or text content, not both",
        )

    if not file and not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either file upload or text content",
        )

    try:

        # Handle file upload
        if file:
            file_content = await file.read()
            prd = prd_service.create_prd_from_file(file_content, file.filename or "uploaded_file")
            logger.info(f"PRD created from file: {prd.id}")

        # Handle text paste
        else:  # text is guaranteed to be not None here
            prd = prd_service.create_prd_from_text(text)
            logger.info(f"PRD created from text: {prd.id}")

        # Initiate analysis
        analysis = await analysis_service.initiate_analysis(prd.id)

        return AnalyzeResponse(
            prd_id=str(prd.id),
            analysis_id=str(analysis.id),
            message="PRD uploaded successfully. Analysis initiated.",
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        ) from e

    except FileParseError as e:
        logger.error(f"File parse error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse file: {e.message}",
        )

    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
