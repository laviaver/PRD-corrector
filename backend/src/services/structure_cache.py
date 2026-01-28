"""
Decision-level cache: structure extraction by content hash.
Latency rule: Cache schema/structure outcomes; do not cache raw LLM text.
"""

from typing import Optional

from src.services.structure_extractor import StructureExtractionResult, extract_structure
from src.utils.logger import get_logger

logger = get_logger(__name__)

_MAX_ENTRIES = 1000
_cache: dict[int, StructureExtractionResult] = {}
_cache_order: list[int] = []


def get_structure_cached(content: str) -> StructureExtractionResult:
    """
    Return structure extraction for content; use cache keyed by hash to avoid re-extraction.
    Enforces: cache intent/schema outcomes, not raw LLM.
    """
    key = hash(content)
    if key in _cache:
        return _cache[key]
    result = extract_structure(content)
    if len(_cache) >= _MAX_ENTRIES:
        evict = _cache_order.pop(0)
        _cache.pop(evict, None)
    _cache[key] = result
    _cache_order.append(key)
    return result
