"""Smart LLM client with provider fallback."""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator

from config.settings import settings


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    metadata: dict = field(default_factory=dict)


class ProviderError(Exception):
    """Base provider error."""


class RateLimitError(ProviderError):
    """Provider rate limit reached."""


class ProviderTimeoutError(ProviderError):
    """Provider timed out."""


class ProviderConnectionError(ProviderError):
    """Provider is unavailable or misconfigured."""


class AllProvidersFailedError(ProviderError):
    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        super().__init__("All LLM providers failed: " + "; ".join(f"{k}: {v}" for k, v in errors.items()))


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    async def generate_stream(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError


class LLMClient:
    def __init__(self, providers: list[BaseLLMProvider] | None = None):
        self.providers = providers if providers is not None else self._build_providers()
        self._unavailable: set[str] = set()

    def _build_providers(self) -> list[BaseLLMProvider]:
        providers: list[BaseLLMProvider] = []
        for name in settings.provider_list:
            if name == "groq" and settings.groq_api_key:
                from src.generation.providers.groq_provider import GroqProvider

                providers.append(GroqProvider(settings.groq_api_key, settings.groq_model, settings.groq_timeout))
            elif name == "cerebras" and settings.cerebras_api_key:
                from src.generation.providers.cerebras_provider import CerebrasProvider

                providers.append(CerebrasProvider(settings.cerebras_api_key, settings.cerebras_model, settings.cerebras_base_url))
            elif name == "gemini" and settings.google_api_key:
                from src.generation.providers.gemini_provider import GeminiProvider

                providers.append(GeminiProvider(settings.google_api_key, settings.gemini_model))
            elif name == "ollama":
                from src.generation.providers.ollama_provider import OllamaProvider

                providers.append(OllamaProvider(settings.ollama_base_url, settings.ollama_model))
        return providers

    async def generate(self, system: str, user: str, max_tokens: int | None = None, temperature: float | None = None) -> LLMResponse:
        errors: dict[str, str] = {}
        for provider in self.providers:
            if provider.name in self._unavailable:
                continue
            try:
                response = await provider.generate(
                    system=system,
                    user=user,
                    max_tokens=max_tokens or settings.groq_max_tokens,
                    temperature=temperature if temperature is not None else settings.groq_temperature,
                )
                if not response.content.strip():
                    raise ProviderConnectionError("Provider returned empty content")
                return response
            except RateLimitError as exc:
                errors[provider.name] = str(exc)
                continue
            except (ProviderConnectionError, ProviderTimeoutError) as exc:
                errors[provider.name] = str(exc)
                await asyncio.sleep(0.2)
                continue
            except Exception as exc:
                errors[provider.name] = str(exc)
                continue
        raise AllProvidersFailedError(errors or {"providers": "No configured provider is available"})

    async def health(self) -> dict[str, bool]:
        results = {}
        for provider in self.providers:
            results[provider.name] = await provider.health_check()
        return results
