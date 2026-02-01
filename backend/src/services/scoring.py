"""
Stage 3 – Scoring.

Deterministic scores from structure (Stage 1) and suggestions (Stage 2).
No LLM. Signals: section presence, measurable metrics, owner.
"""

import re
from typing import List

from src.models.analysis import AnalysisScores
from src.models.suggestion import Suggestion
from src.services.structure_extractor import ExtractedSection

CANONICAL_STRUCTURE_IDS = frozenset({"problem", "goals", "non_goals", "metrics", "risks"})


def _base_section_id(section: ExtractedSection) -> str:
    """Canonical section id (e.g. metrics_0 -> metrics)."""
    if section.parent_section_id:
        return section.parent_section_id
    if "_" in section.id and section.id.split("_")[0] in CANONICAL_STRUCTURE_IDS:
        return section.id.split("_")[0]
    return section.id


def _structure_score(sections: List[ExtractedSection]) -> int:
    """+20 per canonical section type present (problem, goals, non_goals, metrics, risks), max 100."""
    if not sections:
        return 0
    present = {_base_section_id(s) for s in sections} & CANONICAL_STRUCTURE_IDS
    return min(100, 20 * len(present))


# Synonyms for "metrics in text" (graduated: 0 / 15 / 30 by strength)
_METRICS_PATTERNS = [
    re.compile(
        r"\b(metric|kpi|measurable|success\s+criteria|north\s+star|key\s+result)\w*\b",
        re.I,
    ),
    re.compile(
        r"\b(target|outcome|measure|indicator|okr|baseline|benchmark)\w*\b",
        re.I,
    ),
]
# Synonyms for "owner / responsible"
_OWNER_PATTERN = re.compile(
    r"\b(owner|owned\s+by|responsible|stakeholder|accountable|lead|champion|"
    r"contact|point\s+of\s+contact)\b",
    re.I,
)


def _completeness_score(sections: List[ExtractedSection]) -> int:
    """Signals: KPIs/metrics section +20, measurable metrics in text (graduated +15/+30), owner +10, max 100."""
    score = 0
    all_text = " ".join(s.text for s in sections).lower()
    base_ids = {_base_section_id(s) for s in sections}

    # KPIs / metrics section exists
    if "metrics" in base_ids:
        score += 20
    # Measurable metrics in text: graduated (0 / 15 / 30) by number of keyword groups found
    metrics_groups_found = sum(1 for pat in _METRICS_PATTERNS if pat.search(all_text))
    if metrics_groups_found >= 2:
        score += 30
    elif metrics_groups_found == 1:
        score += 15
    # Owner / responsible (synonyms)
    if _OWNER_PATTERN.search(all_text):
        score += 10

    return min(100, score)


def compute_scores(
    sections: List[ExtractedSection],
    suggestions: List[Suggestion],
) -> AnalysisScores:
    """
    Compute Stage 3 scores from structure and suggestions.

    Args:
        sections: Stage 1 extracted sections (with id, text, parent_section_id).
        suggestions: Stage 2 suggestions (used only for future signal expansion if needed).

    Returns:
        AnalysisScores (structure_score, completeness_score, total_score).
    """
    struct = _structure_score(sections)
    comp = _completeness_score(sections)
    total = round(0.4 * struct + 0.6 * comp)
    return AnalysisScores(
        structure_score=struct,
        completeness_score=comp,
        total_score=min(100, total),
    )
