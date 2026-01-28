"""
PRD analyzer service.

This service orchestrates PRD analysis using LLM and generates structured suggestions.
Supports parallel section analysis (suggestion 5) for faster results on long PRDs.
"""

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

from src.models.analysis import Analysis, AnalysisStatus
from src.models.prd import PRD
from src.models.suggestion import Suggestion, SuggestionCategory, SuggestionPriority
from src.services.llm_service import llm_service
from src.services.prompts import (
    PRD_ANALYSIS_SYSTEM_PROMPT,
    PRD_ANALYSIS_USER_PROMPT_TEMPLATE,
    PRD_SECTION_SYSTEM_PROMPT,
    PRD_SECTION_USER_TEMPLATE,
)
from src.services.storage import storage
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Parallel section analysis: max sections to analyze in parallel
MAX_PARALLEL_SECTIONS = 8
MIN_SECTION_CHARS = 200
SECTION_MAX_TOKENS = 800  # per-section output cap


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

            sections = self._split_into_sections(prd.content)
            if len(sections) < 2:
                # Single block or no clear sections: one full-doc call
                llm_response = llm_service.analyze_prd(prd.content, PRD_ANALYSIS_SYSTEM_PROMPT)
                logger.info(f"LLM response received (full doc), length: {len(llm_response) if llm_response else 0}")
                suggestions = self._parse_llm_response(llm_response, analysis.id)
            else:
                # Parallel section analysis (suggestion 5)
                suggestions = self._analyze_sections_parallel(
                    sections, analysis.id, max_workers=min(len(sections), MAX_PARALLEL_SECTIONS)
                )
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

    def _split_into_sections(self, content: str) -> List[Tuple[str, str]]:
        """Split PRD content into (section_name, section_content) by markdown headers."""
        if not content or not content.strip():
            return []
        # Split by lines that look like "# Title" or "## Title"
        lines = content.strip().splitlines()
        sections: List[Tuple[str, str]] = []
        current_name = "Document"
        current_buf: List[str] = []

        for line in lines:
            header_match = re.match(r'^(#{1,3})\s+(.+)$', line.strip())
            if header_match:
                body = "\n".join(current_buf).strip()
                if len(body) >= MIN_SECTION_CHARS:
                    sections.append((current_name, body))
                current_name = header_match.group(2).strip()
                current_buf = []
            else:
                current_buf.append(line)

        body = "\n".join(current_buf).strip()
        if len(body) >= MIN_SECTION_CHARS:
            sections.append((current_name, body))
        if not sections and content.strip():
            return [("Document", content.strip())]
        return sections[:MAX_PARALLEL_SECTIONS]

    def _analyze_sections_parallel(
        self, sections: List[Tuple[str, str]], analysis_id: UUID, max_workers: int = 4
    ) -> List[Suggestion]:
        """Run LLM per section in parallel, merge and dedupe suggestions."""

        def job(section_name: str, section_content: str) -> str:
            user_prompt = PRD_SECTION_USER_TEMPLATE.format(
                section_name=section_name,
                section_content=(section_content[:12000] if len(section_content) > 12000 else section_content),
            )
            return llm_service.analyze_with_prompts(
                PRD_SECTION_SYSTEM_PROMPT,
                user_prompt,
                max_tokens=SECTION_MAX_TOKENS,
            )

        merged: List[Suggestion] = []
        seen_titles: set[str] = set()
        max_total = 10  # cap merged suggestions

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(job, name, content): (name, content)
                for name, content in sections
            }
            for future in as_completed(futures):
                name, _ = futures[future]
                try:
                    raw = future.result()
                    for s in self._parse_llm_response(raw, analysis_id):
                        norm = (s.title or "").lower().strip()
                        if norm and norm not in seen_titles and len(merged) < max_total:
                            seen_titles.add(norm)
                            merged.append(s)
                except Exception as e:
                    logger.warning(f"Section '{name}' analysis failed: {e}")

        return merged

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
