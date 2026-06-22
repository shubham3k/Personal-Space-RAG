"""Ollama local provider."""

import json
from typing import AsyncGenerator

import httpx

from src.generation.llm_client import BaseLLMProvider, LLMResponse, ProviderConnectionError, ProviderTimeoutError


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(base_url=base_url, timeout=120.0)

    @property
    def name(self) -> str:
        return "ollama"

    async def generate(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        try:
            response = await self.client.post("/api/chat", json=payload)
            if response.status_code == 404:
                raise ProviderConnectionError(f"Model '{self.model}' not found. Run: ollama pull {self.model}")
            response.raise_for_status()
            data = response.json()
            return LLMResponse(
                content=data["message"]["content"],
                provider=self.name,
                model=self.model,
                input_tokens=data.get("prompt_eval_count", 0),
                output_tokens=data.get("eval_count", 0),
            )
        except ProviderConnectionError:
            raise
        except httpx.ConnectError as exc:
            raise ProviderConnectionError("Cannot connect to Ollama. Start it with: ollama serve") from exc
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("Ollama timed out. Try a smaller local model.") from exc

    async def generate_stream(self, system: str, user: str, max_tokens: int = 2048, temperature: float = 0.1) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        try:
            async with self.client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if data.get("done"):
                        break
        except httpx.ConnectError as exc:
            raise ProviderConnectionError("Cannot connect to Ollama for streaming") from exc

    async def health_check(self) -> bool:
        try:
            response = await self.client.get("/api/tags")
            if response.status_code != 200:
                return False
            names = [model.get("name", "") for model in response.json().get("models", [])]
            return self.model in names or self.model.split(":")[0] in [name.split(":")[0] for name in names]
        except Exception:
            return False
