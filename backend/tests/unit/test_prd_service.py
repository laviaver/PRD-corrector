"""
Unit tests for PRD service.

Tests PRD creation from files and text, validation, and storage operations.
"""

import pytest
from io import BytesIO
from uuid import UUID

from src.services.prd_service import prd_service
from src.services.validation import ValidationError
from src.utils.file_parser import FileParseError
from src.models.prd import PRDFileType


class TestPRDService:
    """Test suite for PRD service."""

    def test_create_prd_from_txt_file(self):
        """Test creating PRD from .txt file."""
        content = "Test PRD content from file"
        file_content = content.encode('utf-8')
        
        prd = prd_service.create_prd_from_file(file_content, "test.txt")
        
        assert prd.content == content
        assert prd.filename == "test.txt"
        assert prd.file_type == PRDFileType.TXT
        assert isinstance(prd.id, UUID)

    def test_create_prd_from_md_file(self):
        """Test creating PRD from .md file."""
        content = "# PRD Title\n\nContent here"
        file_content = content.encode('utf-8')
        
        prd = prd_service.create_prd_from_file(file_content, "test.md")
        
        assert prd.content == content
        assert prd.file_type == PRDFileType.MD

    def test_create_prd_from_text(self):
        """Test creating PRD from pasted text."""
        text_content = "Pasted PRD content"
        
        prd = prd_service.create_prd_from_text(text_content)
        
        assert prd.content == text_content
        assert prd.file_type == PRDFileType.TXT
        assert prd.filename is None

    def test_create_prd_from_text_empty(self):
        """Test that empty text raises error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            prd_service.create_prd_from_text("")

    def test_create_prd_from_file_other_type(self):
        """Test that unknown extension (.xyz) is accepted and converted to text."""
        content = b"test content from xyz file"
        prd = prd_service.create_prd_from_file(content, "doc.xyz")
        assert prd.content == "test content from xyz file"
        assert prd.file_type == PRDFileType.OTHER
        assert prd.filename == "doc.xyz"

    def test_create_prd_from_file_too_large(self):
        """Test that file too large raises error."""
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        
        with pytest.raises(ValidationError):
            prd_service.create_prd_from_file(large_content, "large.txt")

    def test_get_prd_existing(self):
        """Test retrieving existing PRD."""
        # Create a PRD first
        prd = prd_service.create_prd_from_text("Test content")
        prd_id = prd.id
        
        # Retrieve it
        retrieved = prd_service.get_prd(prd_id)
        
        assert retrieved is not None
        assert retrieved.id == prd_id
        assert retrieved.content == "Test content"

    def test_get_prd_nonexistent(self):
        """Test retrieving non-existent PRD returns None."""
        from uuid import uuid4
        
        nonexistent_id = uuid4()
        result = prd_service.get_prd(nonexistent_id)
        
        assert result is None
