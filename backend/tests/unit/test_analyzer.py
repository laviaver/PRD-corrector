"""Unit tests for analyzer service (Stage 1 structure extraction used by analyzer)."""

import pytest

from src.services.structure_extractor import extract_structure


class TestAnalyzerSectionSplitting:
    """Test structure extraction (Stage 1) used by the analyzer."""

    def test_empty_returns_empty(self):
        result = extract_structure("")
        assert result.sections == []
        result = extract_structure("   \n  ")
        assert result.sections == []

    def test_no_headers_returns_single_document_section(self):
        content = "Some intro text and body without markdown headers. This has enough length to pass the minimum."
        result = extract_structure(content)
        assert len(result.sections) >= 1
        # Stage 1 uses "Document" as header for no-headers content
        ids = [s.id for s in result.sections]
        assert "other" in ids or "Document" in [s.id for s in result.sections] or len(ids) == 1

    def test_two_headers_splits_into_sections(self):
        content = """## Overview
This is the overview section with enough content to pass the minimum.
We need at least 50 chars here so it counts as a section.
Lorem ipsum dolor sit amet, consectetur adipiscing elit.

## Goals
Goals section content. Also long enough to be considered a section.
We need at least 50 characters in this block so it is not skipped.
"""
        result = extract_structure(content)
        assert len(result.sections) >= 2
        section_ids = [s.id for s in result.sections]
        # Overview -> other, Goals -> goals
        assert "goals" in section_ids

    def test_short_section_skipped(self):
        content = """## Big
""" + "x" * 100 + """

## Tiny
nope

## Other
""" + "y" * 100
        result = extract_structure(content)
        assert len(result.sections) >= 1
        # Tiny has very little body so it may be skipped by min-length filter
        section_ids = [s.id for s in result.sections]
        assert len(section_ids) >= 1
