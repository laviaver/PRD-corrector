"""
Unit tests for file validation service.

Tests file type validation, size limits, and content validation.
"""

import pytest
from io import BytesIO

from src.services.validation import (
    validate_file,
    validate_file_type,
    validate_file_size,
    ValidationError,
)
from src.models.prd import PRDFileType


class TestFileValidation:
    """Test suite for file validation service."""

    def test_validate_file_type_valid(self):
        """Test validation of valid file types."""
        assert validate_file_type("test.txt") == PRDFileType.TXT
        assert validate_file_type("test.md") == PRDFileType.MD
        assert validate_file_type("test.docx") == PRDFileType.DOCX
        assert validate_file_type("TEST.TXT") == PRDFileType.TXT  # Case insensitive

    def test_validate_file_type_invalid(self):
        """Test that invalid file types raise error."""
        with pytest.raises(ValidationError, match="Unsupported file type"):
            validate_file_type("test.pdf")
        
        with pytest.raises(ValidationError, match="Unsupported file type"):
            validate_file_type("test.doc")  # Old Word format

    def test_validate_file_type_no_extension(self):
        """Test that files without extension raise error."""
        with pytest.raises(ValidationError, match="File must have an extension"):
            validate_file_type("test")

    def test_validate_file_size_within_limit(self):
        """Test validation of file size within limits."""
        # 5MB file (under 10MB limit)
        file_content = BytesIO(b"x" * (5 * 1024 * 1024))
        
        result = validate_file_size(file_content, "test.txt")
        
        assert result == 5 * 1024 * 1024

    def test_validate_file_size_at_limit(self):
        """Test validation of file size at limit."""
        # Exactly 10MB
        file_content = BytesIO(b"x" * (10 * 1024 * 1024))
        
        result = validate_file_size(file_content, "test.txt")
        
        assert result == 10 * 1024 * 1024

    def test_validate_file_size_exceeds_limit(self):
        """Test that files exceeding size limit raise error."""
        # 11MB file (over 10MB limit)
        file_content = BytesIO(b"x" * (11 * 1024 * 1024))
        
        with pytest.raises(ValidationError, match="exceeds maximum allowed size"):
            validate_file_size(file_content, "test.txt")

    def test_validate_file_size_zero(self):
        """Test that zero-size files raise error."""
        file_content = BytesIO(b"")
        
        with pytest.raises(ValidationError, match="File is empty"):
            validate_file_size(file_content, "test.txt")

    def test_validate_file_complete(self):
        """Test complete file validation."""
        content = b"Test PRD content"
        file_content = BytesIO(content)
        
        file_type, size = validate_file(file_content, "test.txt")
        
        assert file_type == PRDFileType.TXT
        assert size == len(content)

    def test_validate_file_invalid_type(self):
        """Test validation fails for invalid file type."""
        content = b"Test content"
        file_content = BytesIO(content)
        
        with pytest.raises(ValidationError):
            validate_file(file_content, "test.pdf")

    def test_validate_file_too_large(self):
        """Test validation fails for file too large."""
        large_content = b"x" * (11 * 1024 * 1024)
        file_content = BytesIO(large_content)
        
        with pytest.raises(ValidationError):
            validate_file(file_content, "large.txt")
