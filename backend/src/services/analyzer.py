"""
PRD analyzer service.

This service orchestrates PRD analysis using LLM and generates structured suggestions.
"""

import json
import re
from typing import List
from uuid import UUID

from src.models.analysis import Analysis, AnalysisStatus
from src.models.prd import PRD
from src.models.suggestion import Suggestion, SuggestionCategory, SuggestionPriority
from src.services.llm_service import llm_service
from src.services.prompts import PRD_ANALYSIS_SYSTEM_PROMPT, PRD_ANALYSIS_USER_PROMPT_TEMPLATE
from src.services.storage import storage
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyzerService:
    """Service for analyzing PRDs."""

    def analyze_prd(self, prd: PRD) -> Analysis:
        """
        Analyze a PRD and generate suggestions.

        Args:
            prd: PRD to analyze

        Returns:
            Analysis with generated suggestions
        """
        # Create analysis record
        analysis = Analysis(
            prd_id=prd.id,
            status=AnalysisStatus.PROCESSING,
        )
        analysis = storage.create_analysis(analysis)

        try:
            logger.info(f"Starting LLM analysis for PRD: {prd.id}, content length: {len(prd.content)}")
            
            # Get LLM analysis (prompt is now handled inside llm_service)
            llm_response = llm_service.analyze_prd(prd.content, PRD_ANALYSIS_SYSTEM_PROMPT)
            
            logger.info(f"LLM response received, length: {len(llm_response) if llm_response else 0}")

            # Parse LLM response into suggestions
            suggestions = self._parse_llm_response(llm_response, analysis.id)
            logger.info(f"Parsed {len(suggestions)} suggestions from LLM response")
            
            # If no suggestions found, log and create helpful default
            if not suggestions:
                logger.warning(f"No suggestions parsed from LLM response. Response length: {len(llm_response)}, Preview: {llm_response[:500]}")
                # Try to parse the raw response to see what we got
                try:
                    import json
                    parsed = json.loads(llm_response)
                    logger.warning(f"Parsed JSON structure: {type(parsed)}, Keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'N/A'}")
                except:
                    pass
                
                # Create a default suggestion indicating the analysis completed but found no issues
                # This should rarely happen with the improved prompt
                default_suggestion = Suggestion(
                    analysis_id=analysis.id,
                    category=SuggestionCategory.BEST_PRACTICES,
                    priority=SuggestionPriority.LOW,
                    title="Analysis completed - review the PRD manually",
                    explanation="The automated analysis completed but did not generate specific suggestions. This might indicate the PRD is well-structured, or there was an issue parsing the LLM response. Please review the PRD manually for best practices.",
                )
                suggestions = [default_suggestion]

            # Store suggestions
            for suggestion in suggestions:
                storage.create_suggestion(suggestion)

            # Update analysis status
            analysis.status = AnalysisStatus.COMPLETED
            analysis.summary = self._generate_summary(suggestions)
            storage.update_analysis(analysis)

            logger.info(f"Analysis completed: {analysis.id} with {len(suggestions)} suggestions")
            return analysis

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            storage.update_analysis(analysis)
            raise

    def _parse_llm_response(self, llm_response: str, analysis_id: UUID) -> List[Suggestion]:
        """
        Parse LLM response into structured suggestions.

        This is a simplified parser. In production, you might use structured output
        or function calling for more reliable parsing.

        Args:
            llm_response: Raw LLM response
            analysis_id: Analysis ID

        Returns:
            List of Suggestion objects
        """
        suggestions = []

        # Try to parse as JSON first
        try:
            data = json.loads(llm_response)
            if isinstance(data, list):
                for item in data:
                    suggestion = self._create_suggestion_from_dict(item, analysis_id)
                    if suggestion:
                        suggestions.append(suggestion)
            elif isinstance(data, dict) and 'suggestions' in data:
                for item in data['suggestions']:
                    suggestion = self._create_suggestion_from_dict(item, analysis_id)
                    if suggestion:
                        suggestions.append(suggestion)
        except json.JSONDecodeError:
            # Fallback: Try to extract suggestions from text
            suggestions = self._parse_text_response(llm_response, analysis_id)

        return suggestions

    def _create_suggestion_from_dict(self, data: dict, analysis_id: UUID) -> Suggestion | None:
        """Create a Suggestion from a dictionary."""
        try:
            category_str = data.get('category', 'best_practices').lower()
            priority_str = data.get('priority', 'medium').lower()

            # Map category string to enum
            category_map = {
                'structure': SuggestionCategory.STRUCTURE,
                'clarity': SuggestionCategory.CLARITY,
                'completeness': SuggestionCategory.COMPLETENESS,
                'best_practices': SuggestionCategory.BEST_PRACTICES,
                'technical_quality': SuggestionCategory.TECHNICAL_QUALITY,
            }
            category = category_map.get(category_str, SuggestionCategory.BEST_PRACTICES)

            # Map priority string to enum
            priority_map = {
                'high': SuggestionPriority.HIGH,
                'medium': SuggestionPriority.MEDIUM,
                'low': SuggestionPriority.LOW,
            }
            priority = priority_map.get(priority_str, SuggestionPriority.MEDIUM)

            return Suggestion(
                analysis_id=analysis_id,
                category=category,
                priority=priority,
                title=data.get('title', 'Suggestion'),
                explanation=data.get('explanation', ''),
                example=data.get('example'),
                template=data.get('template'),
            )
        except Exception as e:
            logger.warning(f"Failed to create suggestion from dict: {e}")
            return None

    def _parse_text_response(self, llm_response: str, analysis_id: UUID) -> List[Suggestion]:
        """Parse text response into suggestions (fallback method)."""
        suggestions = []
        # Simple pattern matching - in production, use more sophisticated parsing
        # or structured output from LLM
        lines = llm_response.split('\n')
        current_suggestion = None

        for line in lines:
            if re.match(r'^\d+\.', line) or '**' in line:
                if current_suggestion:
                    suggestions.append(current_suggestion)
                # Start new suggestion
                current_suggestion = Suggestion(
                    analysis_id=analysis_id,
                    category=SuggestionCategory.BEST_PRACTICES,
                    priority=SuggestionPriority.MEDIUM,
                    title=line.strip(),
                    explanation='',
                )
            elif current_suggestion:
                current_suggestion.explanation += line + '\n'

        if current_suggestion:
            suggestions.append(current_suggestion)

        return suggestions

    def _generate_summary(self, suggestions: List[Suggestion]) -> dict:
        """Generate analysis summary statistics."""
        from src.models.analysis import AnalysisSummary

        by_category = {}
        by_priority = {'high': 0, 'medium': 0, 'low': 0}

        for suggestion in suggestions:
            category = suggestion.category.value
            by_category[category] = by_category.get(category, 0) + 1

            priority = suggestion.priority.value
            by_priority[priority] = by_priority.get(priority, 0) + 1

        return AnalysisSummary(
            total_suggestions=len(suggestions),
            suggestions_by_category=by_category,
            suggestions_by_priority=by_priority,
        )


# Global service instance
analyzer_service = AnalyzerService()
