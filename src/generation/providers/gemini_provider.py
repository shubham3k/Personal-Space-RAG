"""Google Gemini provider."""

from typing import AsyncGenerator

from src.generation.llm_client import BaseLLMProvider, LLMResponse, ProviderConnectionError, ProviderTimeoutError, RateLimitError


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def name(self) -> str:
        return "gemini"

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def generate(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> LLMResponse:
        try:
            response = self._get_client().models.generate_content(
                model=self.model,
                contents=user,
                config={"system_instruction": system, "temperature": temperature, "max_output_tokens": max_tokens},
            )
            usage = getattr(response, "usage_metadata", None)
            return LLMResponse(
                content=response.text or "",
                provider=self.name,
                model=self.model,
                input_tokens=getattr(usage, "prompt_token_count", 0) if usage else 0,
                output_tokens=getattr(usage, "candidates_token_count", 0) if usage else 0,
            )
        except Exception as exc:
            text = str(exc).lower()
            if "429" in text or "quota" in text or "resource_exhausted" in text:
                raise RateLimitError(f"Gemini rate limit: {exc}") from exc
            if "timeout" in text:
                raise ProviderTimeoutError(f"Gemini timeout: {exc}") from exc
            raise ProviderConnectionError(f"Gemini error: {exc}") from exc

    async def generate_stream(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> AsyncGenerator[str, None]:
        try:
            stream = self._get_client().models.generate_content_stream(
                model=self.model,
                contents=user,
                config={"system_instruction": system, "temperature": temperature, "max_output_tokens": max_tokens},
            )
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
        except Exception as exc:
            raise ProviderConnectionError(f"Gemini streaming error: {exc}") from exc

    async def health_check(self) -> bool:
        try:
            response = await self.generate("Reply ok.", "ok", max_tokens=5)
            return bool(response.content)
        except Exception:
            return False
