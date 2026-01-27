"""
PRD (Product Requirements Document) model.

Represents the uploaded or pasted PRD content.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class PRDFileType(str, Enum):
    """Supported PRD file types."""

    TXT = "txt"
    MD = "md"
    DOCX = "docx"


class PRD(BaseModel):
    """Product Requirements Document model."""

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the PRD")
    content: str = Field(..., min_length=1, description="Full text content of the PRD")
    filename: Optional[str] = Field(None, description="Original filename if uploaded")
    file_type: PRDFileType = Field(..., description="Format of the original file")
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when PRD was uploaded/pasted"
    )
    size: int = Field(..., ge=0, description="Size in bytes")
    metadata: Optional[dict] = Field(None, description="Additional metadata (word count, etc.)")

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        """Validate that content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content must not be empty")
        return v.strip()

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: int) -> int:
        """Validate that size is within limits (10MB)."""
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f"Content size must be less than {max_size} bytes (10MB)")
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "content": "Product Requirements Document content...",
                "filename": "prd.txt",
                "file_type": "txt",
                "uploaded_at": "2024-12-19T10:00:00Z",
                "size": 1024,
                "metadata": {"word_count": 500},
            }
        }
