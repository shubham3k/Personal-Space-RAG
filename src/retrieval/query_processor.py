"""Query validation and normalization."""

from config.constants import MAX_QUERY_LENGTH, MIN_QUERY_LENGTH


class QueryProcessor:
    def normalize(self, query: str) -> str:
        normalized = " ".join(query.strip().split())
        if len(normalized) < MIN_QUERY_LENGTH:
            raise ValueError("Query is too short.")
        if len(normalized) > MAX_QUERY_LENGTH:
            raise ValueError("Query is too long.")
        return normalized
