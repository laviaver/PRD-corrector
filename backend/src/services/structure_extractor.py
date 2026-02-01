"""
Stage 1 – Structure extraction.

Deterministic, rule-based extraction of PRD sections with canonical ids.
No LLM. Splits by markdown headers, maps header text to canonical ids,
and sub-chunks sections larger than MAX_SECTION_CHARS.
"""

import re
from typing import List, Optional

from pydantic import BaseModel, Field

from src.config import settings

# Canonical section ids
CANONICAL_IDS = frozenset({"problem", "goals", "non_goals", "metrics", "risks", "other"})

# Header text (case-insensitive, normalized) -> canonical id
# Order matters: more specific patterns first when we do substring/startswith
# Order matters: more specific (e.g. non-goals) must appear before generic (goals)
HEADER_TO_CANONICAL: List[tuple] = [
    # problem
    ("problem statement", "problem"),
    ("executive summary", "problem"),
    ("overview", "problem"),
    ("background", "problem"),
    ("context", "problem"),
    ("opportunity", "problem"),
    ("current state", "problem"),
    ("problem", "problem"),
    # non_goals (before goals so "non-goals" doesn't match "goals")
    ("non-goals", "non_goals"),
    ("non goals", "non_goals"),
    ("out of scope", "non_goals"),
    ("scope exclusions", "non_goals"),
    ("exclusions", "non_goals"),
    ("non-objectives", "non_goals"),
    # goals
    ("goals", "goals"),
    ("objectives", "goals"),
    ("objective", "goals"),
    ("aims", "goals"),
    ("targets", "goals"),
    ("outcomes", "goals"),
    ("vision", "goals"),
    ("purpose", "goals"),
    # metrics
    ("success metrics", "metrics"),
    ("key results", "metrics"),
    ("key performance indicators", "metrics"),
    ("success criteria", "metrics"),
    ("measurements", "metrics"),
    ("okrs", "metrics"),
    ("north star", "metrics"),
    ("metrics", "metrics"),
    ("kpis", "metrics"),
    # risks
    ("risks", "risks"),
    ("assumptions", "risks"),
    ("dependencies", "risks"),
    ("constraints", "risks"),
    ("limitations", "risks"),
    ("open questions", "risks"),
]


def _normalize_header(header: str) -> str:
    """Normalize header for lookup: strip, lower, collapse spaces, strip punctuation."""
    s = " ".join(header.lower().strip().split())
    # Strip trailing/leading punctuation so "Success Metrics:" still matches
    return s.strip(".:;,")


def _header_to_canonical_id(header: str) -> str:
    """Map header text to canonical id. Unmatched -> 'other'."""
    normalized = _normalize_header(header)
    if not normalized:
        return "other"
    for pattern, cid in HEADER_TO_CANONICAL:
        if pattern in normalized or normalized.startswith(pattern):
            return cid
    return "other"


class ExtractedSection(BaseModel):
    """A single extracted section with canonical id and optional parent."""

    id: str = Field(..., description="Canonical section id or sub-chunk id (e.g. metrics_0)")
    text: str = Field(..., description="Section body text")
    parent_section_id: Optional[str] = Field(None, description="Parent section id when sub-chunked")


class StructureExtractionResult(BaseModel):
    """Result of Stage 1 structure extraction."""

    sections: List[ExtractedSection] = Field(default_factory=list, description="Extracted sections")


def _split_by_headers(content: str) -> List[tuple[str, str]]:
    """Split content into (header_text, body) by markdown # / ## / ### headers."""
    if not content or not content.strip():
        return []
    lines = content.strip().splitlines()
    sections: List[tuple[str, str]] = []
    current_header = "Document"
    current_buf: List[str] = []

    for line in lines:
        m = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if m:
            body = "\n".join(current_buf).strip()
            if body:
                sections.append((current_header, body))
            current_header = m.group(2).strip()
            current_buf = []
        else:
            current_buf.append(line)

    body = "\n".join(current_buf).strip()
    if body or current_header != "Document":
        sections.append((current_header, body))
    if not sections and content.strip():
        return [("Document", content.strip())]
    return sections


def _sub_chunk_section(section_id: str, text: str, max_chars: int) -> List[ExtractedSection]:
    """Split a section into chunks of at most max_chars; ids are section_id_0, section_id_1, ..."""
    if len(text) <= max_chars:
        return [ExtractedSection(id=section_id, text=text, parent_section_id=None)]
    out: List[ExtractedSection] = []
    # Split by paragraph (double newline) when possible, else by size
    parts = re.split(r"\n\s*\n", text)
    chunk_buf: List[str] = []
    chunk_len = 0
    idx = 0
    for i, part in enumerate(parts):
        part_len = len(part) + 2  # +2 for "\n\n"
        if chunk_len + part_len > max_chars and chunk_buf:
            chunk_text = "\n\n".join(chunk_buf)
            out.append(
                ExtractedSection(
                    id=f"{section_id}_{idx}",
                    text=chunk_text,
                    parent_section_id=section_id,
                )
            )
            idx += 1
            chunk_buf = []
            chunk_len = 0
        if len(part) > max_chars:
            # Single paragraph too long: split by size with overlap
            start = 0
            while start < len(part):
                end = min(start + max_chars, len(part))
                slice_text = part[start:end]
                out.append(
                    ExtractedSection(
                        id=f"{section_id}_{idx}",
                        text=slice_text,
                        parent_section_id=section_id,
                    )
                )
                idx += 1
                start = end
            continue
        chunk_buf.append(part)
        chunk_len += part_len
    if chunk_buf:
        chunk_text = "\n\n".join(chunk_buf)
        out.append(
            ExtractedSection(
                id=f"{section_id}_{idx}",
                text=chunk_text,
                parent_section_id=section_id,
            )
        )
    return out


def extract_structure(content: str) -> StructureExtractionResult:
    """
    Extract PRD structure with canonical section ids (Stage 1).

    - Splits by markdown # / ## / ### headers.
    - Maps each header to canonical id: problem | goals | non_goals | metrics | risks | other.
    - If a section body exceeds MAX_SECTION_CHARS, sub-chunks it with parent_section_id.

    Args:
        content: Full PRD text.

    Returns:
        StructureExtractionResult with sections list.
    """
    max_chars = getattr(settings, "MAX_SECTION_CHARS", 4000)
    raw = _split_by_headers(content)
    sections: List[ExtractedSection] = []
    seen_ids: set[str] = set()

    for header_text, body in raw:
        if not body or len(body.strip()) < 50:
            continue
        base_id = _header_to_canonical_id(header_text)
        # Avoid id collision when many sections map to same canonical id
        candidate = base_id
        suffix = 0
        while candidate in seen_ids:
            suffix += 1
            candidate = f"{base_id}_{suffix}" if base_id != "other" else f"other_{suffix}"
        seen_ids.add(candidate)
        for sec in _sub_chunk_section(candidate, body, max_chars):
            sections.append(sec)

    return StructureExtractionResult(sections=sections)
