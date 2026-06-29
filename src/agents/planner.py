"""Multi-step query planner."""

import asyncio
from dataclasses import dataclass

from src.generation.generator import AnswerGenerator
from src.retrieval.retriever import Retriever


@dataclass
class PlanStep:
    query: str
    depends_on: list[int]


class MultiStepPlannerAgent:
    def __init__(self, retriever: Retriever | None = None, generator: AnswerGenerator | None = None):
        self.retriever = retriever or Retriever()
        self.generator = generator or AnswerGenerator()

    def plan(self, query: str) -> list[PlanStep]:
        import re
        lowered = query.lower()
        if re.search(r"\bvs\b", lowered):
            parts = re.split(r"\s+vs\s+", query, flags=re.IGNORECASE)
            if len(parts) >= 2:
                return [PlanStep(parts[0].strip(), []), PlanStep(parts[1].strip(), [])]
        if "compare" in lowered and " and " in lowered:
            parts_split = re.split(r"\bcompare\b", query, flags=re.IGNORECASE)
            if len(parts_split) >= 2:
                tail = parts_split[1]
                parts = [part.strip(" ?.") for part in re.split(r"\s+and\s+", tail, flags=re.IGNORECASE)[:5] if part.strip()]
                return [PlanStep(part, []) for part in parts]
        return [PlanStep(query, [])]

    async def run(self, query: str, top_k: int | None = None) -> dict:
        steps = self.plan(query)[:5]
        tasks = [asyncio.to_thread(self.retriever.retrieve, step.query, top_k) for step in steps]
        step_contexts = await asyncio.gather(*tasks)
        contexts = [item for group in step_contexts for item in group]
        prompt = "Original question: " + query + "\n\nSub-results:\n"
        for step, group in zip(steps, step_contexts):
            prompt += f"\nSub-query: {step.query}\nResults: {len(group)} chunks"
        result = await self.generator.generate(prompt, contexts)
        result["plan"] = [step.__dict__ for step in steps]
        return result
