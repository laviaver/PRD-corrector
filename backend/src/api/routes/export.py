"""
Export endpoints for downloading analysis results.

This module provides endpoints for exporting analysis results in various formats.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, Response
from uuid import UUID

from src.models.export import ExportFormat
from src.services.export_service import export_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/export")
async def export_analysis(analysis_id: str, format: str = "markdown"):
    """
    Export analysis results.

    Args:
        analysis_id: Analysis identifier
        format: Export format (pdf, markdown, json)

    Returns:
        Export file or data
    """
    try:
        analysis_uuid = UUID(analysis_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis ID format",
        )

    # Validate format
    format_map = {
        "pdf": ExportFormat.PDF,
        "markdown": ExportFormat.MARKDOWN,
        "md": ExportFormat.MARKDOWN,
        "json": ExportFormat.JSON,
    }

    export_format = format_map.get(format.lower())
    if not export_format:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Supported: pdf, markdown, json",
        )

    try:
        export = export_service.export_analysis(analysis_uuid, export_format)

        # For MVP, return JSON representation
        # In production, return actual file download
        return {
            "export_id": str(export.id),
            "analysis_id": analysis_id,
            "format": export.format.value,
            "file_path": export.file_path,
            "created_at": export.created_at,
            "message": "Export created successfully. File download will be implemented in production.",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed",
        )
