"""
Export model.

Represents an export of analysis results.
"""

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Supported export formats."""

    PDF = "pdf"
    MARKDOWN = "markdown"
    JSON = "json"


class Export(BaseModel):
    """Export model representing an exported analysis."""

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the export")
    analysis_id: UUID = Field(..., description="Reference to the analysis being exported")
    format: ExportFormat = Field(..., description="Export format")
    file_path: str = Field(..., description="Path to the exported file")
    created_at: str = Field(..., description="Timestamp when export was created")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "analysis_id": "123e4567-e89b-12d3-a456-426614174001",
                "format": "pdf",
                "file_path": "/exports/analysis_123.pdf",
                "created_at": "2024-12-19T10:05:00Z",
            }
        }
