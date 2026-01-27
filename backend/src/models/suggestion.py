"""
Suggestion model.

Represents a single improvement suggestion for the PRD.
"""

from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SuggestionCategory(str, Enum):
    """Categories of suggestions."""

    STRUCTURE = "structure"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    BEST_PRACTICES = "best_practices"
    TECHNICAL_QUALITY = "technical_quality"


class SuggestionPriority(str, Enum):
    """Priority levels for suggestions."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SuggestionLocation(BaseModel):
    """Location in document where issue occurs."""

    section: Optional[str] = Field(None, description="Section name")
    paragraph_index: Optional[int] = Field(None, ge=0, description="Paragraph number")
    line_range: Optional[dict[str, int]] = Field(None, description="Line range {start, end}")


class Suggestion(BaseModel):
    """Suggestion model representing a single improvement suggestion."""

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    analysis_id: UUID = Field(..., description="Reference to the parent analysis")
    category: SuggestionCategory = Field(..., description="Category of suggestion")
    priority: SuggestionPriority = Field(..., description="Priority level")
    title: str = Field(..., min_length=1, description="Short title/summary of the suggestion")
    explanation: str = Field(..., min_length=1, description="Detailed explanation of the issue")
    location: Optional[SuggestionLocation] = Field(None, description="Location in document")
    example: Optional[str] = Field(None, description="Example of how to fix the issue")
    template: Optional[str] = Field(None, description="Template or snippet to use")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "analysis_id": "123e4567-e89b-12d3-a456-426614174001",
                "category": "structure",
                "priority": "high",
                "title": "Missing Executive Summary",
                "explanation": "The PRD should include an executive summary section...",
                "location": {
                    "section": "Overview",
                    "paragraph_index": 0,
                    "line_range": {"start": 1, "end": 5},
                },
                "example": "Executive Summary: This PRD describes...",
                "template": "## Executive Summary\n\n[Summary content]",
            }
        }
