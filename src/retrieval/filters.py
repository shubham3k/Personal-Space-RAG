"""Retrieval filter helpers."""


def build_where_filter(doc_type: str | None = None, source_path: str | None = None, media_type: str | None = None) -> dict | None:
    clauses = []
    if doc_type:
        clauses.append({"type": doc_type})
    if source_path:
        clauses.append({"source_path": source_path})
    if media_type:
        clauses.append({"media_type": media_type})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}
