"""Response post-processing."""


def mark_truncated(text: str) -> str:
    stripped = text.strip()
    if stripped and stripped[-1] not in ".!?)]}\"'":
        return stripped + "..."
    return stripped
