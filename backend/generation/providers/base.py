"""
LLM Provider Protocol — the interface contract every provider must implement.

Architecture §1.5:
    class LLMProvider(Protocol):
        async def generate(self, prompt: str, max_tokens: int, temperature: float) -> LLMResponse:
            ...

Both IBM Granite (primary) and Gemini (fallback) implement this protocol.
Neither is wired yet; this module defines the contract only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class LLMResponse:
    """Unified response object returned by any LLM provider."""

    content: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw: object = None  # The raw SDK response, for debugging


@runtime_checkable
class LLMProvider(Protocol):
    """
    Protocol that all LLM providers must satisfy.

    Implementations:
        - backend/generation/providers/granite.py  (IBM Granite — primary)
        - backend/generation/providers/gemini.py   (Gemini — fallback)
    """

    async def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """
        Send a prompt to the provider and return a structured response.

        Args:
            prompt: The fully-assembled RAG prompt string.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (lower = more deterministic).

        Returns:
            LLMResponse with the generated text and token counts.

        Raises:
            ProviderError: If the provider cannot fulfil the request.
        """
        ...


class ProviderError(Exception):
    """Raised by an LLM provider on non-retryable failure."""
