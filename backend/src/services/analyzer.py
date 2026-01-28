"""
PRD analyzer service.

Single-pass default: 1 LLM call per request. Optional slow path (deep=True) for
per-section analysis. Deterministic routing; structure cached by content hash.
"""

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from typing import Callable, List, Tuple
from uuid import UUID

from src.config import settings
from src.models.analysis import Analysis, AnalysisScores, AnalysisStatus, SectionStatusEntry
from src.models.prd import PRD
from src.models.section_output import SectionSuggestionOutput
from src.models.suggestion import Suggestion, SuggestionCategory, SuggestionLocation, SuggestionPriority
from src.services.llm_service import llm_service
from src.services.best_practices_loader import (
    get_prd_analysis_system_prompt_base,
    get_stage2_system_prompt_base,
)
from src.services.prompts import (
    PRD_ANALYSIS_USER_PROMPT_TEMPLATE,
    STAGE2_SECTION_USER_TEMPLATE,
)
from src.services.storage import storage
from src.services.scoring import compute_scores
from src.services.structure_extractor import ExtractedSection, StructureExtractionResult, extract_structure
from src.services.structure_cache import get_structure_cached
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Latency rule: ≤1 LLM call per request (default); fail if >2 unintentionally
MAX_LLM_CALLS_PER_REQUEST = 2
# No tool calls in default path; log 0 unless we add function calling
TOOL_CALLS_DEFAULT = 0
# Slow path only (when deep=True)
MAX_PARALLEL_SECTIONS = 8
SECTION_MAX_TOKENS = 800
SECTION_TIMEOUT_SEC = 10
MAX_MERGED_SUGGESTIONS = 10
# Max wait for parallel structure fetch (structure is CPU-bound, should be fast)
STRUCTURE_FETCH_TIMEOUT_SEC = 30


class AnalyzerService:
    """Service for analyzing PRDs."""

    def analyze_prd(
        self,
        prd: PRD,
        progress_callback: Callable[[str, dict], None] | None = None,
        deep: bool = False,
    ) -> Analysis:
        """
        Analyze a PRD. Default: single-pass, 1 LLM call. deep=True: slow path (per-section).
        """
        t0 = time.perf_counter()
        llm_call_count: List[int] = [0]  # mutable so wrapper can increment

        analysis = Analysis(prd_id=prd.id, status=AnalysisStatus.PROCESSING)
        analysis = storage.create_analysis(analysis)

        def emit(event_type: str, data: dict) -> None:
            if progress_callback:
                progress_callback(event_type, data)

        try:
            emit("started", {"analysis_id": str(analysis.id)})

            # Latency rule: deterministic routing – no LLM for routing; rule-based.
            # Fast path (default): 1 LLM call. Slow path (deep): explicit multi-call.
            structure_result: StructureExtractionResult
            if deep:
                # Slow path: per-section LLM calls; run only when explicitly requested.
                # Latency rule: reuse structure for scoring – no second extraction.
                structure_result = extract_structure(prd.content)
                extracted = structure_result.sections
                if not extracted:
                    extracted = []  # will do single full-doc below
                if extracted:
                    suggestions, section_status_list = self._analyze_sections_stage2(
                        extracted,
                        analysis.id,
                        max_workers=min(len(extracted), MAX_PARALLEL_SECTIONS),
                        progress_callback=progress_callback,
                        llm_call_count=llm_call_count,
                    )
                    incomplete_sections = [
                        e.section_id for e in section_status_list
                        if e.status in ("timeout", "error")
                    ]
                else:
                    suggestions, section_status_list, incomplete_sections = self._single_llm_call(
                        prd, analysis, llm_call_count, emit
                    )
            else:
                # Fast path: single LLM call only. No ReAct, no retry loops.
                # Latency rule: parallelize non-dependent ops – run structure fetch with LLM.
                with ThreadPoolExecutor(max_workers=2) as executor:
                    f_llm = executor.submit(
                        self._single_llm_call,
                        prd, analysis, llm_call_count, emit,
                    )
                    f_struct = executor.submit(get_structure_cached, prd.content)
                    try:
                        suggestions, section_status_list, incomplete_sections = f_llm.result(
                            timeout=settings.LLM_TIMEOUT_SEC + 5
                        )
                        structure_result = f_struct.result(timeout=STRUCTURE_FETCH_TIMEOUT_SEC)
                    except FuturesTimeoutError:
                        f_llm.cancel()
                        raise

            # Instrumentation: fail if >2 LLM calls (unintentional)
            if llm_call_count[0] > MAX_LLM_CALLS_PER_REQUEST:
                logger.error(f"latency: llm_calls={llm_call_count[0]} exceeds max {MAX_LLM_CALLS_PER_REQUEST}")
                raise RuntimeError(f"Too many LLM calls: {llm_call_count[0]} (max {MAX_LLM_CALLS_PER_REQUEST})")

            t1 = time.perf_counter()
            # Instrumentation: log LLM/tool counts and time to first useful (latency rule).
            tool_call_count = TOOL_CALLS_DEFAULT
            logger.info(
                "latency: llm_calls=%s tool_calls=%s time_to_first_useful_ms=%.0f",
                llm_call_count[0],
                tool_call_count,
                (t1 - t0) * 1000,
            )

            logger.info(f"Parsed {len(suggestions)} suggestions from LLM response")

            # If no suggestions found, add helpful default
            if not suggestions:
                logger.warning("No suggestions parsed from LLM response.")
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

            # Latency rule: deterministic scoring – no LLM. Structure already set (fast: parallel fetch; deep: reuse).
            analysis.scores = compute_scores(structure_result.sections, suggestions)

            # Update analysis status
            analysis.status = AnalysisStatus.COMPLETED
            analysis.summary = self._generate_summary(suggestions)
            analysis.section_status = section_status_list if section_status_list else None
            analysis.incomplete_sections = incomplete_sections if incomplete_sections else None
            storage.update_analysis(analysis)

            emit("complete", {"analysis_id": str(analysis.id), "summary": analysis.summary.model_dump() if analysis.summary else None})
            logger.info(f"Analysis completed: {analysis.id} with {len(suggestions)} suggestions")
            return analysis

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            storage.update_analysis(analysis)
            raise

    def _single_llm_call(
        self,
        prd: PRD,
        analysis: Analysis,
        llm_call_count: List[int],
        emit: Callable[[str, dict], None],
    ) -> Tuple[List[Suggestion], List[SectionStatusEntry], List[str]]:
        """Single-pass: 1 LLM call only. Latency rule: one LLM call max for default path."""
        section_status_list: List[SectionStatusEntry] = []
        incomplete_sections: List[str] = []

        def one_call(content: str, system_prompt: str):
            llm_call_count[0] += 1
            return llm_service.analyze_prd(content, system_prompt)

        system_prompt = get_prd_analysis_system_prompt_base()
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(one_call, prd.content, system_prompt)
            try:
                llm_response = future.result(timeout=settings.LLM_TIMEOUT_SEC)
                suggestions = self._parse_llm_response(llm_response, analysis.id)
            except FuturesTimeoutError:
                logger.error(f"Analysis timed out after {settings.LLM_TIMEOUT_SEC}s")
                raise Exception(
                    f"Analysis timed out after {settings.LLM_TIMEOUT_SEC}s. Please try again or use a shorter PRD."
                )
        return suggestions, section_status_list, incomplete_sections

    def _analyze_sections_stage2(
        self,
        extracted: List[ExtractedSection],
        analysis_id: UUID,
        max_workers: int = 4,
        progress_callback: Callable[[str, dict], None] | None = None,
        llm_call_count: List[int] | None = None,
    ) -> Tuple[List[Suggestion], List[SectionStatusEntry]]:
        """Slow path only: per-section LLM calls. Instrumentation: count each call."""
        section_status_list: List[SectionStatusEntry] = []
        stage2_system_prompt = get_stage2_system_prompt_base()
        counter = llm_call_count if llm_call_count is not None else [0]

        def job(sec: ExtractedSection) -> str:
            counter[0] += 1
            user_prompt = STAGE2_SECTION_USER_TEMPLATE.format(
                section_id=sec.id,
                section_content=(sec.text[:12000] if len(sec.text) > 12000 else sec.text),
            )
            return llm_service.analyze_with_prompts(
                stage2_system_prompt,
                user_prompt,
                max_tokens=SECTION_MAX_TOKENS,
            )

        merged: List[Suggestion] = []
        seen_key: set[Tuple[str, str]] = set()  # (section, proposed) for dedupe

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(job, sec): sec for sec in extracted}
            for future in as_completed(futures):
                sec = futures[future]
                try:
                    raw = future.result(timeout=SECTION_TIMEOUT_SEC)
                    section_status_list.append(SectionStatusEntry(section_id=sec.id, status="ok"))
                    out = self._parse_stage2_response(raw, analysis_id)
                    for s in out:
                        key = (getattr(s.location, "section", None) or "", (s.title or "").strip())
                        if key not in seen_key and len(merged) < MAX_MERGED_SUGGESTIONS:
                            seen_key.add(key)
                            merged.append(s)
                    if progress_callback:
                        progress_callback("section_complete", {"section_id": sec.id, "suggestions_count": len(merged)})
                except FuturesTimeoutError:
                    logger.warning(f"Section '{sec.id}' timed out after {SECTION_TIMEOUT_SEC}s")
                    section_status_list.append(SectionStatusEntry(section_id=sec.id, status="timeout"))
                except Exception as e:
                    logger.warning(f"Section '{sec.id}' analysis failed: {e}")
                    section_status_list.append(SectionStatusEntry(section_id=sec.id, status="error"))

        return merged, section_status_list

    def _parse_stage2_response(self, raw: str, analysis_id: UUID) -> List[Suggestion]:
        """Parse Stage 2 LLM output into SectionSuggestionOutput and map to Suggestion list."""
        suggestions: List[Suggestion] = []
        try:
            data = json.loads(raw) if raw else {}
            out = SectionSuggestionOutput.model_validate(data)
            for item in out.suggestions:
                s = self._stage2_item_to_suggestion(item, analysis_id)
                if s:
                    suggestions.append(s)
        except Exception as e:
            logger.warning(f"Stage 2 parse failed: {e}")
        return suggestions

    def _stage2_item_to_suggestion(self, item, analysis_id: UUID) -> Suggestion | None:
        """Map SectionSuggestionItem to Suggestion (proposed→title, reason→explanation, section→location)."""
        try:
            title = (item.proposed or item.reason or "Suggestion").strip()[:200]
            explanation = (item.reason or "").strip()[:5000]
            if not explanation:
                explanation = item.proposed or title
            cat = SuggestionCategory.BEST_PRACTICES
            if getattr(item, "type", "").lower() == "add":
                cat = SuggestionCategory.COMPLETENESS
            elif getattr(item, "type", "").lower() == "fix":
                cat = SuggestionCategory.CLARITY
            conf = getattr(item, "confidence", 0.7) or 0.7
            prio = SuggestionPriority.HIGH if conf >= 0.8 else (SuggestionPriority.MEDIUM if conf >= 0.5 else SuggestionPriority.LOW)
            return Suggestion(
                analysis_id=analysis_id,
                category=cat,
                priority=prio,
                title=title,
                explanation=explanation,
                location=SuggestionLocation(section=item.section),
                example=item.proposed if item.proposed != title else None,
            )
        except Exception as e:
            logger.warning(f"Stage 2 item map failed: {e}")
            return None

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
