"""
LLM service for AI-powered PRD analysis.

This module supports multiple LLM providers:
- Ollama (free, local, no API key needed)
- Groq (free tier, very fast)
- OpenAI (paid)
- Hugging Face (free tier)
"""

import json
from typing import Optional

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Try to import providers (optional dependencies)
try:
    from openai import OpenAI as OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAIClient = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


class LLMService:
    """Service for LLM interactions with multiple provider support."""

    def __init__(self):
        """Initialize LLM service with configured provider."""
        self.provider = settings.LLM_PROVIDER.lower()
        self.client = None
        
        if self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "groq":
            self._init_groq()
        elif self.provider == "openai":
            self._init_openai()
        elif self.provider == "huggingface":
            self._init_huggingface()
        else:
            logger.warning(f"Unknown LLM provider: {self.provider}. Defaulting to Ollama.")
            self.provider = "ollama"
            self._init_ollama()

    def _init_ollama(self):
        """Initialize Ollama client (local, free, no API key needed)."""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for Ollama. Install with: pip install requests")
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        logger.info(f"Initialized Ollama provider with model: {self.model} at {self.base_url}")

    def _init_groq(self):
        """Initialize Groq client (free tier, very fast)."""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai library required for Groq. Install with: pip install openai")
        if not settings.GROQ_API_KEY:
            logger.warning("Groq API key not configured. Falling back to Ollama.")
            self.provider = "ollama"
            self._init_ollama()
            return
        # Groq uses OpenAI-compatible API
        self.client = OpenAIClient(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        logger.info("Initialized Groq provider")

    def _init_openai(self):
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai library required. Install with: pip install openai")
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured. Falling back to Ollama.")
            self.provider = "ollama"
            self._init_ollama()
            return
        self.client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
        logger.info("Initialized OpenAI provider")

    def _init_huggingface(self):
        """Initialize Hugging Face client."""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for Hugging Face. Install with: pip install requests")
        if not settings.HUGGINGFACE_API_KEY:
            logger.warning("Hugging Face API key not configured. Falling back to Ollama.")
            self.provider = "ollama"
            self._init_ollama()
            return
        self.api_key = settings.HUGGINGFACE_API_KEY
        logger.info("Initialized Hugging Face provider")

    def analyze_prd(self, prd_content: str, system_prompt: str) -> str:
        """
        Analyze PRD content using configured LLM provider.

        Args:
            prd_content: PRD text content
            system_prompt: System prompt for analysis

        Returns:
            Analysis response from LLM as JSON string

        Raises:
            ValueError: If provider is not configured
            Exception: If API call fails
        """
        # Use user prompt template for better structure
        from src.services.prompts import PRD_ANALYSIS_USER_PROMPT_TEMPLATE
        user_prompt = PRD_ANALYSIS_USER_PROMPT_TEMPLATE.format(prd_content=prd_content)

        if self.provider == "ollama":
            return self._analyze_with_ollama(system_prompt, user_prompt)
        elif self.provider == "groq":
            return self._analyze_with_groq(system_prompt, user_prompt)
        elif self.provider == "openai":
            return self._analyze_with_openai(system_prompt, user_prompt)
        elif self.provider == "huggingface":
            return self._analyze_with_huggingface(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _analyze_with_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Analyze using Ollama (local, free)."""
        try:
            # Normalize model name (remove :latest suffix if present, Ollama handles it)
            model_name = self.model.split(":")[0] if ":" in self.model else self.model
            
            # First, ensure model is available (this will trigger model load if needed)
            try:
                check_response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if check_response.status_code == 200:
                    models = check_response.json().get("models", [])
                    model_found = any(m.get("name", "").startswith(model_name) for m in models)
                    if not model_found:
                        logger.warning(f"Model {model_name} not found in Ollama. Available models: {[m.get('name') for m in models]}")
            except Exception as e:
                logger.warning(f"Could not check Ollama models: {e}")
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model_name,  # Use normalized name
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 4000,  # max tokens
                    },
                    "format": "json",  # Request JSON format
                },
                timeout=180,  # 3 minute timeout (first call can be slow as model loads)
            )
            response.raise_for_status()
            result = response.json()
            analysis = result.get("message", {}).get("content", "")
            
            if not analysis:
                logger.warning("Ollama returned empty response")
                return '{"suggestions": []}'
            
            logger.info(f"Ollama analysis completed. Response length: {len(analysis)}")
            return self._normalize_json_response(analysis)
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama request timed out: {e}")
            raise Exception("Ollama request timed out. The model might be loading. Please try again in a moment.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}", exc_info=True)
            # Provide more helpful error message
            if "Connection refused" in str(e) or "Failed to establish" in str(e):
                raise Exception("Cannot connect to Ollama. Make sure Ollama is running: 'ollama serve'")
            raise Exception(f"Ollama request failed: {e}")

    def _analyze_with_groq(self, system_prompt: str, user_prompt: str) -> str:
        """Analyze using Groq (free tier, very fast)."""
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # Free model on Groq
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )
            analysis = response.choices[0].message.content
            logger.info(f"Groq analysis completed. Response length: {len(analysis) if analysis else 0}")
            return self._normalize_json_response(analysis or "")
        except Exception as e:
            logger.error(f"Groq API call failed: {e}", exc_info=True)
            raise

    def _analyze_with_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Analyze using OpenAI."""
        try:
            # Try with JSON mode first (requires GPT-4-turbo or newer)
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=4000,
                    response_format={"type": "json_object"},
                )
            except Exception as e:
                # Fallback to regular GPT-4 if JSON mode not supported
                logger.warning(f"JSON mode not available, using standard mode: {e}")
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=4000,
                )
            analysis = response.choices[0].message.content
            logger.info(f"OpenAI analysis completed. Response length: {len(analysis) if analysis else 0}")
            return self._normalize_json_response(analysis or "")
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}", exc_info=True)
            raise

    def _analyze_with_huggingface(self, system_prompt: str, user_prompt: str) -> str:
        """Analyze using Hugging Face Inference API."""
        # Note: Hugging Face models vary, this is a basic implementation
        # You may need to adjust based on the specific model
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            # Using a good free model for text generation
            model_id = "mistralai/Mistral-7B-Instruct-v0.2"
            
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_id}",
                headers=headers,
                json={
                    "inputs": full_prompt,
                    "parameters": {
                        "temperature": 0.3,
                        "max_new_tokens": 4000,
                        "return_full_text": False,
                    },
                },
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
            
            # Hugging Face returns different formats depending on model
            if isinstance(result, list) and len(result) > 0:
                analysis = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                analysis = result.get("generated_text", "")
            else:
                analysis = str(result)
            
            logger.info(f"Hugging Face analysis completed. Response length: {len(analysis) if analysis else 0}")
            return self._normalize_json_response(analysis)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face API call failed: {e}", exc_info=True)
            raise Exception(f"Hugging Face request failed: {e}")

    def _normalize_json_response(self, analysis: str) -> str:
        """
        Normalize LLM response to ensure it's valid JSON with suggestions array.
        
        Args:
            analysis: Raw LLM response
            
        Returns:
            JSON string with {"suggestions": [...]} format
        """
        if not analysis:
            logger.warning("LLM returned empty response")
            return '{"suggestions": []}'
        
        # Try to parse as JSON
        try:
            parsed = json.loads(analysis)
            
            # If it's already an array, wrap it
            if isinstance(parsed, list):
                return json.dumps({"suggestions": parsed})
            
            # If it's an object with suggestions key, return as-is
            if isinstance(parsed, dict) and "suggestions" in parsed:
                return json.dumps(parsed)
            
            # If it's an object but not wrapped, check if it looks like a suggestion
            if isinstance(parsed, dict) and len(parsed) > 0:
                # Check if it has suggestion-like keys
                if any(key in parsed for key in ["category", "priority", "title", "explanation"]):
                    return json.dumps({"suggestions": [parsed]})
                # Otherwise, try to extract suggestions from the dict
                # Some models might return {"suggestions": [...]} but we already checked
                return json.dumps({"suggestions": []})
            
            return json.dumps({"suggestions": []})
            
        except json.JSONDecodeError:
            logger.warning(f"LLM response is not valid JSON: {analysis[:200]}")
            # Try to extract JSON from text if it's wrapped in markdown or text
            import re
            json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
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
            
            # Return empty suggestions if JSON parsing fails
            return '{"suggestions": []}'


# Global service instance
llm_service = LLMService()
