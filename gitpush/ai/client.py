"""Unified client for prompt + provider execution."""

from __future__ import annotations

from typing import List, Optional

from gitpush.ai.config import AIConfig
from gitpush.ai.factory import AIProviderFactory
from gitpush.ai.prompts.commit_prompt import build_commit_prompt
from gitpush.ai.prompts.pr_prompt import build_pr_prompt
from gitpush.ai.prompts.review_prompt import build_review_prompt
from gitpush.ai.providers.base import BaseAIProvider


class AIClient:
    """Provider-agnostic AI client."""

    def __init__(self, provider: Optional[BaseAIProvider] = None, config: Optional[AIConfig] = None):
        self.config = config or AIConfig.from_env()
        self.provider = provider or AIProviderFactory.create(self.config)

    def generate_commit_message(self, cleaned_diff: str) -> str:
        """Generate commit message from diff."""

        prompt = build_commit_prompt(cleaned_diff)
        return self.provider.generate(prompt=prompt, max_tokens=450, temperature=0.2)

    def generate_pr_description(self, cleaned_diff: str, commit_messages: List[str]) -> str:
        """Generate PR description from diff and commit history."""

        prompt = build_pr_prompt(cleaned_diff, commit_messages)
        return self.provider.generate(prompt=prompt, max_tokens=950, temperature=0.2)

    def generate_review(self, cleaned_diff: str) -> str:
        """Generate PR review feedback from diff."""

        prompt = build_review_prompt(cleaned_diff)
        return self.provider.generate(prompt=prompt, max_tokens=1200, temperature=0.1)
