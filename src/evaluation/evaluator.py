"""Run evaluation cases against the RAG pipeline."""

import json
from pathlib import Path

from src.evaluation.metrics import RAGEvaluator
from src.orchestrator.rag_pipeline import RAGPipeline


async def run_eval(test_query_path: str = "src/evaluation/test_queries.json") -> list[dict]:
    path = Path(test_query_path)
    cases = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    pipeline = RAGPipeline()
    evaluator = RAGEvaluator()
    results = []
    for case in cases:
        response = await pipeline.ask(case["query"])
        contexts = [source.get("source_path", "") for source in response.get("sources", [])]
        metric = evaluator.evaluate_single(case["query"], response["answer"], contexts)
        results.append(metric.__dict__)
    return results
