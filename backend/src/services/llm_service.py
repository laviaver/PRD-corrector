"""
LLM service for AI-powered PRD analysis.

Uses Groq only, via the OpenAI-compatible API (openai package + httpx for timeout).
"""

import json
import re

from openai import OpenAI as OpenAIClient
import httpx

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for LLM interactions using Groq."""

    def __init__(self):
        """Initialize Groq client. Requires GROQ_API_KEY."""
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "Groq API key required. Set GROQ_API_KEY in backend/.env"
            )
        timeout = httpx.Timeout(settings.LLM_TIMEOUT_SEC)
        http_client = httpx.Client(timeout=timeout)
        self.client = OpenAIClient(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            http_client=http_client,
        )
        logger.info("Initialized Groq provider")

    def analyze_prd(
        self, prd_content: str, system_prompt: str, max_tokens: int | None = None
    ) -> str:
        """
        Analyze PRD content using Groq.

        Args:
            prd_content: PRD text content
            system_prompt: System prompt for analysis
            max_tokens: Optional cap on output tokens (default from settings)

        Returns:
            Analysis response from LLM as JSON string
        """
        from src.services.prompts import PRD_ANALYSIS_USER_PROMPT_TEMPLATE

        user_prompt = PRD_ANALYSIS_USER_PROMPT_TEMPLATE.format(
            prd_content=prd_content
        )
        return self._analyze(system_prompt, user_prompt, max_tokens)

    def analyze_with_prompts(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> str:
        """
        Analyze using given system and user prompts (no template).
        Used for section analysis where the caller builds the user prompt.
        """
        return self._analyze(system_prompt, user_prompt, max_tokens)

    def _analyze(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> str:
        """Call Groq API and return normalized JSON response."""
        tokens = (
            max_tokens
            if max_tokens is not None
            else getattr(settings, "LLM_MAX_TOKENS", 2000)
        )
        try:
            response = self.client.chat.completions.create(
                model=getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=tokens,
                response_format={"type": "json_object"},
                timeout=settings.LLM_TIMEOUT_SEC,
            )
            analysis = response.choices[0].message.content
            logger.info(
                f"Groq analysis completed. Response length: {len(analysis) if analysis else 0}"
            )
            return self._normalize_json_response(analysis or "")
        except Exception as e:
            logger.error(f"Groq API call failed: {e}", exc_info=True)
            raise

    def _normalize_json_response(self, analysis: str) -> str:
        """
        Normalize LLM response to ensure it's valid JSON with suggestions array.
        """
        if not analysis:
            logger.warning("LLM returned empty response")
            return '{"suggestions": []}'

        try:
            parsed = json.loads(analysis)

            if isinstance(parsed, list):
                return json.dumps({"suggestions": parsed})
            if isinstance(parsed, dict) and "suggestions" in parsed:
                return json.dumps(parsed)
            if isinstance(parsed, dict) and len(parsed) > 0:
                if any(
                    key in parsed
                    for key in ["category", "priority", "title", "explanation"]
                ):
                    return json.dumps({"suggestions": [parsed]})
                return json.dumps({"suggestions": []})

            return json.dumps({"suggestions": []})

        except json.JSONDecodeError:
            logger.warning(f"LLM response is not valid JSON: {analysis[:200]}")
            json_match = re.search(r"\{.*\}", analysis, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    if isinstance(parsed, list):
                        return json.dumps({"suggestions": parsed})
                    if isinstance(parsed, dict) and "suggestions" in parsed:
                        return json.dumps(parsed)
                    if isinstance(parsed, dict):
                        return json.dumps({"suggestions": [parsed]})
                except json.JSONDecodeError:
                    pass

            return '{"suggestions": []}'


llm_service = LLMService()
