"""RAG answer generator."""

from src.generation.citation_manager import sources_from_context
from src.generation.llm_client import LLMClient, LLMResponse
from src.generation.prompt_builder import PromptBuilder
from src.generation.response_parser import mark_truncated


class AnswerGenerator:
    def __init__(self, client: LLMClient | None = None, prompt_builder: PromptBuilder | None = None):
        self.client = client or LLMClient()
        self.prompt_builder = prompt_builder or PromptBuilder()

    async def generate(self, query: str, contexts: list[dict]) -> dict:
        response: LLMResponse = await self.client.generate(
            system=self.prompt_builder.system_prompt(),
            user=self.prompt_builder.build_user_prompt(query, contexts),
        )
        return {
            "answer": mark_truncated(response.content),
            "provider": response.provider,
            "model": response.model,
            "sources": sources_from_context(contexts),
            "usage": {"input_tokens": response.input_tokens, "output_tokens": response.output_tokens},
        }
