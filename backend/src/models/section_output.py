"""
Stage 2 LLM output schema.

Strict Pydantic model for section-level suggestion output (LLM contract).
"""

from typing import List

from pydantic import BaseModel, Field


class SectionSuggestionItem(BaseModel):
    """One suggestion from the Stage 2 section review LLM."""

    id: str = Field(..., description="Suggestion id e.g. SUG-001")
    section: str = Field(..., description="Section id (canonical or sub-chunk)")
    type: str = Field(..., description="Suggestion type e.g. add, improve, fix")
    original: str = Field(default="", description="Original text if applicable")
    proposed: str = Field(..., description="Proposed text or change")
    reason: str = Field(..., description="Why this suggestion")
    confidence: float = Field(default=0.8, ge=0, le=1, description="Confidence 0-1")


class SectionSuggestionOutput(BaseModel):
    """Stage 2 LLM response: list of suggestions per section."""

    suggestions: List[SectionSuggestionItem] = Field(default_factory=list)
