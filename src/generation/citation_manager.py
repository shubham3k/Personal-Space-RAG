"""Citation formatting helpers."""


def sources_from_context(contexts: list[dict]) -> list[dict]:
    sources = []
    for idx, item in enumerate(contexts, start=1):
        metadata = item.get("metadata", {})
        sources.append(
            {
                "number": idx,
                "title": metadata.get("title", "Untitled"),
                "source_path": metadata.get("source_path", ""),
                "media_type": metadata.get("media_type", metadata.get("type", "text")),
                "thumbnail_path": metadata.get("thumbnail_path", ""),
                "transcript_path": metadata.get("transcript_path", ""),
                "score": item.get("score", 0),
            }
        )
    return sources
