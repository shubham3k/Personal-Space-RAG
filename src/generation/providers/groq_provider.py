"""Groq provider."""

from typing import AsyncGenerator

from src.generation.llm_client import BaseLLMProvider, LLMResponse, ProviderConnectionError, ProviderTimeoutError, RateLimitError


class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", timeout: int = 30):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client = None

    @property
    def name(self) -> str:
        return "groq"

    def _get_client(self):
        if self._client is None:
            from groq import AsyncGroq

            self._client = AsyncGroq(api_key=self.api_key, timeout=self.timeout)
        return self._client

    async def generate(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> LLMResponse:
        try:
            response = await self._get_client().chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            choice = response.choices[0]
            usage = getattr(response, "usage", None)
            return LLMResponse(
                content=choice.message.content or "",
                provider=self.name,
                model=self.model,
                input_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
                output_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
            )
        except Exception as exc:
            self._raise_typed(exc)

    async def generate_stream(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> AsyncGenerator[str, None]:
        try:
            stream = await self._get_client().chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as exc:
            self._raise_typed(exc)

    async def health_check(self) -> bool:
        try:
            await self.generate("Reply with ok.", "ok", max_tokens=5)
            return True
        except Exception:
            return False

    def _raise_typed(self, exc: Exception):
        text = str(exc).lower()
        if "429" in text or "rate" in text:
            raise RateLimitError(f"Groq rate limit: {exc}") from exc
        if "timeout" in text:
            raise ProviderTimeoutError(f"Groq timeout: {exc}") from exc
        raise ProviderConnectionError(f"Groq error: {exc}") from exc
