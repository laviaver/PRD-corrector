"""
Analysis model.

Represents an analysis run on a PRD.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    """Analysis status values."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisSummary(BaseModel):
    """Summary statistics for an analysis."""

    total_suggestions: int = Field(..., ge=0, description="Total number of suggestions")
    suggestions_by_category: dict[str, int] = Field(
        default_factory=dict, description="Count of suggestions per category"
    )
    suggestions_by_priority: dict[str, int] = Field(
        default_factory=dict, description="Count of suggestions per priority level"
    )


class Analysis(BaseModel):
    """Analysis model representing a PRD analysis run."""

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the analysis")
    prd_id: UUID = Field(..., description="Reference to the PRD being analyzed")
    status: AnalysisStatus = Field(
        default=AnalysisStatus.PENDING, description="Current status of the analysis"
    )
    started_at: datetime = Field(
        default_factory=datetime.utcnow, description="When analysis started"
    )
    completed_at: Optional[datetime] = Field(None, description="When analysis completed")
    error_message: Optional[str] = Field(None, description="Error message if status is 'failed'")
    summary: Optional[AnalysisSummary] = Field(None, description="Analysis summary statistics")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "prd_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "started_at": "2024-12-19T10:00:00Z",
                "completed_at": "2024-12-19T10:00:30Z",
                "error_message": None,
                "summary": {
                    "total_suggestions": 5,
                    "suggestions_by_category": {"structure": 2, "clarity": 3},
                    "suggestions_by_priority": {"high": 1, "medium": 3, "low": 1},
                },
            }
        }
