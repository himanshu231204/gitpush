"""OpenAI provider implementation."""

from __future__ import annotations

from typing import Any, Dict

import requests

from gitpush.ai.providers.base import BaseAIProvider
from gitpush.exceptions import AIGenerationError, AIProviderError


class OpenAIProvider(BaseAIProvider):
    """OpenAI-compatible chat completion provider."""

    def __init__(self, api_key: str, model: str, base_url: str, timeout: int = 30) -> None:
        super().__init__(model=model, timeout=timeout)
        self.api_key = api_key
        self.base_url = base_url

    def generate(self, prompt: str, max_tokens: int = 900, temperature: float = 0.2) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise AIProviderError(f"OpenAI request failed: {exc}") from exc

        text = _extract_openai_content(data)
        if not text:
            raise AIGenerationError("OpenAI response did not contain generated text")
        return text


def _extract_openai_content(data: Dict[str, Any]) -> str:
    """Extract generated content from OpenAI response."""

    choices = data.get("choices")
    if not choices:
        return ""

    first = choices[0]
    message = first.get("message", {})
    content = message.get("content", "")
    return str(content).strip()
