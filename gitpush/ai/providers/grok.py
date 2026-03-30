"""Grok (xAI) AI provider."""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional

from gitpush.ai.providers.base import BaseAIProvider

# Configure logging
logger = logging.getLogger(__name__)


# Error code mapping for user-friendly messages
GROK_ERROR_CODES = {
    400: "Bad request - check model name and parameters",
    401: "Invalid API key - please check your Grok API key",
    403: "Access denied - insufficient permissions or rate limited (error 1010)",
    404: "Model not found - try a different model",
    408: "Request timeout - try again later",
    429: "Rate limited - too many requests, please wait",
    500: "Grok server error - try again later",
    502: "Bad gateway - service temporarily unavailable",
    503: "Service unavailable - try again later",
    1010: "Account usage limit exceeded or rate limited - check your xAI account",
}


class GrokProvider(BaseAIProvider):
    """Grok (xAI) AI provider."""

    # Fallback models in order of preference (verified working)
    FALLBACK_MODELS = ["grok-2", "grok-2-mini", "grok-2-1212", "grok-2-preview", "grok-beta"]

    def __init__(self, api_key: str, model: str, base_url: str, timeout: int = 30):
        super().__init__(model, timeout)
        self.api_key = api_key
        self.base_url = base_url
        self._original_model = model

    def generate(self, prompt: str, max_tokens: int = 900, temperature: float = 0.2) -> str:
        """Generate text from a prompt using Grok API with automatic fallback."""
        if not self.api_key:
            raise ValueError("GROK_API_KEY is required for Grok provider")

        # Try models in order of preference
        models_to_try = self._get_models_to_try()

        last_error = None
        for model in models_to_try:
            try:
                logger.debug(f"Trying Grok model: {model}")
                return self._generate_with_model(prompt, model, max_tokens, temperature)
            except RuntimeError as e:
                error_str = str(e)
                last_error = e

                # Check if this error is retryable (rate limit, server error)
                if any(code in error_str for code in ["1010", "429", "500", "502", "503"]):
                    logger.debug(f"Model {model} failed with retryable error, trying next...")
                    continue
                # For non-retryable errors, don't try other models
                elif "404" in error_str or "Model not found" in error_str:
                    logger.debug(f"Model {model} not found, trying next...")
                    continue
                else:
                    # Other errors - try next model anyway
                    logger.debug(f"Model {model} failed: {error_str[:50]}...")
                    continue

        # All models failed
        error_hint = self._get_error_hint(str(last_error))
        raise RuntimeError(f"All Grok models failed. Last error: {last_error}\n" f"{error_hint}")

    def _generate_with_model(
        self, prompt: str, model: str, max_tokens: int, temperature: float
    ) -> str:
        """Generate text with a specific model."""
        logger.debug(f"Grok Provider - Model: {model}, Base URL: {self.base_url}")

        # Prepare request data for Grok API (OpenAI-compatible)
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        # Prepare request
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

        req = urllib.request.Request(
            self.base_url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

                # Extract text from Grok response (OpenAI-compatible format)
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    if "content" in message:
                        return message["content"].strip()

                # Fallback if response format is unexpected
                return str(result)

        except urllib.error.HTTPError as e:
            # Read error body once - HTTPError.read() can only be called once
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                error_body = str(e)

            logger.debug(f"Grok API error response: {error_body}")

            # Try to extract error code from response
            error_code = e.code
            try:
                error_json = json.loads(error_body)
                if isinstance(error_json, dict):
                    error_code = error_json.get("error", {}).get("code", e.code)
            except (json.JSONDecodeError, ValueError, Exception):
                # If error_body is not JSON, use HTTP status code as fallback
                pass

            # Get user-friendly error message
            error_msg = GROK_ERROR_CODES.get(error_code, f"HTTP {error_code}")
            if error_code == 1010:
                error_msg = "Account usage limit exceeded or rate limited (error 1010). Check your xAI account at https://console.x.ai"

            raise RuntimeError(f"Grok API error ({error_code}): {error_msg}")

        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Grok API: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in Grok provider: {str(e)}")

    def _get_models_to_try(self) -> list:
        """Get list of models to try, including fallback models."""
        models = []

        # Add original model first if not already in fallback list
        if self.model not in self.FALLBACK_MODELS:
            models.append(self.model)

        # Add fallback models
        for fallback_model in self.FALLBACK_MODELS:
            if fallback_model not in models:
                models.append(fallback_model)

        return models

    def _get_error_hint(self, error_str: str) -> str:
        """Get helpful hint based on error."""
        if "1010" in error_str:
            return (
                "Hint: Your Grok account may have exceeded usage limits. "
                "Visit https://console.x.ai to check your account status and quota."
            )
        elif "401" in error_str:
            return (
                "Hint: Your API key may be invalid. "
                "Make sure you have a valid Grok API key from https://console.x.ai"
            )
        elif "404" in error_str:
            return (
                "Hint: The model may not be available. "
                "Try updating to a different model in Configure Provider."
            )
        else:
            return "Hint: Check your Grok account at https://console.x.ai for status and quota."
