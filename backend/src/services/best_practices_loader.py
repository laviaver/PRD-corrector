"""
Load local PRD best practices once; inject into prompts.
Update backend/src/data/prd_best_practices.md monthly.
"""

from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Path relative to backend src
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_BEST_PRACTICES_FILE = _DATA_DIR / "prd_best_practices.md"
_CACHE: str | None = None


def load_best_practices() -> str:
    """Load best practices text from disk; cached for process lifetime."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    path = _BEST_PRACTICES_FILE
    if not path.exists():
        logger.warning(f"Best practices file not found: {path}")
        return ""
    try:
        _CACHE = path.read_text(encoding="utf-8").strip()
        # Keep concise: first 1500 chars to avoid bloating prompt
        if len(_CACHE) > 1500:
            _CACHE = _CACHE[:1500] + "\n..."
        logger.info(f"Loaded best practices from {path} ({len(_CACHE)} chars)")
        return _CACHE
    except Exception as e:
        logger.warning(f"Failed to load best practices: {e}")
        return ""


def get_prd_analysis_system_prompt_base() -> str:
    """Return system prompt with best practices appended (for full-doc analysis)."""
    from src.services.prompts import PRD_ANALYSIS_SYSTEM_PROMPT
    bp = load_best_practices()
    if not bp:
        return PRD_ANALYSIS_SYSTEM_PROMPT
    return PRD_ANALYSIS_SYSTEM_PROMPT + "\n\nCompare against these criteria (local checklist):\n" + bp


def get_stage2_system_prompt_base() -> str:
    """Return Stage 2 system prompt with best practices appended."""
    from src.services.prompts import STAGE2_SECTION_SYSTEM_PROMPT
    bp = load_best_practices()
    if not bp:
        return STAGE2_SECTION_SYSTEM_PROMPT
    return STAGE2_SECTION_SYSTEM_PROMPT + "\n\nCompare section against (local checklist):\n" + bp
