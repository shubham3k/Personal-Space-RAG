import pytest

from src.generation.llm_client import BaseLLMProvider, LLMClient, LLMResponse, ProviderConnectionError


class FailingProvider(BaseLLMProvider):
    @property
    def name(self):
        return "failing"

    async def generate(self, system, user, max_tokens=2048, temperature=0.1):
        raise ProviderConnectionError("nope")

    async def generate_stream(self, system, user, max_tokens=2048, temperature=0.1):
        yield ""

    async def health_check(self):
        return False


class WorkingProvider(BaseLLMProvider):
    @property
    def name(self):
        return "working"

    async def generate(self, system, user, max_tokens=2048, temperature=0.1):
        return LLMResponse(content="ok", provider=self.name, model="test")

    async def generate_stream(self, system, user, max_tokens=2048, temperature=0.1):
        yield "ok"

    async def health_check(self):
        return True


@pytest.mark.asyncio
async def test_llm_client_falls_back():
    client = LLMClient(providers=[FailingProvider(), WorkingProvider()])
    response = await client.generate("system", "user")
    assert response.provider == "working"
