"""
Analysis model.

Represents an analysis run on a PRD.
"""

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    """Analysis status values."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SectionStatusEntry(BaseModel):
    """Per-section status from Stage 2 (ok, timeout, error)."""

    section_id: str = Field(..., description="Extracted section id")
    status: Literal["ok", "timeout", "error"] = Field(..., description="Section review status")


class AnalysisSummary(BaseModel):
    """Summary statistics for an analysis."""

    total_suggestions: int = Field(..., ge=0, description="Total number of suggestions")
    suggestions_by_category: dict[str, int] = Field(
        default_factory=dict, description="Count of suggestions per category"
    )
    suggestions_by_priority: dict[str, int] = Field(
        default_factory=dict, description="Count of suggestions per priority level"
    )


class AnalysisScores(BaseModel):
    """Stage 3 deterministic scores from structure + suggestions."""

    structure_score: int = Field(0, ge=0, le=100, description="Presence of problem, goals, metrics, risks")
    completeness_score: int = Field(0, ge=0, le=100, description="Signals: owner, metrics, KPIs")
    total_score: int = Field(0, ge=0, le=100, description="Weighted sum")


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
    section_status: Optional[List[SectionStatusEntry]] = Field(
        None, description="Per-section review status (ok|timeout|error)"
    )
    incomplete_sections: Optional[List[str]] = Field(
        None, description="Section ids that are timeout or error (review incomplete)"
    )
    scores: Optional[AnalysisScores] = Field(None, description="Stage 3 deterministic scores")

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
