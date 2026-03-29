"""Tests for AI provider factory."""

import unittest

from gitpush.ai.config import AIConfig
from gitpush.ai.factory import AIProviderFactory
from gitpush.ai.providers.anthropic import AnthropicProvider
from gitpush.ai.providers.local import LocalAIProvider
from gitpush.ai.providers.openai import OpenAIProvider
from gitpush.exceptions import AIConfigurationError


class TestAIProviderFactory(unittest.TestCase):
    """Factory behavior for supported providers."""

    def test_create_local_provider(self):
        config = AIConfig(provider="local")
        provider = AIProviderFactory.create(config)
        self.assertIsInstance(provider, LocalAIProvider)

    def test_create_openai_provider(self):
        config = AIConfig(provider="openai", openai_api_key="test-key")
        provider = AIProviderFactory.create(config)
        self.assertIsInstance(provider, OpenAIProvider)

    def test_create_anthropic_provider(self):
        config = AIConfig(provider="anthropic", anthropic_api_key="test-key")
        provider = AIProviderFactory.create(config)
        self.assertIsInstance(provider, AnthropicProvider)

    def test_openai_requires_key(self):
        config = AIConfig(provider="openai", openai_api_key="")
        with self.assertRaises(AIConfigurationError):
            AIProviderFactory.create(config)

    def test_anthropic_requires_key(self):
        config = AIConfig(provider="anthropic", anthropic_api_key="")
        with self.assertRaises(AIConfigurationError):
            AIProviderFactory.create(config)

    def test_unknown_provider_raises(self):
        config = AIConfig(provider="unknown")
        with self.assertRaises(AIConfigurationError):
            AIProviderFactory.create(config)


if __name__ == "__main__":
    unittest.main()
