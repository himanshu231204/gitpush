"""Local model provider (Ollama-compatible)."""

from __future__ import annotations

from typing import Any, Dict

import requests

from gitpush.ai.providers.base import BaseAIProvider
from gitpush.exceptions import AIGenerationError, AIProviderError


class LocalAIProvider(BaseAIProvider):
    """Local model endpoint provider for on-device AI."""

    def __init__(self, model: str, base_url: str, timeout: int = 30) -> None:
        super().__init__(model=model, timeout=timeout)
        self.base_url = base_url

    def generate(self, prompt: str, max_tokens: int = 900, temperature: float = 0.2) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise AIProviderError(f"Local model request failed: {exc}") from exc

        text = _extract_local_content(data)
        if not text:
            raise AIGenerationError("Local model response did not contain generated text")
        return text


def _extract_local_content(data: Dict[str, Any]) -> str:
    """Extract generated content from local response."""

    response = data.get("response", "")
    return str(response).strip()
