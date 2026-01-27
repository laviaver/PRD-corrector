"""
File parser utility for extracting text content from various file formats.

Supports .txt, .md, and .docx file formats.
"""

from io import BytesIO
from typing import BinaryIO

from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from src.models.prd import PRDFileType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileParseError(Exception):
    """Exception raised when file parsing fails."""

    def __init__(self, message: str, file_type: str = None):
        self.message = message
        self.file_type = file_type
        super().__init__(self.message)


def parse_file(file_content: BinaryIO, filename: str, file_type: PRDFileType) -> str:
    """
    Parse file content and extract text.

    Args:
        file_content: Binary file content
        filename: Original filename
        file_type: Type of file (txt, md, docx)

    Returns:
        Extracted text content

    Raises:
        FileParseError: If parsing fails
    """
    try:
        if file_type == PRDFileType.TXT or file_type == PRDFileType.MD:
            # Read as text
            content = file_content.read().decode('utf-8')
            return content.strip()

        elif file_type == PRDFileType.DOCX:
            # Parse .docx file
            try:
                # Save to temporary location for python-docx
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(file_content.read())
                    tmp_path = tmp_file.name

                try:
                    doc = Document(tmp_path)
                    # Extract text from all paragraphs
                    paragraphs = [para.text for para in doc.paragraphs]
                    content = '\n'.join(paragraphs)
                    return content.strip()
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            except PackageNotFoundError:
                raise FileParseError(f"Invalid .docx file: {filename}", file_type.value)
            except Exception as e:
                logger.error(f"Error parsing .docx file {filename}: {e}")
                raise FileParseError(f"Failed to parse .docx file: {str(e)}", file_type.value)

        else:
            raise FileParseError(f"Unsupported file type: {file_type}", file_type.value)

    except UnicodeDecodeError as e:
        logger.error(f"Encoding error parsing file {filename}: {e}")
        raise FileParseError(f"Failed to decode file content: {str(e)}", file_type.value)
    except Exception as e:
        logger.error(f"Unexpected error parsing file {filename}: {e}")
        raise FileParseError(f"Unexpected error parsing file: {str(e)}", file_type.value)


def parse_text_content(content: str) -> str:
    """
    Parse direct text content input.

    Args:
        content: Text content string

    Returns:
        Stripped text content

    Raises:
        ValueError: If content is empty or whitespace-only
    """
    if not content or not content.strip():
        raise ValueError("Content cannot be empty")

    return content.strip()
