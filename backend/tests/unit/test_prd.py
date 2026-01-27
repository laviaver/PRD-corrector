"""
Unit tests for PRD model.

Tests validation, field constraints, and model behavior.
"""

import pytest
from datetime import datetime
from uuid import UUID

from src.models.prd import PRD, PRDFileType


class TestPRDModel:
    """Test suite for PRD model."""

    def test_create_prd_with_required_fields(self):
        """Test creating a PRD with only required fields."""
        prd = PRD(
            content="Test PRD content",
            file_type=PRDFileType.TXT,
            size=100,
        )

        assert isinstance(prd.id, UUID)
        assert prd.content == "Test PRD content"
        assert prd.file_type == PRDFileType.TXT
        assert prd.size == 100
        assert isinstance(prd.uploaded_at, datetime)
        assert prd.filename is None
        assert prd.metadata is None

    def test_create_prd_with_all_fields(self):
        """Test creating a PRD with all fields."""
        prd = PRD(
            content="Full PRD content",
            file_type=PRDFileType.DOCX,
            size=1024,
            filename="test_prd.docx",
            metadata={"word_count": 500, "page_count": 10},
        )

        assert prd.filename == "test_prd.docx"
        assert prd.metadata == {"word_count": 500, "page_count": 10}

    def test_prd_content_validation_empty_string(self):
        """Test that empty content raises validation error."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            PRD(
                content="",
                file_type=PRDFileType.TXT,
                size=0,
            )

    def test_prd_content_validation_whitespace_only(self):
        """Test that whitespace-only content raises validation error."""
        with pytest.raises(ValueError, match="Content must not be empty"):
            PRD(
                content="   \n\t  ",
                file_type=PRDFileType.TXT,
                size=10,
            )

    def test_prd_content_stripped(self):
        """Test that content is automatically stripped."""
        prd = PRD(
            content="  Test content  \n",
            file_type=PRDFileType.TXT,
            size=15,
        )

        assert prd.content == "Test content"

    def test_prd_size_validation_max_limit(self):
        """Test that size exceeding 10MB raises validation error."""
        max_size = 10 * 1024 * 1024  # 10MB
        with pytest.raises(ValueError, match="Content size must be less than"):
            PRD(
                content="x" * (max_size + 1),
                file_type=PRDFileType.TXT,
                size=max_size + 1,
            )

    def test_prd_size_validation_zero_allowed(self):
        """Test that zero size is allowed."""
        prd = PRD(
            content="x",
            file_type=PRDFileType.TXT,
            size=0,
        )

        assert prd.size == 0

    def test_prd_size_validation_negative(self):
        """Test that negative size raises validation error."""
        with pytest.raises(ValueError):
            PRD(
                content="Test",
                file_type=PRDFileType.TXT,
                size=-1,
            )

    def test_prd_file_type_enum(self):
        """Test that file_type must be valid enum value."""
        prd = PRD(
            content="Test",
            file_type=PRDFileType.MD,
            size=4,
        )

        assert prd.file_type == PRDFileType.MD

    def test_prd_serialization(self):
        """Test that PRD can be serialized to dict."""
        prd = PRD(
            content="Test content",
            file_type=PRDFileType.TXT,
            size=12,
            filename="test.txt",
        )

        prd_dict = prd.model_dump()
        assert isinstance(prd_dict, dict)
        assert prd_dict["content"] == "Test content"
        assert prd_dict["file_type"] == "txt"
        assert prd_dict["filename"] == "test.txt"

    def test_prd_json_serialization(self):
        """Test that PRD can be serialized to JSON."""
        prd = PRD(
            content="Test content",
            file_type=PRDFileType.TXT,
            size=12,
        )

        prd_json = prd.model_dump_json()
        assert isinstance(prd_json, str)
        assert "Test content" in prd_json
        assert "txt" in prd_json
