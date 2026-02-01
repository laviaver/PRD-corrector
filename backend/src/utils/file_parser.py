"""
File parser utility for extracting text content from various file formats.

All formats are converted to markdown (.md) format before analysis.
Supports .txt, .md, .docx - all converted to markdown.
"""

from typing import BinaryIO

import mammoth
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
    Parse file content and convert to markdown format.

    Args:
        file_content: Binary file content
        filename: Original filename
        file_type: Type of file (txt, md, docx)

    Returns:
        Markdown-formatted text content

    Raises:
        FileParseError: If parsing fails
    """
    try:
        if file_type == PRDFileType.MD:
            # Already markdown, just read and return
            raw = file_content.read()
            for encoding in ('utf-8', 'cp1252', 'latin-1'):
                try:
                    content = raw.decode(encoding)
                    if encoding != 'utf-8':
                        logger.warning(
                            "File %s is not UTF-8; decoded with %s",
                            filename,
                            encoding,
                        )
                    return content.strip()
                except UnicodeDecodeError:
                    continue
            raise FileParseError("Failed to decode file content", file_type.value)

        elif file_type == PRDFileType.TXT:
            # Convert .txt to markdown format
            raw = file_content.read()
            for encoding in ('utf-8', 'cp1252', 'latin-1'):
                try:
                    content = raw.decode(encoding)
                    if encoding != 'utf-8':
                        logger.warning(
                            "File %s is not UTF-8; decoded with %s",
                            filename,
                            encoding,
                        )
                    # Convert plain text to markdown by preserving structure
                    # Wrap in code block or format as markdown paragraphs
                    content = content.strip()
                    if not content:
                        raise FileParseError("File is empty", file_type.value)
                    # Format as markdown: preserve line breaks and structure
                    lines = content.split('\n')
                    markdown_lines = []
                    for line in lines:
                        line = line.strip()
                        if line:
                            markdown_lines.append(line)
                        else:
                            markdown_lines.append('')
                    return '\n'.join(markdown_lines)
                except UnicodeDecodeError:
                    continue
            raise FileParseError("Failed to decode file content", file_type.value)

        elif file_type == PRDFileType.DOCX:
            # Convert .docx to markdown using mammoth
            try:
                import tempfile
                import os

                # Read file content
                file_content.seek(0)
                docx_bytes = file_content.read()

                # Save to temporary location for mammoth
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(docx_bytes)
                    tmp_file.flush()
                    tmp_path = tmp_file.name

                try:
                    # Use mammoth to convert .docx to markdown
                    with open(tmp_path, 'rb') as docx_file:
                        result = mammoth.convert_to_markdown(docx_file)
                        content = result.value
                        
                        # Log any warnings from mammoth
                        if result.messages:
                            for message in result.messages:
                                logger.warning(f"Mammoth conversion warning: {message}")

                    content = content.strip()
                    if not content:
                        # Fallback to python-docx if mammoth fails to extract content
                        logger.warning(f"Mammoth extracted no content from {filename}, trying python-docx fallback")
                        doc = Document(tmp_path)
                        parts = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
                        content = '\n'.join(parts)
                        if len(content) < 100 and hasattr(doc, 'tables') and doc.tables:
                            table_texts = []
                            for table in doc.tables:
                                for row in table.rows:
                                    for cell in row.cells:
                                        if cell.text.strip():
                                            table_texts.append(cell.text.strip())
                            if table_texts:
                                content = '\n'.join(parts + [''] + table_texts) if parts else '\n'.join(table_texts)
                        content = content.strip()
                        if not content:
                            raise FileParseError(
                                "Document has no extractable text. The file may be empty, "
                                "or text may be in images/headers/footers.",
                                file_type.value,
                            )
                    return content
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            except PackageNotFoundError:
                raise FileParseError(f"Invalid .docx file: {filename}", file_type.value)
            except FileParseError:
                raise
            except Exception as e:
                logger.error(f"Error parsing .docx file {filename}: {e}")
                raise FileParseError(f"Failed to parse .docx file: {str(e)}", file_type.value)

        else:
            # Only .docx, .md, .txt are supported
            raise FileParseError(
                f"Unsupported file type: {file_type.value}. Only .docx, .md, and .txt files are allowed.",
                file_type.value,
            )

    except FileParseError:
        raise  # already a clear message (e.g. empty docx)
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
