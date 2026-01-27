"""
LLM service for AI-powered PRD analysis.

This module integrates with OpenAI GPT-4 API to analyze PRD content.
"""

from typing import List, Dict, Any

from openai import OpenAI
from openai.types.chat import ChatCompletion

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for LLM interactions."""

    def __init__(self):
        """Initialize LLM service with API client."""
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def analyze_prd(self, prd_content: str, system_prompt: str) -> str:
        """
        Analyze PRD content using LLM.

        Args:
            prd_content: PRD text content
            system_prompt: System prompt for analysis

        Returns:
            Analysis response from LLM

        Raises:
            ValueError: If API key is not configured
            Exception: If API call fails
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        try:
            response: ChatCompletion = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prd_content},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            analysis = response.choices[0].message.content
            logger.info("LLM analysis completed successfully")
            return analysis or ""

        except Exception as e:
            logger.error(f"LLM API call failed: {e}", exc_info=True)
            raise


# Global service instance
llm_service = LLMService()
