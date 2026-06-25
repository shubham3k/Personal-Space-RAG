"""Intent classification for routing user queries."""

from dataclasses import dataclass
from enum import StrEnum


class Intent(StrEnum):
    SIMPLE_RECALL = "simple_recall"
    TEMPORAL_RECALL = "temporal_recall"
    MULTI_STEP = "multi_step"
    REFLECTION = "reflection"
    CONNECTION = "connection"
    SYNTHESIS = "synthesis"
    PREPARATION = "preparation"
    CONVERSATIONAL = "conversational"
    META = "meta"
    COMMAND = "command"


@dataclass
class IntentResult:
    intent: Intent
    confidence: float
    reason: str


class IntentRouter:
    """Fast heuristic router with safe default to simple recall."""

    def classify(self, query: str) -> IntentResult:
        text = query.strip().lower()
        if len(text) <= 2:
            return IntentResult(Intent.SIMPLE_RECALL, 0.6, "Very short query")
        if text in {"hi", "hello", "thanks", "thank you", "what can you do"}:
            return IntentResult(Intent.CONVERSATIONAL, 0.95, "Conversational phrase")
        if any(term in text for term in ("how many documents", "stats", "status", "health", "how many files")):
            return IntentResult(Intent.META, 0.9, "System stats request")
        if any(term in text for term in ("reindex", "clear cache", "sync", "connect", "disconnect")):
            return IntentResult(Intent.COMMAND, 0.85, "System command request")
        if any(term in text for term in ("prepare me", "brief me", "meeting with", "tomorrow's meeting")):
            return IntentResult(Intent.PREPARATION, 0.9, "Preparation request")
        if any(term in text for term in ("weekly review", "daily digest", "monthly reflection", "summarize my week")):
            return IntentResult(Intent.SYNTHESIS, 0.9, "Digest/synthesis request")
        if any(term in text for term in ("pattern", "recurring", "themes", "why am i", "overwhelmed", "sentiment")):
            return IntentResult(Intent.REFLECTION, 0.8, "Reflection pattern request")
        if any(term in text for term in ("connection", "connect", "relate", "relationship between", "link between")):
            return IntentResult(Intent.CONNECTION, 0.8, "Connection request")
        if any(term in text for term in ("compare", "versus", " vs ", "evolved", "changed from", "q1", "q2")):
            return IntentResult(Intent.MULTI_STEP, 0.8, "Comparative multi-step request")
        if any(term in text for term in ("yesterday", "today", "last week", "last month", "last tuesday", "tomorrow", "march", "january")):
            return IntentResult(Intent.TEMPORAL_RECALL, 0.75, "Temporal recall request")
        return IntentResult(Intent.SIMPLE_RECALL, 0.7, "Default recall route")
