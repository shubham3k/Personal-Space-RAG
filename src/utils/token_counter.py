"""Token counting with a safe fallback."""


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        import tiktoken

        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        return max(1, len(text) // 4)
