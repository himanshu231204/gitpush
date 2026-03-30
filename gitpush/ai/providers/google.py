"""Google (Gemini) AI provider."""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional

from gitpush.ai.providers.base import BaseAIProvider

# Configure logging
logger = logging.getLogger(__name__)


# Error code mapping for user-friendly messages
GOOGLE_ERROR_CODES = {
    400: "Bad request - check model name and parameters",
    401: "Invalid API key - please check your Google API key",
    403: "Access denied - insufficient permissions or rate limited",
    404: "Model not found - the model may not exist or not be available",
    429: "Rate limited - too many requests, please wait",
    500: "Google server error - try again later",
    502: "Bad gateway - service temporarily unavailable",
    503: "Service unavailable - try again later",
}


class GoogleProvider(BaseAIProvider):
    """Google Gemini AI provider."""

    # Fallback models in order of preference (v1 API - verified working)
    FALLBACK_MODELS = [
        "gemini-2.0-flash-exp",  # Latest experimental
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-pro",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8k",
        "gemini-1.5-pro",
    ]

    def __init__(self, api_key: str, model: str, base_url: str, timeout: int = 30):
        super().__init__(model, timeout)
        self.api_key = api_key
        self._original_base_url = base_url

    def _get_formatted_url(self, model: str) -> str:
        """Get URL with model substituted."""
        return f"{self._original_base_url.format(model=model)}?key={self.api_key}"

    def generate(self, prompt: str, max_tokens: int = 900, temperature: float = 0.2) -> str:
        """Generate text from a prompt using Google Gemini API with fallback."""
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required for Google provider")

        # Try models in order of preference
        models_to_try = self._get_models_to_try()

        last_error = None
        for model in models_to_try:
            try:
                logger.debug(f"Trying Google model: {model}")
                return self._generate_with_model(prompt, model, max_tokens, temperature)
            except RuntimeError as e:
                error_str = str(e)
                last_error = e

                # Check if this error is retryable
                if any(code in error_str for code in ["429", "500", "502", "503"]):
                    logger.debug(f"Model {model} failed with retryable error, trying next...")
                    continue
                # For model not found, try next model
                elif "404" in error_str or "Model not found" in error_str:
                    logger.debug(f"Model {model} not found, trying next...")
                    continue
                else:
                    logger.debug(f"Model {model} failed: {error_str[:50]}...")
                    continue

        # All models failed
        error_hint = self._get_error_hint(str(last_error))
        raise RuntimeError(f"All Google models failed. Last error: {last_error}\n{error_hint}")

    def _generate_with_model(
        self, prompt: str, model: str, max_tokens: int, temperature: float
    ) -> str:
        """Generate text with a specific model."""
        url = self._get_formatted_url(model)
        logger.debug(f"Google Provider - Model: {model}, URL: {url[:60]}...")

        # Prepare request data for Gemini API
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
                "topK": 10,
            },
        }

        headers = {"Content-Type": "application/json"}

        req = urllib.request.Request(
            url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

                # Extract text from Gemini response
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            return parts[0]["text"].strip()

                # Fallback if response format is unexpected
                return str(result)

        except urllib.error.HTTPError as e:
            # Read error body once - HTTPError.read() can only be called once
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                error_body = str(e)

            logger.debug(f"Google API error response: {error_body}")

            # Get user-friendly error message
            error_msg = GOOGLE_ERROR_CODES.get(e.code, f"HTTP {e.code}")
            raise RuntimeError(f"Google API error ({e.code}): {error_msg}")

        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Google API: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in Google provider: {str(e)}")

    def _get_models_to_try(self) -> list:
        """Get list of models to try."""
        models = []

        # Add original model first
        if self.model not in self.FALLBACK_MODELS:
            models.append(self.model)

        # Add fallback models
        for fallback_model in self.FALLBACK_MODELS:
            if fallback_model not in models:
                models.append(fallback_model)

        return models

    def _get_error_hint(self, error_str: str) -> str:
        """Get helpful hint based on error."""
        if "401" in error_str or "Invalid API key" in error_str:
            return "Hint: Your Google API key may be invalid. Get one from https://aistudio.google.com/app/apikey"
        elif "404" in error_str:
            return (
                "Hint: The model may not be available. Try a different model in Configure Provider."
            )
        else:
            return "Hint: Check your Google Cloud console at https://console.cloud.google.com for status and quota."
