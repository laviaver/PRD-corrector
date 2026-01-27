"""
Caching service for analysis results.

This module provides in-memory caching for MVP. Phase 2 will use Redis or similar.
"""

from typing import Optional
from uuid import UUID

from src.models.analysis import Analysis
from src.models.suggestion import Suggestion
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """In-memory cache service for MVP."""

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize cache.

        Args:
            ttl_seconds: Time to live in seconds (default 1 hour)
        """
        self.ttl = ttl_seconds
        self._cache: dict[UUID, tuple[Analysis, list[Suggestion], float]] = {}

    def get_analysis(self, analysis_id: UUID) -> Optional[tuple[Analysis, list[Suggestion]]]:
        """
        Get cached analysis.

        Args:
            analysis_id: Analysis identifier

        Returns:
            Tuple of (Analysis, Suggestions) if cached and not expired, None otherwise
        """
        if analysis_id not in self._cache:
            return None

        analysis, suggestions, cached_at = self._cache[analysis_id]

        # Check expiration
        from time import time

        if time() - cached_at > self.ttl:
            del self._cache[analysis_id]
            logger.debug(f"Cache expired for analysis: {analysis_id}")
            return None

        logger.debug(f"Cache hit for analysis: {analysis_id}")
        return analysis, suggestions

    def set_analysis(
        self, analysis_id: UUID, analysis: Analysis, suggestions: list[Suggestion]
    ):
        """
        Cache analysis results.

        Args:
            analysis_id: Analysis identifier
            analysis: Analysis object
            suggestions: List of suggestions
        """
        from time import time

        self._cache[analysis_id] = (analysis, suggestions, time())
        logger.debug(f"Cached analysis: {analysis_id}")

    def clear(self, analysis_id: UUID):
        """Clear cache for specific analysis."""
        if analysis_id in self._cache:
            del self._cache[analysis_id]
            logger.debug(f"Cleared cache for analysis: {analysis_id}")

    def clear_all(self):
        """Clear all cache."""
        self._cache.clear()
        logger.debug("Cleared all cache")


# Global cache instance
cache_service = CacheService()
