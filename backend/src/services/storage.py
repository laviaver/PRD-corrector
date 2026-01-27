"""
In-memory storage service for PRD and Analysis data.

This module provides session-based storage for MVP. Phase 2 will migrate to persistent storage.
"""

from typing import Dict, Optional
from uuid import UUID

from src.models.analysis import Analysis
from src.models.prd import PRD
from src.models.suggestion import Suggestion
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StorageService:
    """
    In-memory storage service for PRD Reviewer data.

    This is a simple in-memory implementation for MVP. In Phase 2, this will be
    replaced with a database-backed implementation.
    """

    def __init__(self):
        """Initialize storage with empty dictionaries."""
        self._prds: Dict[UUID, PRD] = {}
        self._analyses: Dict[UUID, Analysis] = {}
        self._suggestions: Dict[UUID, Suggestion] = {}
        logger.info("Storage service initialized (in-memory)")

    # PRD operations
    def create_prd(self, prd: PRD) -> PRD:
        """
        Store a PRD.

        Args:
            prd: PRD model to store

        Returns:
            Stored PRD (with generated ID if not provided)
        """
        self._prds[prd.id] = prd
        logger.debug(f"PRD created: {prd.id}")
        return prd

    def get_prd(self, prd_id: UUID) -> Optional[PRD]:
        """
        Retrieve a PRD by ID.

        Args:
            prd_id: PRD identifier

        Returns:
            PRD if found, None otherwise
        """
        return self._prds.get(prd_id)

    def delete_prd(self, prd_id: UUID) -> bool:
        """
        Delete a PRD.

        Args:
            prd_id: PRD identifier

        Returns:
            True if deleted, False if not found
        """
        if prd_id in self._prds:
            del self._prds[prd_id]
            logger.debug(f"PRD deleted: {prd_id}")
            return True
        return False

    # Analysis operations
    def create_analysis(self, analysis: Analysis) -> Analysis:
        """
        Store an analysis.

        Args:
            analysis: Analysis model to store

        Returns:
            Stored Analysis (with generated ID if not provided)
        """
        self._analyses[analysis.id] = analysis
        logger.debug(f"Analysis created: {analysis.id}")
        return analysis

    def get_analysis(self, analysis_id: UUID) -> Optional[Analysis]:
        """
        Retrieve an analysis by ID.

        Args:
            analysis_id: Analysis identifier

        Returns:
            Analysis if found, None otherwise
        """
        return self._analyses.get(analysis_id)

    def update_analysis(self, analysis: Analysis) -> bool:
        """
        Update an existing analysis.

        Args:
            analysis: Analysis with updated fields

        Returns:
            True if updated, False if not found
        """
        if analysis.id in self._analyses:
            self._analyses[analysis.id] = analysis
            logger.debug(f"Analysis updated: {analysis.id}")
            return True
        return False

    def get_analyses_by_prd(self, prd_id: UUID) -> list[Analysis]:
        """
        Get all analyses for a PRD.

        Args:
            prd_id: PRD identifier

        Returns:
            List of analyses for the PRD
        """
        return [a for a in self._analyses.values() if a.prd_id == prd_id]

    # Suggestion operations
    def create_suggestion(self, suggestion: Suggestion) -> Suggestion:
        """
        Store a suggestion.

        Args:
            suggestion: Suggestion model to store

        Returns:
            Stored Suggestion (with generated ID if not provided)
        """
        self._suggestions[suggestion.id] = suggestion
        logger.debug(f"Suggestion created: {suggestion.id}")
        return suggestion

    def get_suggestions_by_analysis(self, analysis_id: UUID) -> list[Suggestion]:
        """
        Get all suggestions for an analysis.

        Args:
            analysis_id: Analysis identifier

        Returns:
            List of suggestions for the analysis
        """
        return [s for s in self._suggestions.values() if s.analysis_id == analysis_id]

    def delete_suggestions_by_analysis(self, analysis_id: UUID) -> int:
        """
        Delete all suggestions for an analysis.

        Args:
            analysis_id: Analysis identifier

        Returns:
            Number of suggestions deleted
        """
        to_delete = [s.id for s in self._suggestions.values() if s.analysis_id == analysis_id]
        for suggestion_id in to_delete:
            del self._suggestions[suggestion_id]
        logger.debug(f"Deleted {len(to_delete)} suggestions for analysis {analysis_id}")
        return len(to_delete)


# Global storage instance
storage = StorageService()
