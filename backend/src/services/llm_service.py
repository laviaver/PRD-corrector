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
            # Use user prompt template for better structure
            from src.services.prompts import PRD_ANALYSIS_USER_PROMPT_TEMPLATE
            user_prompt = PRD_ANALYSIS_USER_PROMPT_TEMPLATE.format(prd_content=prd_content)
            
            # Try with JSON mode first (requires GPT-4-turbo or newer)
            try:
                response: ChatCompletion = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",  # Use turbo for JSON mode support
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,  # Lower temperature for more consistent, focused responses
                    max_tokens=4000,  # Increased for longer PRDs and more suggestions
                    response_format={"type": "json_object"},  # Force JSON output
                )
            except Exception as e:
                # Fallback to regular GPT-4 if JSON mode not supported
                logger.warning(f"JSON mode not available, using standard mode: {e}")
                response: ChatCompletion = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=4000,
                )

            analysis = response.choices[0].message.content
            logger.info(f"LLM analysis completed successfully. Response length: {len(analysis) if analysis else 0}")
            
            if not analysis:
                logger.warning("LLM returned empty response")
                return '{"suggestions": []}'
            
            # If response_format is json_object, wrap in suggestions key if needed
            try:
                import json
                parsed = json.loads(analysis)
                # If it's already an array, wrap it
                if isinstance(parsed, list):
                    analysis = json.dumps({"suggestions": parsed})
                # If it's an object but not wrapped, check if it has suggestions
                elif isinstance(parsed, dict) and "suggestions" not in parsed and len(parsed) > 0:
                    # Assume it's a single suggestion, wrap it
                    analysis = json.dumps({"suggestions": [parsed]})
            except json.JSONDecodeError:
                logger.warning(f"LLM response is not valid JSON: {analysis[:200]}")
                # Return empty suggestions if JSON parsing fails
                return '{"suggestions": []}'
            
            return analysis

        except Exception as e:
            logger.error(f"LLM API call failed: {e}", exc_info=True)
            raise


# Global service instance
llm_service = LLMService()
