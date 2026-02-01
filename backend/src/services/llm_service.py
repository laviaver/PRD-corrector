"""
LLM service for AI-powered PRD analysis.

Supports Groq (cloud, TPM limits) and Ollama (local, no truncation).
Uses OpenAI-compatible API (openai package + httpx for timeout).
"""

import json
import re

from openai import OpenAI as OpenAIClient
import httpx

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Cap PRD content for Groq so a single request stays under on_demand TPM (6000 tokens/min).
# Not used when LLM_PROVIDER=ollama (full context sent).
MAX_PRD_INPUT_CHARS_GROQ = 12_000


class LLMService:
    """Service for LLM interactions (Groq or Ollama)."""

    def __init__(self):
        """Initialize client from LLM_PROVIDER (groq or ollama)."""
        self.provider = getattr(settings, "LLM_PROVIDER", "groq").lower()
        timeout = httpx.Timeout(settings.LLM_TIMEOUT_SEC)
        http_client = httpx.Client(timeout=timeout)

        if self.provider == "ollama":
            base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
            # Ollama OpenAI-compatible endpoint
            if not base_url.endswith("/v1"):
                base_url = f"{base_url}/v1"
            self.client = OpenAIClient(
                api_key="ollama",
                base_url=base_url,
                http_client=http_client,
            )
            self.model = getattr(settings, "OLLAMA_MODEL", "llama3.2")
            logger.info("Initialized Ollama provider (full PRD context, no truncation)")
        else:
            if not settings.GROQ_API_KEY:
                raise ValueError(
                    "Groq API key required. Set GROQ_API_KEY in backend/.env (or use LLM_PROVIDER=ollama)"
                )
            self.client = OpenAIClient(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
                http_client=http_client,
            )
            self.model = getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant")
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

        # Only truncate for Groq (TPM/context limits). Ollama gets full PRD context.
        if self.provider == "groq" and len(prd_content) > MAX_PRD_INPUT_CHARS_GROQ:
            prd_content = (
                prd_content[:MAX_PRD_INPUT_CHARS_GROQ]
                + "\n\n[... document truncated for analysis ...]"
            )
            logger.info(
                "PRD content truncated to %s chars for Groq TPM limit",
                MAX_PRD_INPUT_CHARS_GROQ,
            )

        user_prompt = PRD_ANALYSIS_USER_PROMPT_TEMPLATE.format(
            prd_content=prd_content
        )
        # #region agent log
        try:
            with open("/Users/lavia/PRD-corrector/.cursor/debug.log", "a") as _f:
                _f.write(json.dumps({"location": "llm_service.py:analyze_prd", "message": "analyze_prd entry", "data": {"prd_content_len": len(prd_content), "system_prompt_len": len(system_prompt), "user_prompt_len": len(user_prompt), "runId": "post-fix"}, "timestamp": __import__("time").time() * 1000, "sessionId": "debug-session", "hypothesisId": "A"}) + "\n")
        except Exception:
            pass
        # #endregion
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
        # #region agent log
        total_chars = len(system_prompt) + len(user_prompt)
        try:
            with open("/Users/lavia/PRD-corrector/.cursor/debug.log", "a") as _f:
                _f.write(json.dumps({"location": "llm_service.py:_analyze", "message": "before API call", "data": {"total_input_chars": total_chars, "max_tokens": tokens}, "timestamp": __import__("time").time() * 1000, "sessionId": "debug-session", "hypothesisId": "B"}) + "\n")
        except Exception:
            pass
        # #endregion
        try:
            response = self.client.chat.completions.create(
                model=self.model,
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
            # #region agent log
            err_str = str(e)
            try:
                with open("/Users/lavia/PRD-corrector/.cursor/debug.log", "a") as _f:
                    _f.write(json.dumps({"location": "llm_service.py:_analyze", "message": "API call failed", "data": {"error": err_str[:500], "total_input_chars": total_chars, "max_tokens": tokens}, "timestamp": __import__("time").time() * 1000, "sessionId": "debug-session", "hypothesisId": "E"}) + "\n")
            except Exception:
                pass
            # #endregion
            logger.error(f"Groq API call failed: {e}", exc_info=True)
            raise

    def score_prd(self, prd_content: str, sections_summary: str) -> dict | None:
        """
        Optional LLM-based scoring: return structure_score and completeness_score (0-100)
        with brief reasoning. Returns None on parse failure or API error (caller should fall back to rules).
        """
        from src.services.prompts import PRD_SCORING_SYSTEM_PROMPT, PRD_SCORING_USER_TEMPLATE

        content_snippet = (prd_content[:8000] + "...") if len(prd_content) > 8000 else prd_content
        # #region agent log
        try:
            with open("/Users/lavia/PRD-corrector/.cursor/debug.log", "a") as _f:
                _f.write(json.dumps({"location": "llm_service.py:score_prd", "message": "score_prd entry", "data": {"prd_content_len": len(prd_content), "snippet_len": len(content_snippet)}, "timestamp": __import__("time").time() * 1000, "sessionId": "debug-session", "hypothesisId": "D"}) + "\n")
        except Exception:
            pass
        # #endregion
        user_prompt = PRD_SCORING_USER_TEMPLATE.format(
            prd_content=content_snippet,
            sections_summary=sections_summary or "(none)",
        )
        try:
            raw = self._analyze(PRD_SCORING_SYSTEM_PROMPT, user_prompt, max_tokens=300)
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                return None
            struct = parsed.get("structure_score")
            comp = parsed.get("completeness_score")
            if struct is None or comp is None:
                return None
            struct = max(0, min(100, int(struct))) if isinstance(struct, (int, float)) else None
            comp = max(0, min(100, int(comp))) if isinstance(comp, (int, float)) else None
            if struct is None or comp is None:
                return None
            return {
                "structure_score": struct,
                "completeness_score": comp,
                "structure_reason": parsed.get("structure_reason", ""),
                "completeness_reason": parsed.get("completeness_reason", ""),
            }
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.warning(f"LLM scoring parse failed: {e}")
            return None
        except Exception as e:
            logger.warning(f"LLM scoring failed: {e}", exc_info=True)
            return None

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
