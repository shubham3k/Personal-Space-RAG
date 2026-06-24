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

    def expand(self, query: str) -> list[str]:
        normalized = self.normalize(query)
        expansions = [normalized]
        lowered = normalized.lower()
        if "image" in lowered or "photo" in lowered or "screenshot" in lowered:
            expansions.append(f"{normalized} OCR visible text image description")
        if "audio" in lowered or "voice" in lowered or "recording" in lowered:
            expansions.append(f"{normalized} transcript spoken audio")
        return expansions
