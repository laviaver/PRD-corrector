"""
Prompt engineering for PRD analysis.

This module contains system prompts and prompt templates for LLM analysis.
"""

PRD_ANALYSIS_SYSTEM_PROMPT = """You are a PRD reviewer.

Review the PRD and return 3–5 concrete improvement suggestions.

Return ONLY a valid JSON array. No extra text.

Format:
[
  {
    "category": "structure|clarity|completeness|best_practices|technical_quality",
    "priority": "high|medium|low",
    "title": "Short issue summary",
    "explanation": "What's wrong and why",
    "location": "Section (optional)",
    "example": "Fix example (optional)",
    "template": "Template snippet (optional)"
  }
]

Check for: missing core sections, ambiguity, weak structure, missing acceptance criteria, vague technical detail.

Always return 3–5 items."""

PRD_ANALYSIS_USER_PROMPT_TEMPLATE = """Analyze this PRD and provide 3-5 improvement suggestions as JSON array.

PRD:
{prd_content}

Check for missing sections, unclear language, incomplete info. Return ONLY JSON array with suggestions."""

# Shorter prompt for per-section parallel analysis (suggestion 5)
PRD_SECTION_SYSTEM_PROMPT = """You are a PRD reviewer. Analyze this PRD section and return 0-3 improvement suggestions.

CRITICAL: Return ONLY valid JSON: {"suggestions": [{"category":"...","priority":"high|medium|low","title":"...","explanation":"...","location":"Section name"}]}
Use category: structure|clarity|completeness|best_practices|technical_quality. If no issues, return {"suggestions":[]}."""

PRD_SECTION_USER_TEMPLATE = """Section "{section_name}":
{section_content}

Return 0-3 suggestions as JSON {"suggestions": [...]}. No other text."""

# Stage 2 – Section-level review (hard schema, short prompts)
STAGE2_SECTION_SYSTEM_PROMPT = """You are a PRD reviewer. Return ONLY valid JSON of this shape, no other text:

{"suggestions": [{"id": "SUG-001", "section": "<section_id>", "type": "add|improve|fix", "original": "", "proposed": "text", "reason": "why", "confidence": 0.0-1.0}]}

Rules: id like SUG-NNN, section = section id given, type add|improve|fix. If no issues return {"suggestions":[]}."""

STAGE2_SECTION_USER_TEMPLATE = """Section id: {section_id}
{section_content}

Return 0-3 suggestions as JSON with id, section, type, original, proposed, reason, confidence. No other text."""

# Optional LLM-based scoring (context and meaning)
PRD_SCORING_SYSTEM_PROMPT = """You are a PRD reviewer. Score this PRD on structure and completeness (0-100 each).

Consider context and meaning: partial fulfillment (e.g. goals implied in intro) should get partial credit. Use synonyms (e.g. overview = problem, key results = metrics).

Return ONLY valid JSON with this exact shape, no other text:
{"structure_score": <0-100>, "completeness_score": <0-100>, "structure_reason": "<one line>", "completeness_reason": "<one line>"}"""

PRD_SCORING_USER_TEMPLATE = """PRD content (first 8000 chars):
{prd_content}

Sections detected: {sections_summary}

Return JSON: structure_score (0-100), completeness_score (0-100), structure_reason, completeness_reason."""
