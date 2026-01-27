"""
Export service for generating analysis exports.

This module handles exporting analysis results to various formats (PDF, Markdown, JSON).
"""

import json
from pathlib import Path
from typing import List
from uuid import UUID

from src.models.analysis import Analysis
from src.models.export import Export, ExportFormat
from src.models.suggestion import Suggestion
from src.services.storage import storage
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExportService:
    """Service for exporting analysis results."""

    def export_analysis(
        self, analysis_id: UUID, format: ExportFormat
    ) -> Export:
        """
        Export analysis results to specified format.

        Args:
            analysis_id: Analysis identifier
            format: Export format (PDF, Markdown, JSON)

        Returns:
            Export object with file path

        Raises:
            ValueError: If analysis not found
        """
        analysis = storage.get_analysis(analysis_id)
        if not analysis:
            raise ValueError(f"Analysis not found: {analysis_id}")

        suggestions = storage.get_suggestions_by_analysis(analysis_id)

        if format == ExportFormat.JSON:
            return self._export_json(analysis, suggestions)
        elif format == ExportFormat.MARKDOWN:
            return self._export_markdown(analysis, suggestions)
        elif format == ExportFormat.PDF:
            return self._export_pdf(analysis, suggestions)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_json(self, analysis: Analysis, suggestions: List[Suggestion]) -> Export:
        """Export analysis as JSON."""
        from datetime import datetime

        data = {
            "analysis": analysis.model_dump(),
            "suggestions": [s.model_dump() for s in suggestions],
            "exported_at": datetime.utcnow().isoformat(),
        }

        # In production, save to file system or cloud storage
        # For MVP, return in-memory representation
        file_path = f"/tmp/analysis_{analysis.id}.json"

        export = Export(
            analysis_id=analysis.id,
            format=ExportFormat.JSON,
            file_path=file_path,
            created_at=datetime.utcnow().isoformat(),
        )

        logger.info(f"Exported analysis {analysis.id} as JSON")
        return export

    def _export_markdown(self, analysis: Analysis, suggestions: List[Suggestion]) -> Export:
        """Export analysis as Markdown."""
        from datetime import datetime

        md_lines = [
            f"# PRD Analysis Report",
            f"",
            f"**Analysis ID:** {analysis.id}",
            f"**Status:** {analysis.status.value}",
            f"**Created:** {analysis.started_at.isoformat() if analysis.started_at else 'N/A'}",
            f"",
        ]

        if analysis.summary:
            md_lines.extend([
                f"## Summary",
                f"",
                f"- Total Suggestions: {analysis.summary.total_suggestions}",
                f"",
            ])

        md_lines.append("## Suggestions\n")

        # Group by category
        by_category: dict[str, List[Suggestion]] = {}
        for suggestion in suggestions:
            category = suggestion.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(suggestion)

        for category, category_suggestions in by_category.items():
            md_lines.append(f"### {category.replace('_', ' ').title()}\n")
            for i, suggestion in enumerate(category_suggestions, 1):
                md_lines.extend([
                    f"#### {i}. {suggestion.title} [{suggestion.priority.value.upper()}]",
                    f"",
                    f"{suggestion.explanation}",
                    f"",
                ])
                if suggestion.example:
                    md_lines.extend([
                        f"**Example:**",
                        f"```",
                        suggestion.example,
                        f"```",
                        f"",
                    ])

        # In production, save to file system
        file_path = f"/tmp/analysis_{analysis.id}.md"

        export = Export(
            analysis_id=analysis.id,
            format=ExportFormat.MARKDOWN,
            file_path=file_path,
            created_at=datetime.utcnow().isoformat(),
        )

        logger.info(f"Exported analysis {analysis.id} as Markdown")
        return export

    def _export_pdf(self, analysis: Analysis, suggestions: List[Suggestion]) -> Export:
        """Export analysis as PDF."""
        from datetime import datetime

        # For MVP, we'll use a simple approach
        # In production, use a library like reportlab or weasyprint
        # For now, return a placeholder
        file_path = f"/tmp/analysis_{analysis.id}.pdf"

        export = Export(
            analysis_id=analysis.id,
            format=ExportFormat.PDF,
            file_path=file_path,
            created_at=datetime.utcnow().isoformat(),
        )

        logger.info(f"Exported analysis {analysis.id} as PDF (placeholder)")
        return export


# Global service instance
export_service = ExportService()
