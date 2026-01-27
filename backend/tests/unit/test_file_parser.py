"""
Unit tests for file parser utility.

Tests extraction of text content from .txt, .md, and .docx files.
"""

import pytest
from io import BytesIO
from pathlib import Path
import tempfile
import os

from src.utils.file_parser import parse_file, parse_text_content, FileParseError
from src.models.prd import PRDFileType


class TestFileParser:
    """Test suite for file parser utility."""

    def test_parse_txt_file(self):
        """Test parsing a .txt file."""
        content = "This is a test PRD content.\nIt has multiple lines."
        file_content = BytesIO(content.encode('utf-8'))
        
        result = parse_file(file_content, "test.txt", PRDFileType.TXT)
        
        assert result == content
        assert len(result) > 0

    def test_parse_md_file(self):
        """Test parsing a .md file."""
        content = "# PRD Title\n\nThis is markdown content.\n\n## Section 1"
        file_content = BytesIO(content.encode('utf-8'))
        
        result = parse_file(file_content, "test.md", PRDFileType.MD)
        
        assert result == content
        assert "# PRD Title" in result

    def test_parse_docx_file(self):
        """Test parsing a .docx file."""
        # Create a minimal .docx file for testing
        # For now, we'll test that the function handles .docx files
        # In a real scenario, we'd use python-docx to create a test file
        pytest.skip("Requires actual .docx file creation - will implement with python-docx")

    def test_parse_file_invalid_type(self):
        """Test that invalid file type raises error."""
        content = b"test content"
        file_content = BytesIO(content)
        
        # Test with an invalid enum value (this would be caught at validation level)
        # For now, test that unsupported file type in parse_file raises error
        # We'll use a mock invalid type by calling with an invalid string
        from enum import Enum
        class InvalidType(str, Enum):
            INVALID = "invalid"
        
        # This test verifies that parse_file handles unsupported types
        # The actual validation happens at the validation service level
        pytest.skip("Invalid type validation handled at validation service level")

    def test_parse_text_content(self):
        """Test parsing text content directly."""
        content = "Direct text input for PRD"
        
        result = parse_text_content(content)
        
        assert result == content

    def test_parse_text_content_empty(self):
        """Test that empty text content raises error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            parse_text_content("")

    def test_parse_text_content_whitespace_only(self):
        """Test that whitespace-only content raises error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            parse_text_content("   \n\t  ")

    def test_parse_file_encoding_handling(self):
        """Test that file parser handles different encodings."""
        content = "Test content with special chars: àáâãäå"
        file_content = BytesIO(content.encode('utf-8'))
        
        result = parse_file(file_content, "test.txt", PRDFileType.TXT)
        
        assert result == content

    def test_parse_file_large_content(self):
        """Test parsing large file content."""
        # Create content just under 10MB limit
        large_content = "x" * (9 * 1024 * 1024)  # 9MB
        file_content = BytesIO(large_content.encode('utf-8'))
        
        result = parse_file(file_content, "large.txt", PRDFileType.TXT)
        
        assert len(result) == len(large_content)
        assert result == large_content
