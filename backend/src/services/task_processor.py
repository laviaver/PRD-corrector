"""
Background task processor for async PRD analysis.

This module handles asynchronous analysis processing.
"""

import asyncio
from typing import Callable
from uuid import UUID

from src.models.prd import PRD
from src.services.analyzer import analyzer_service
from src.services.prd_service import prd_service
from src.utils.logger import get_logger

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
        Run analysis in background.

        Args:
            prd: PRD to analyze

        Returns:
            Analysis ID
        """
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
            
            # Run analysis (this is CPU/IO bound, so we run in executor)
            loop = asyncio.get_event_loop()
            analysis = await loop.run_in_executor(
                None, analyzer_service.analyze_prd, prd
            )
            logger.info(f"Background analysis completed: {analysis.id}")
            return analysis.id
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


# Global task processor instance
task_processor = TaskProcessor()
