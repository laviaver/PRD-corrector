"""
Analyze endpoint for PRD upload and text paste.

This endpoint handles file uploads and text paste, creates PRD, and initiates analysis.
Supports streaming (SSE) via POST /api/analyze/stream.
"""

import asyncio
import json
from queue import Empty, Queue

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError as PydanticValidationError

from src.config import settings
from src.services.prd_service import prd_service
from src.services.analysis_service import analysis_service
from src.services.analyzer import analyzer_service
from src.services.validation import ValidationError
from src.utils.file_parser import FileParseError
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


def _sse_message(event: str, data: dict) -> str:
    """Format one SSE message (event + data)."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


class TextInputRequest(BaseModel):
    """Request model for text paste input."""

    content: str


class AnalyzeResponse(BaseModel):
    """Response model for analyze endpoint."""

    prd_id: str
    analysis_id: str | None = None
    message: str


@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_201_CREATED)
async def analyze_prd(
    file: UploadFile | None = File(None, description="PRD file to upload"),
    text: str | None = Form(None, description="PRD text content to paste"),
):
    """
    Upload PRD file or paste text content for analysis.

    Accepts either:
    - File upload (multipart/form-data with 'file' field)
    - Text paste (multipart/form-data with 'text' field)

    Returns:
        PRD ID and analysis ID (if analysis initiated)
    """
    # Validate that exactly one input method is provided
    if file and text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either file upload or text content, not both",
        )

    if not file and not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either file upload or text content",
        )

    try:

        # Handle file upload
        if file:
            file_content = await file.read()
            prd = prd_service.create_prd_from_file(file_content, file.filename or "uploaded_file")
            logger.info(f"PRD created from file: {prd.id}")

        # Handle text paste
        else:  # text is guaranteed to be not None here
            prd = prd_service.create_prd_from_text(text)
            logger.info(f"PRD created from text: {prd.id}")

        # Initiate analysis
        analysis = await analysis_service.initiate_analysis(prd.id)

        return AnalyzeResponse(
            prd_id=str(prd.id),
            analysis_id=str(analysis.id),
            message="PRD uploaded successfully. Analysis initiated.",
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        ) from e

    except FileParseError as e:
        logger.error(f"File parse error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse file: {e.message}",
        )

    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except PydanticValidationError as e:
        # PRD/Analysis model validation (e.g. content empty, size invalid)
        errs = e.errors()
        msg = errs[0].get("msg", str(e)) if errs else str(e)
        if errs and "loc" in errs[0]:
            loc = errs[0]["loc"]
            if loc and loc[-1] == "content":
                msg = "Content must not be empty. The file may have no extractable text."
        logger.error(f"Validation error in analyze: {msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        ) from e

    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {e}", exc_info=True)
        detail = "An unexpected error occurred"
        if getattr(settings, "DEBUG", False):
            detail = f"{detail}: {type(e).__name__}: {e}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


def _run_analysis_with_queue(prd, queue: Queue, deep: bool = False) -> None:
    """Run analyzer in thread; push progress events to queue. deep=True = slow path (multi-LLM)."""
    def callback(event_type: str, data: dict) -> None:
        queue.put({"event": event_type, "data": data})

    try:
        analyzer_service.analyze_prd(prd, progress_callback=callback, deep=deep)
    except Exception as e:
        logger.error(f"Stream analysis failed: {e}", exc_info=True)
        queue.put({"event": "error", "data": {"message": str(e)}})


@router.post("/analyze/stream")
async def analyze_prd_stream(
    file: UploadFile | None = File(None, description="PRD file to upload"),
    text: str | None = Form(None, description="PRD text content to paste"),
    deep: bool = Query(False, description="Slow path: per-section analysis (multiple LLM calls)"),
):
    """
    Upload PRD and run analysis; stream progress as Server-Sent Events.

    Default: 1 LLM call (fast). deep=true: slow path with per-section calls.
    """
    if file and text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either file upload or text content, not both",
        )
    if not file and not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either file upload or text content",
        )

    try:
        if file:
            file_content = await file.read()
            prd = prd_service.create_prd_from_file(file_content, file.filename or "uploaded_file")
        else:
            prd = prd_service.create_prd_from_text(text)
    except (ValidationError, FileParseError, ValueError, PydanticValidationError) as e:
        msg = getattr(e, "message", str(e))
        if hasattr(e, "errors") and e.errors():
            msg = e.errors()[0].get("msg", msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    event_queue: Queue = Queue()

    async def event_generator():
        loop = asyncio.get_event_loop()
        task = loop.run_in_executor(None, _run_analysis_with_queue, prd, event_queue, deep)
        while True:
            try:
                item = event_queue.get_nowait()
            except Empty:
                await asyncio.sleep(0.05)
                continue
            ev = item.get("event", "")
            data = item.get("data") or {}
            yield _sse_message(ev, data)
            if ev in ("complete", "error"):
                break
        try:
            await task  # ensure executor task finishes
        except Exception:
            pass  # already sent error event if any

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
