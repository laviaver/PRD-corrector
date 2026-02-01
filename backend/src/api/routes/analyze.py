"""
Analyze endpoint for PRD upload and text paste.

This endpoint handles file uploads and text paste, creates PRD, and initiates analysis.
Supports streaming (SSE) via POST /api/analyze/stream.
"""

import asyncio
import json
import time
from queue import Empty, Queue

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, status

# #region agent log
_DEBUG_LOG = "/Users/lavia/PRD-corrector/.cursor/debug.log"
def _dbg(loc: str, msg: str, data: dict, hyp: str):
    try:
        with open(_DEBUG_LOG, "a") as f:
            f.write(json.dumps({"location": loc, "message": msg, "data": data, "timestamp": time.time() * 1000, "sessionId": "debug-session", "hypothesisId": hyp}) + "\n")
    except Exception:
        pass
# #endregion
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError as PydanticValidationError

from src.config import settings
from src.services.prd_service import prd_service
from src.services.analysis_service import analysis_service
from src.services.storage import storage
from src.services.task_processor import task_processor
from src.services.analyzer import analyzer_service
from src.services.validation import ValidationError, validate_file
from src.utils.file_parser import FileParseError, parse_file
from src.utils.logger import get_logger
from io import BytesIO

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

    prd_id: str | None  # null for file uploads until conversion completes
    analysis_id: str | None = None
    message: str


class PreviewMarkdownResponse(BaseModel):
    """Response model for preview-markdown endpoint."""

    markdown: str


@router.post("/preview-markdown", response_model=PreviewMarkdownResponse)
async def preview_markdown(file: UploadFile = File(..., description="PRD file to convert to markdown")):
    """
    Convert uploaded PRD file to markdown (same conversion used for analysis).
    Returns the markdown string so the client can show it before uploading for analysis.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name required")
    file_content = await file.read()
    file_io = BytesIO(file_content)
    try:
        file_type, _ = validate_file(file_io, file.filename)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
    try:
        file_io.seek(0)
        markdown = parse_file(file_io, file.filename, file_type)
    except FileParseError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message or "Failed to convert file to markdown",
        ) from e
    return PreviewMarkdownResponse(markdown=markdown)


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
    # #region agent log
    _dbg("analyze.py:analyze_prd_entry", "analyze_prd entry", {"has_file": file is not None, "has_text": text is not None}, "A")
    # #endregion
    try:
        return await _analyze_prd_impl(file, text)
    except HTTPException:
        raise
    except BaseException as e:
        # #region agent log
        _dbg("analyze.py:analyze_prd_top_level_catch", "top-level BaseException", {"exc_type": type(e).__name__, "exc_msg": str(e)[:200]}, "B")
        # #endregion
        logger.error("Analyze endpoint top-level error", exc_info=True)
        exc_str = f"{type(e).__name__}: {e}"[:400]
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error. {exc_str}",
        ) from e


async def _analyze_prd_impl(
    file: UploadFile | None,
    text: str | None,
) -> AnalyzeResponse:
    """Implementation of analyze endpoint (called so we can catch all exceptions in the route)."""
    # #region agent log
    _dbg("analyze.py:_analyze_prd_impl_entry", "impl entry", {"has_file": file is not None}, "B")
    # #endregion
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
        # Handle file upload: validate only, store raw file, convert in background
        if file:
            logger.info("Analyze file upload started")
            # #region agent log
            _dbg("analyze.py:before_file_read", "before file.read", {}, "B")
            # #endregion
            file_content = await file.read()
            # #region agent log
            _dbg("analyze.py:after_file_read", "after file.read", {"len": len(file_content)}, "B")
            # #endregion
            filename = file.filename or "uploaded_file"
            from io import BytesIO
            file_io = BytesIO(file_content)
            try:
                file_type, size = validate_file(file_io, filename)
            except ValidationError as e:
                logger.error(f"File validation failed for {filename}: {e.message}")
                raise
            try:
                # #region agent log
                _dbg("analyze.py:before_create_analysis_converting", "before create_analysis_converting", {}, "B")
                # #endregion
                analysis = analysis_service.create_analysis_converting()
                # #region agent log
                _dbg("analyze.py:after_create_analysis_converting", "after create_analysis_converting", {"analysis_id": str(analysis.id)}, "B")
                # #endregion
                storage.set_pending_upload(analysis.id, file_content, filename)
                asyncio.create_task(task_processor.process_file_conversion_and_analysis(analysis.id))
            except Exception as e:
                logger.error(f"Failed to create analysis or store pending upload: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to start analysis. Please try again.",
                ) from e
            logger.info(f"[TIMING] Endpoint returning 201 with analysis_id={analysis.id} (file upload, CONVERTING)")
            # #region agent log
            _dbg("analyze.py:returning_201_file", "returning 201 file upload", {"analysis_id": str(analysis.id)}, "C")
            # #endregion
            return AnalyzeResponse(
                prd_id=None,
                analysis_id=str(analysis.id),
                message="File received. Converting to text, then analysis will start.",
            )

        # Handle text paste: create PRD and initiate analysis in request
        else:  # text is guaranteed to be not None here
            prd = prd_service.create_prd_from_text(text)
            logger.info(f"PRD created from text: {prd.id}")
            analysis = await analysis_service.initiate_analysis(prd.id)
            logger.info(f"[TIMING] Endpoint returning 201 with analysis_id={analysis.id}")

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
        ) from e

    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except PydanticValidationError as e:
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
        logger.error("Analyze endpoint error", exc_info=True)
        exc_str = f"{type(e).__name__}: {e}"[:400]
        detail = f"An unexpected error occurred. {exc_str}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        ) from e

    # Not reached
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unexpected state in analyze endpoint",
    )


def _run_analysis_with_queue(prd, queue: Queue, deep: bool = False) -> None:
    """Run analyzer in thread; push progress events to queue. Guarantees complete/error event."""
    completion_sent = False

    def callback(event_type: str, data: dict) -> None:
        queue.put({"event": event_type, "data": data})

    try:
        analyzer_service.analyze_prd(prd, progress_callback=callback, deep=deep)
        completion_sent = True  # analyzer emitted "complete" via callback
    except Exception as e:
        logger.error(f"Stream analysis failed: {e}", exc_info=True)
        queue.put({"event": "error", "data": {"message": str(e)}})
        completion_sent = True
    finally:
        if not completion_sent:
            logger.error("Analysis ended without sending completion - sending error event")
            queue.put({
                "event": "error",
                "data": {"message": "Analysis ended unexpectedly"},
            })


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
        timeout_sec = settings.MAX_ANALYSIS_TIMEOUT_SEC
        start_time = loop.time()
        task = loop.run_in_executor(None, _run_analysis_with_queue, prd, event_queue, deep)
        while True:
            elapsed = loop.time() - start_time
            if elapsed > timeout_sec:
                logger.error(f"Stream timeout after {elapsed:.1f}s")
                yield _sse_message("error", {
                    "error": "Analysis timeout - please try again or contact support",
                })
                break
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
