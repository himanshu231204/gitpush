"""Anthropic provider implementation."""

from __future__ import annotations

from typing import Any, Dict, List

import requests

from gitpush.ai.providers.base import BaseAIProvider
from gitpush.exceptions import AIGenerationError, AIProviderError


class AnthropicProvider(BaseAIProvider):
    """Anthropic messages API provider."""

    def __init__(self, api_key: str, model: str, base_url: str, timeout: int = 30) -> None:
        super().__init__(model=model, timeout=timeout)
        self.api_key = api_key
        self.base_url = base_url

    def generate(self, prompt: str, max_tokens: int = 900, temperature: float = 0.2) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
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
            raise AIProviderError(f"Anthropic request failed: {exc}") from exc

        text = _extract_anthropic_content(data)
        if not text:
            raise AIGenerationError("Anthropic response did not contain generated text")
        return text


def _extract_anthropic_content(data: Dict[str, Any]) -> str:
    """Extract generated content from Anthropic response."""

    content_blocks: List[Dict[str, Any]] = data.get("content", [])
    fragments = []
    for block in content_blocks:
        if block.get("type") == "text":
            fragments.append(str(block.get("text", "")))
    return "\n".join(part for part in fragments if part).strip()
