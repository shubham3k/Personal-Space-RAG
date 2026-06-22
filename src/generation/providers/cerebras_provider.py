"""Cerebras OpenAI-compatible provider."""

from typing import AsyncGenerator

import httpx

from src.generation.llm_client import BaseLLMProvider, LLMResponse, ProviderConnectionError, ProviderTimeoutError, RateLimitError


class CerebrasProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b", base_url: str = "https://api.cerebras.ai/v1"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(base_url=base_url, timeout=60.0, headers={"Authorization": f"Bearer {api_key}"})

    @property
    def name(self) -> str:
        return "cerebras"

    async def generate(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        try:
            response = await self.client.post("/chat/completions", json=payload)
            if response.status_code == 429:
                raise RateLimitError("Cerebras rate limit")
            response.raise_for_status()
            data = response.json()
            usage = data.get("usage", {})
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider=self.name,
                model=self.model,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
            )
        except RateLimitError:
            raise
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(f"Cerebras timeout: {exc}") from exc
        except Exception as exc:
            raise ProviderConnectionError(f"Cerebras error: {exc}") from exc

    async def generate_stream(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> AsyncGenerator[str, None]:
        response = await self.generate(system, user, max_tokens, temperature)
        yield response.content

    async def health_check(self) -> bool:
        try:
            await self.generate("Reply ok.", "ok", max_tokens=5)
            return True
        except Exception:
            return False
