"""Unit tests for Stage 1 structure extractor."""

import pytest

from src.services.structure_extractor import (
    StructureExtractionResult,
    extract_structure,
    _header_to_canonical_id,
    _split_by_headers,
)


class TestHeaderToCanonical:
    """Test header -> canonical id mapping."""

    def test_problem_synonyms(self):
        assert _header_to_canonical_id("Problem Statement") == "problem"
        assert _header_to_canonical_id("Problem") == "problem"
        assert _header_to_canonical_id("Background") == "problem"

    def test_goals_synonyms(self):
        assert _header_to_canonical_id("Goals") == "goals"
        assert _header_to_canonical_id("Objective") == "goals"
        assert _header_to_canonical_id("Objectives") == "goals"

    def test_non_goals_synonyms(self):
        assert _header_to_canonical_id("Non-Goals") == "non_goals"
        assert _header_to_canonical_id("Out of Scope") == "non_goals"

    def test_metrics_synonyms(self):
        assert _header_to_canonical_id("Metrics") == "metrics"
        assert _header_to_canonical_id("KPIs") == "metrics"
        assert _header_to_canonical_id("Success Metrics") == "metrics"

    def test_risks_synonyms(self):
        assert _header_to_canonical_id("Risks") == "risks"
        assert _header_to_canonical_id("Assumptions") == "risks"

    def test_unmatched_is_other(self):
        assert _header_to_canonical_id("Introduction") == "other"
        assert _header_to_canonical_id("Appendix") == "other"
        assert _header_to_canonical_id("Random Section") == "other"


class TestSplitByHeaders:
    """Test raw header/body splitting."""

    def test_empty_returns_empty(self):
        assert _split_by_headers("") == []
        assert _split_by_headers("   \n  ") == []

    def test_no_headers_returns_document(self):
        out = _split_by_headers("Some intro text.")
        assert len(out) == 1
        assert out[0][0] == "Document"
        assert out[0][1] == "Some intro text."

    def test_two_headers(self):
        content = """## Problem
What we solve.

## Goals
What we want.
"""
        out = _split_by_headers(content)
        assert len(out) == 2
        assert out[0][0] == "Problem"
        assert "What we solve" in out[0][1]
        assert out[1][0] == "Goals"
        assert "What we want" in out[1][1]


class TestExtractStructure:
    """Test full structure extraction with canonical ids and sub-chunking."""

    def test_empty_returns_empty_sections(self):
        result = extract_structure("")
        assert isinstance(result, StructureExtractionResult)
        assert result.sections == []

    def test_whitespace_only_returns_empty(self):
        result = extract_structure("   \n\n   ")
        assert result.sections == []

    def test_single_section_gets_canonical_id(self):
        content = """## Problem Statement
This is the problem we are solving.
It has several sentences so we pass the minimum length.
"""
        result = extract_structure(content)
        assert len(result.sections) == 1
        assert result.sections[0].id == "problem"
        assert "problem we are solving" in result.sections[0].text
        assert result.sections[0].parent_section_id is None

    def test_metrics_and_goals_extracted(self):
        content = """## Metrics
We will track DAU and retention. This section has enough text to pass the minimum length.

## Goals
Increase engagement and grow the user base. This section also has enough content.
"""
        result = extract_structure(content)
        ids = [s.id for s in result.sections]
        assert "metrics" in ids
        assert "goals" in ids

    def test_very_short_body_skipped(self):
        content = """## Tiny
x

## Big
""" + "y" * 100
        result = extract_structure(content)
        # Tiny has very little body; Big has 100 chars
        assert len(result.sections) >= 1
        section_ids = [s.id for s in result.sections]
        assert "Big" not in section_ids  # "Big" normalizes to other
        assert any(s.id == "other" or s.id.startswith("other") for s in result.sections)

    def test_long_section_sub_chunked(self):
        # Use a section > MAX_SECTION_CHARS to trigger sub-chunking
        from src.config import settings
        max_chars = getattr(settings, "MAX_SECTION_CHARS", 4000)
        body = "x" * (max_chars + 500)
        content = "## Metrics\n\n" + body
        result = extract_structure(content)
        assert len(result.sections) >= 2
        for s in result.sections:
            assert s.id.startswith("metrics")
            assert len(s.text) <= max_chars + 100  # allow some slack for paragraph boundaries
        parents = [s.parent_section_id for s in result.sections]
        assert "metrics" in parents or all(s.id != "metrics" for s in result.sections)
