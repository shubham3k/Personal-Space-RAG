"""Build prompts for retrieval-augmented answers."""

from pathlib import Path

from config.constants import CONTEXT_BUDGET
from src.utils.token_counter import count_tokens


class PromptBuilder:
    def __init__(self, system_prompt_path: str = "config/prompts/system_prompt.md"):
        self.system_prompt_path = system_prompt_path

    def system_prompt(self) -> str:
        return Path(self.system_prompt_path).read_text(encoding="utf-8")

    def build_user_prompt(self, query: str, contexts: list[dict]) -> str:
        blocks = []
        budget = CONTEXT_BUDGET
        used = 0
        for idx, item in enumerate(contexts, start=1):
            metadata = item.get("metadata", {})
            source = metadata.get("source_path", "unknown")
            title = metadata.get("title", "Untitled")
            block = f"[{idx}] {title}\nSource: {source}\n{item.get('content', '')}"
            tokens = count_tokens(block)
            if used + tokens > budget:
                break
            used += tokens
            blocks.append(block)
        context = "\n\n".join(blocks) if blocks else "No relevant local context was found."
        return f"Question:\n{query}\n\nContext:\n{context}\n\nAnswer with citations when using context."
