"""
PRD service for managing PRD creation and storage.

This service handles PRD creation, validation, and storage operations.
"""

from uuid import UUID

from src.models.prd import PRD, PRDFileType
from src.services.storage import storage
from src.services.validation import ValidationError, validate_file
from src.utils.file_parser import parse_file, parse_text_content, FileParseError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PRDService:
    """Service for PRD operations."""

    def create_prd_from_file(
        self, file_content: bytes, filename: str
    ) -> PRD:
        """
        Create a PRD from uploaded file.

        Args:
            file_content: Binary file content
            filename: Original filename

        Returns:
            Created PRD model

        Raises:
            ValidationError: If file validation fails
            FileParseError: If file parsing fails
        """
        from io import BytesIO

        file_io = BytesIO(file_content)

        # Validate file
        try:
            file_type, size = validate_file(file_io, filename)
        except ValidationError as e:
            logger.error(f"File validation failed for {filename}: {e.message}")
            raise

        # Reset file position for parsing
        file_io.seek(0)

        # Parse file content
        try:
            content = parse_file(file_io, filename, file_type)
        except FileParseError as e:
            logger.error(f"File parsing failed for {filename}: {e.message}")
            raise

        # Create PRD model
        prd = PRD(
            content=content,
            filename=filename,
            file_type=file_type,
            size=size,
        )

        # Store PRD
        stored_prd = storage.create_prd(prd)
        logger.info(f"PRD created: {stored_prd.id} from file {filename}")

        return stored_prd

    def create_prd_from_extracted_text(
        self,
        content: str,
        filename: str,
        file_type: PRDFileType,
        size: int,
    ) -> PRD:
        """
        Create a PRD from already-extracted text (e.g. after background conversion).

        Args:
            content: Extracted text content
            filename: Original filename
            file_type: Detected file type
            size: File size in bytes

        Returns:
            Created PRD model
        """
        content = content.strip()
        if not content:
            raise ValueError("Extracted content cannot be empty")
        prd = PRD(
            content=content,
            filename=filename,
            file_type=file_type,
            size=size,
        )
        stored_prd = storage.create_prd(prd)
        logger.info(f"PRD created: {stored_prd.id} from extracted text ({filename})")
        return stored_prd

    def create_prd_from_text(self, text_content: str) -> PRD:
        """
        Create a PRD from pasted text content.

        Args:
            text_content: Text content string

        Returns:
            Created PRD model

        Raises:
            ValueError: If content is empty
        """
        # Parse and validate text content
        try:
            content = parse_text_content(text_content)
        except ValueError as e:
            logger.error(f"Text content validation failed: {e}")
            raise

        # Create PRD model
        prd = PRD(
            content=content,
            file_type=PRDFileType.TXT,  # Default to TXT for pasted content
            size=len(text_content.encode('utf-8')),
        )

        # Store PRD
        stored_prd = storage.create_prd(prd)
        logger.info(f"PRD created: {stored_prd.id} from text content")

        return stored_prd

    def get_prd(self, prd_id: UUID) -> PRD | None:
        """
        Retrieve a PRD by ID.

        Args:
            prd_id: PRD identifier

        Returns:
            PRD if found, None otherwise
        """
        return storage.get_prd(prd_id)


# Global service instance
prd_service = PRDService()
