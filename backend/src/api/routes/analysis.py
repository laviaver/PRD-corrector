"""
Analysis endpoints for retrieving analysis results and status.

This module provides endpoints for getting analysis results and polling status.
"""

from fastapi import APIRouter, HTTPException, status
from uuid import UUID

from src.services.analysis_service import analysis_service
from src.services.storage import storage
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Get analysis results by ID.

    Args:
        analysis_id: Analysis identifier

    Returns:
        Analysis with suggestions
    """
    try:
        analysis_uuid = UUID(analysis_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis ID format",
        )

    analysis = analysis_service.get_analysis(analysis_uuid)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    # Get suggestions
    suggestions = analysis_service.get_suggestions(analysis_uuid)

    return {
        "analysis": analysis.model_dump(),
        "suggestions": [s.model_dump() for s in suggestions],
    }


@router.get("/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """
    Get analysis status for polling.

    Args:
        analysis_id: Analysis identifier

    Returns:
        Status information
    """
    try:
        analysis_uuid = UUID(analysis_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis ID format",
        )

    status_info = analysis_service.get_analysis_status(analysis_uuid)
    if status_info.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    return status_info
