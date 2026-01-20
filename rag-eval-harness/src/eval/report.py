import json
import time
from pathlib import Path
from statistics import mean
from src.eval.buckets import assign_bucket

import requests

from src.eval.metrics import (
    format_valid,
    citation_count,
    citation_coverage,
    context_hit,
)

CHUNKS_PATH = Path("data/processed/chunks.jsonl")

def load_chunk_map():
    m = {}
    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            m[obj["chunk_id"]] = obj["text"]
    return m

TESTSET_PATH = Path("data/testset_v1.jsonl")
OUT_PATH = Path("logs/eval_results.jsonl")
API_URL = "http://localhost:8000/ask"

def load_testset():
    with TESTSET_PATH.open("r", encoding="utf-8") as f:
        return [json.loads(l) for l in f]

def append_result(obj: dict):
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def main():
    chunk_map = load_chunk_map()
    tests = load_testset()

    latencies = []
    citation_counts = []
    coverage_hits = []

    for t in tests:
        t0 = time.time()

        r = requests.post(API_URL, json={"query": t["question"]})
        r.raise_for_status()
        data = r.json()

        latency_ms = (time.time() - t0) * 1000
        latencies.append(latency_ms)

        answer = data["answer"]["answer"]
        retrieved_ids = data["answer"]["retrieved_chunk_ids"]

        retrieved_texts = [chunk_map.get(cid, "") for cid in retrieved_ids]
        cov = context_hit(retrieved_texts, t["expected_points"])
        coverage_hits.append(cov)

        cc = citation_count(answer)
        citation_counts.append(cc)

        result = {
            "test_id": t["id"],
            "question": t["question"],
            "expected_points": t["expected_points"],
            "answer": answer,
            "retrieved_chunk_ids": retrieved_ids,
            "latency_ms": round(latency_ms, 1),
            "format_valid": format_valid(answer),
            "citation_count": cc,
            "citation_coverage": citation_coverage(answer),
            "context_hit": cov,
            "retrieved_text_preview": [rt[:120] for rt in retrieved_texts],
        }

        result["bucket"] = assign_bucket(result)
        append_result(result)

    summary = {
        "tests": len(tests),
        "avg_latency_ms": round(mean(latencies), 1),
        "avg_citation_count": round(mean(citation_counts), 2),
        "context_hit_rate": round(sum(coverage_hits) / len(coverage_hits), 2),
    }

    print("EVAL SUMMARY")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
