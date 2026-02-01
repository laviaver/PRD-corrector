"""
Analysis service for managing analysis lifecycle.

This service coordinates analysis creation, status tracking, and retrieval.
"""

from uuid import UUID

from src.models.analysis import Analysis, AnalysisStatus
from src.models.suggestion import Suggestion
from src.services.storage import storage
from src.services.task_processor import task_processor
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisService:
    """Service for analysis operations."""

    async def initiate_analysis(self, prd_id: UUID) -> Analysis:
        """
        Initiate analysis for a PRD.

        Args:
            prd_id: PRD identifier

        Returns:
            Analysis object with status PENDING or PROCESSING
        """
        # Create analysis record
        analysis = Analysis(
            prd_id=prd_id,
            status=AnalysisStatus.PENDING,
        )
        analysis = storage.create_analysis(analysis)

        # Start background processing (don't await - let it run in background)
        try:
            # Create background task without awaiting
            import asyncio
            asyncio.create_task(task_processor.process_analysis(prd_id))
            logger.info(f"Analysis task started in background for PRD: {prd_id}")
        except Exception as e:
            logger.error(f"Failed to start analysis task: {e}", exc_info=True)
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            storage.update_analysis(analysis)

        return analysis

    def create_analysis_converting(self) -> Analysis:
        """
        Create an analysis record in CONVERTING state (no PRD yet).
        Used for file uploads; background task will set prd_id and move to PENDING.
        """
        from src.models.analysis import Analysis
        analysis = Analysis(
            prd_id=None,
            status=AnalysisStatus.CONVERTING,
        )
        analysis = storage.create_analysis(analysis)
        logger.info(f"Analysis created in CONVERTING state: {analysis.id}")
        return analysis

    def get_analysis(self, analysis_id: UUID) -> Analysis | None:
        """
        Retrieve analysis by ID.

        Args:
            analysis_id: Analysis identifier

        Returns:
            Analysis if found, None otherwise
        """
        return storage.get_analysis(analysis_id)

    def get_analysis_status(self, analysis_id: UUID) -> dict:
        """
        Get analysis status.

        Args:
            analysis_id: Analysis identifier

        Returns:
            Status dictionary (prd_id may be null while status is converting)
        """
        analysis = storage.get_analysis(analysis_id)
        if not analysis:
            return {"status": "not_found"}

        out = {
            "status": analysis.status.value,
            "prd_id": str(analysis.prd_id) if analysis.prd_id else None,
            "started_at": analysis.started_at.isoformat() if analysis.started_at else None,
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
            "error_message": analysis.error_message,
        }
        if analysis.scores is not None:
            out["scores"] = analysis.scores.model_dump()
        if analysis.section_status is not None:
            out["section_status"] = [e.model_dump() for e in analysis.section_status]
        if analysis.incomplete_sections is not None:
            out["incomplete_sections"] = analysis.incomplete_sections
        return out

    def get_suggestions(self, analysis_id: UUID) -> list[Suggestion]:
        """
        Get suggestions for an analysis.

        Args:
            analysis_id: Analysis identifier

        Returns:
            List of suggestions
        """
        return storage.get_suggestions_by_analysis(analysis_id)


# Global service instance
analysis_service = AnalysisService()
