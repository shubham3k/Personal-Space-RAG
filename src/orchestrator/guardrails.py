"""Simple input guardrails."""


def validate_user_query(query: str) -> str:
    cleaned = " ".join(query.strip().split())
    if not cleaned:
        raise ValueError("Query cannot be empty.")
    return cleaned
