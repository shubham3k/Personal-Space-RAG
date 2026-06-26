"""Smart LLM client with provider fallback."""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import AsyncGenerator

from config.settings import settings
from src.orchestrator.rate_limiter import RateLimiter


class ProviderStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class CircuitBreaker:
    def __init__(self, max_failures: int = 3, cooldown_base: float = 60.0):
        self.max_failures = max_failures
        self.cooldown_base = cooldown_base
        self.failure_count = 0
        self.last_failure = 0.0
        self.status = ProviderStatus.HEALTHY

    @property
    def cooldown_remaining(self) -> float:
        if self.status != ProviderStatus.DOWN:
            return 0.0
        cooldown = self.cooldown_base * (2 ** max(0, self.failure_count - self.max_failures))
        elapsed = time.time() - self.last_failure
        return max(0.0, cooldown - elapsed)

    def record_success(self) -> None:
        self.failure_count = 0
        self.status = ProviderStatus.HEALTHY

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure = time.time()
        if self.failure_count >= self.max_failures:
            self.status = ProviderStatus.DOWN

    def should_attempt(self) -> bool:
        if self.status == ProviderStatus.HEALTHY:
            return True
        if self.status == ProviderStatus.DOWN:
            if self.cooldown_remaining <= 0.0:
                self.status = ProviderStatus.DEGRADED
                return True
            return False
        return True


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
        self.rate_limiter = RateLimiter()
        self.circuit_breakers = {p.name: CircuitBreaker() for p in self.providers}

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
            cb = self.circuit_breakers.get(provider.name)
            if cb and not cb.should_attempt():
                errors[provider.name] = f"Circuit breaker open ({cb.cooldown_remaining:.0f}s remaining)"
                continue
            if provider.name in self._unavailable:
                continue
            if not self.rate_limiter.can_use(provider.name):
                errors[provider.name] = "Daily rate limit reached"
                continue
            try:
                await self.rate_limiter.acquire(provider.name)
                response = await provider.generate(
                    system=system,
                    user=user,
                    max_tokens=max_tokens or settings.groq_max_tokens,
                    temperature=temperature if temperature is not None else settings.groq_temperature,
                )
                if not response.content.strip():
                    raise ProviderConnectionError("Provider returned empty content")
                if cb:
                    cb.record_success()
                return response
            except RateLimitError as exc:
                errors[provider.name] = str(exc)
                if cb:
                    cb.record_failure()
                continue
            except (ProviderConnectionError, ProviderTimeoutError) as exc:
                errors[provider.name] = str(exc)
                if cb:
                    cb.record_failure()
                await asyncio.sleep(0.2)
                continue
            except Exception as exc:
                errors[provider.name] = str(exc)
                if cb:
                    cb.record_failure()
                continue
        raise AllProvidersFailedError(errors or {"providers": "No configured provider is available"})

    async def health(self) -> dict[str, bool]:
        results = {}
        for provider in self.providers:
            results[provider.name] = await provider.health_check()
        return results
