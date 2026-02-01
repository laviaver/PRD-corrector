"""
Background task processor for async PRD analysis.

This module handles asynchronous analysis processing, including file conversion
then analysis for uploaded files.
"""

import asyncio
from io import BytesIO
from typing import Callable
from uuid import UUID

from src.config import settings
from src.models.analysis import AnalysisStatus
from src.models.prd import PRD
from src.services.analyzer import analyzer_service
from src.services.prd_service import prd_service
from src.services.storage import storage
from src.utils.file_parser import FileParseError, parse_file
from src.utils.logger import get_logger
from src.services.validation import validate_file_type

logger = get_logger(__name__)


class TaskProcessor:
    """Processor for background analysis tasks."""

    def __init__(self):
        """Initialize task processor."""
        self._tasks: dict[UUID, asyncio.Task] = {}

    async def process_analysis(self, prd_id: UUID) -> UUID:
        """
        Process PRD analysis asynchronously.

        Args:
            prd_id: PRD identifier

        Returns:
            Analysis ID
        """
        # Get PRD
        prd = prd_service.get_prd(prd_id)
        if not prd:
            raise ValueError(f"PRD not found: {prd_id}")

        # Create and run analysis task
        task = asyncio.create_task(self._run_analysis(prd))
        analysis_id = await task

        return analysis_id

    async def _run_analysis(self, prd: PRD) -> UUID:
        """
        Run analysis in background with detailed timing.
        """
        loop = asyncio.get_event_loop()
        t_start = loop.time()
        logger.info(f"[TIMING] Task processor starting analysis for PRD {prd.id}")

        try:
            # Get the analysis that was created (it should be PENDING)
            from src.services.storage import storage
            from src.services.analysis_service import analysis_service
            
            # Find the analysis for this PRD
            analyses = storage.get_analyses_by_prd(prd.id)
            if not analyses:
                raise ValueError(f"No analysis found for PRD: {prd.id}")
            
            analysis = analyses[-1]  # Get the most recent one
            
            # Update status to PROCESSING
            from src.models.analysis import AnalysisStatus
            analysis.status = AnalysisStatus.PROCESSING
            storage.update_analysis(analysis)
            logger.info(f"Analysis status updated to PROCESSING: {analysis.id}")

            def _log_progress(event_type: str, data: dict) -> None:
                logger.info("analysis progress: %s", event_type)

            # Run analysis with timeout so we never hang indefinitely (fixes 60s "stuck" UX)
            t_before_exec = loop.time()
            logger.info(
                f"[TIMING] Calling analyzer.analyze_prd via executor (timeout={settings.MAX_ANALYSIS_TIMEOUT_SEC}s)",
            )
            analysis = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: analyzer_service.analyze_prd(
                        prd,
                        progress_callback=_log_progress,
                        existing_analysis_id=analysis.id,
                    ),
                ),
                timeout=settings.MAX_ANALYSIS_TIMEOUT_SEC,
            )
            t_after_exec = loop.time()
            logger.info(f"[TIMING] Executor completed in {(t_after_exec - t_before_exec) * 1000:.0f}ms")

            t_end = loop.time()
            logger.info(f"[TIMING] ✓ Task processor COMPLETE in {(t_end - t_start) * 1000:.0f}ms total")
            logger.info(f"Background analysis completed: {analysis.id}")
            return analysis.id
        except asyncio.TimeoutError:
            t_timeout = loop.time()
            logger.error(
                f"[TIMING] ✗ TIMEOUT after {(t_timeout - t_start) * 1000:.0f}ms "
                f"(limit was {settings.MAX_ANALYSIS_TIMEOUT_SEC}s)",
            )
            logger.error(
                f"Analysis timed out after {settings.MAX_ANALYSIS_TIMEOUT_SEC}s for PRD: {prd.id}",
            )
            try:
                from src.services.storage import storage
                from src.models.analysis import AnalysisStatus
                analyses = storage.get_analyses_by_prd(prd.id)
                if analyses:
                    analysis = analyses[-1]
                    analysis.status = AnalysisStatus.FAILED
                    analysis.error_message = (
                        f"Analysis timed out after {settings.MAX_ANALYSIS_TIMEOUT_SEC} seconds"
                    )
                    storage.update_analysis(analysis)
            except Exception as update_err:
                logger.error(f"Failed to update analysis status after timeout: {update_err}")
            raise
        except Exception as e:
            logger.error(f"Background analysis failed: {e}", exc_info=True)
            # Update analysis status to FAILED
            try:
                from src.services.storage import storage
                from src.models.analysis import AnalysisStatus
                analyses = storage.get_analyses_by_prd(prd.id)
                if analyses:
                    analysis = analyses[-1]
                    analysis.status = AnalysisStatus.FAILED
                    analysis.error_message = str(e)
                    storage.update_analysis(analysis)
            except:
                pass
            raise


    async def process_file_conversion_and_analysis(self, analysis_id: UUID) -> None:
        """
        Load pending file for this analysis, convert to text, create PRD, then run analysis.

        If no pending file exists or conversion fails, marks analysis as FAILED.
        """
        analysis = storage.get_analysis(analysis_id)
        if not analysis or analysis.status != AnalysisStatus.CONVERTING:
            logger.warning(f"process_file_conversion_and_analysis: no CONVERTING analysis {analysis_id}")
            return

        entry = storage.get_and_remove_pending_upload(analysis_id)
        if not entry:
            logger.error(f"No pending upload for analysis {analysis_id}; marking FAILED")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = "No pending file for conversion"
            storage.update_analysis(analysis)
            return

        file_bytes, filename = entry
        try:
            file_type = validate_file_type(filename)
        except Exception as e:
            logger.error(f"Invalid file type for {filename}: {e}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            storage.update_analysis(analysis)
            return

        try:
            content = parse_file(BytesIO(file_bytes), filename, file_type)
        except FileParseError as e:
            logger.error(f"Parse failed for {filename}: {e.message}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = f"Failed to convert file: {e.message}"
            storage.update_analysis(analysis)
            return
        except Exception as e:
            logger.error(f"Unexpected error converting {filename}: {e}", exc_info=True)
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            storage.update_analysis(analysis)
            return

        try:
            prd = prd_service.create_prd_from_extracted_text(
                content=content,
                filename=filename,
                file_type=file_type,
                size=len(file_bytes),
            )
        except Exception as e:
            logger.error(f"Failed to create PRD from extracted text: {e}", exc_info=True)
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            storage.update_analysis(analysis)
            return

        analysis.prd_id = prd.id
        analysis.status = AnalysisStatus.PENDING
        storage.update_analysis(analysis)
        logger.info(f"Conversion done for analysis {analysis_id}; PRD {prd.id}; starting analysis")

        try:
            await self.process_analysis(prd.id)
        except Exception as e:
            logger.error(f"Analysis failed after conversion for {analysis_id}: {e}", exc_info=True)
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            storage.update_analysis(analysis)


# Global task processor instance
task_processor = TaskProcessor()
