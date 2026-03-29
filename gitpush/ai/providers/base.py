"""Base interface for all AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """Provider contract for text generation."""

    def __init__(self, model: str, timeout: int = 30) -> None:
        self.model = model
        self.timeout = timeout

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 900, temperature: float = 0.2) -> str:
        """Generate text from a prompt."""
