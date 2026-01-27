"""
File validation service.

Validates file types, sizes, and content for PRD uploads.
"""

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Tuple

from src.models.prd import PRDFileType
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.txt', '.md', '.docx'}


class ValidationError(Exception):
    """Exception raised when validation fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def validate_file_type(filename: str) -> PRDFileType:
    """
    Validate file type based on extension.

    Args:
        filename: Name of the file

    Returns:
        PRDFileType enum value

    Raises:
        ValidationError: If file type is not supported
    """
    if not filename or '.' not in filename:
        raise ValidationError("File must have an extension")

    extension = Path(filename).suffix.lower()

    if extension == '.txt':
        return PRDFileType.TXT
    elif extension == '.md':
        return PRDFileType.MD
    elif extension == '.docx':
        return PRDFileType.DOCX
    else:
        raise ValidationError(
            f"Unsupported file type: {extension}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def validate_file_size(file_content: BinaryIO, filename: str) -> int:
    """
    Validate file size.

    Args:
        file_content: File content
        filename: Name of the file

    Returns:
        File size in bytes

    Raises:
        ValidationError: If file size exceeds limit or is empty
    """
    # Read file size
    current_position = file_content.tell()
    file_content.seek(0, 2)  # Seek to end
    size = file_content.tell()
    file_content.seek(current_position)  # Reset position

    if size == 0:
        raise ValidationError("File is empty")

    if size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size ({size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes / 10MB)"
        )

    return size


def validate_file(file_content: BinaryIO, filename: str) -> Tuple[PRDFileType, int]:
    """
    Validate file type and size.

    Args:
        file_content: File content
        filename: Name of the file

    Returns:
        Tuple of (file_type, size)

    Raises:
        ValidationError: If validation fails
    """
    file_type = validate_file_type(filename)
    size = validate_file_size(file_content, filename)

    logger.debug(f"File validated: {filename}, type: {file_type.value}, size: {size} bytes")

    return file_type, size
