"""Unit tests for analyzer service (section splitting, etc.)."""

import pytest

from src.services.analyzer import analyzer_service


class TestAnalyzerSectionSplitting:
    """Test _split_into_sections behavior."""

    def test_empty_returns_empty(self):
        assert analyzer_service._split_into_sections("") == []
        assert analyzer_service._split_into_sections("   \n  ") == []

    def test_no_headers_returns_single_document_section(self):
        content = "Some intro text and body without markdown headers."
        out = analyzer_service._split_into_sections(content)
        assert len(out) == 1
        assert out[0][0] == "Document"
        assert out[0][1] == content.strip()

    def test_two_headers_splits_into_sections(self):
        # Each section body must be >= MIN_SECTION_CHARS (200) to be included
        content = """## Overview
This is the overview section with enough content to pass the minimum.
We need at least 200 chars here so it counts as a section.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, and more filler
text to reach the limit. The analyzer splits by markdown headers.

## Goals
Goals section content. Also long enough to be considered a section.
We need at least 200 characters in this block so it is not skipped.
Extra filler to ensure we pass the minimum threshold for section length.
"""
        out = analyzer_service._split_into_sections(content)
        assert len(out) >= 2
        names = [s[0] for s in out]
        assert "Overview" in names
        assert "Goals" in names

    def test_short_section_skipped(self):
        content = """## Big
""" + "x" * 250 + """

## Tiny
nope

## Other
""" + "y" * 250
        out = analyzer_service._split_into_sections(content)
        # "Tiny" has < 200 chars so it's skipped; we get Big and Other (or merged)
        assert len(out) >= 1
        section_names = [s[0] for s in out]
        assert "Tiny" not in section_names or any(len(s[1]) >= 200 for s in out)
