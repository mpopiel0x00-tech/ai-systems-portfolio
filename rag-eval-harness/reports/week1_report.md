# Week 1 — RAG Eval Report (v0)

## Setup
- Qdrant: local Docker (port 6333)
- Collection: docs_v1
- Embeddings: text-embedding-3-small
- Answer model: gpt-4o-mini
- Source: data/raw/source1.txt (Qdrant guide article)

## Dataset
- testset_v1: 5 questions (JSONL)
- Expected points: 2–3 keywords/facts per question

## Metrics (current)
- tests: 5
- avg_latency_ms: 7388.3
- avg_citation_count: 2
- context_hit_rate: 0.2

## Bucket distribution (last run)
- OK: 1
- WRONG_CONTEXT: 4
- NO_RETRIEVAL: 0
- UNGROUNDED: 0
- FORMAT_FAIL: 0

## Top failure examples (2–3)
Format:
- test_id: ...
- question: ...
- expected_points: ...
- bucket: ...
- retrieved_chunk_ids: [...]
- note: (1 sentence)

## 1
- test_id: q01
- question: What is Qdrant? 
- expected_points: ['vector database', 'embeddings'] 
- bucket: WRONG_CONTEXT
- retrieved_chunk_ids: ['source1__0004', 'source1__0080', 'source1__0048', 'source1__0007', 'source1__0058']
- note: expected_points nie pojawiają się w retrieved context

## 2
- test_id: q04
- question: How is similarity measured in Qdrant?
- expected_points: ['cosine', 'distance']
- bucket: WRONG_CONTEXT
- retrieved_chunk_ids: ['source1__0004', 'source1__0080', 'source1__0048', 'source1__0007', 'source1__0058']
- note: retrieval zwrócił chunki o innym temacie

## Improvements
- Using prompt v1 increases avg_citation_count from 0 to 1.35, but increases latency.
- Increasing chunk_size on v2 reduced avg_latency_ms
- Citation metric fix (v2)
    - In v2, citations are returned as a structured list field: `answer.citations`.
    - We updated eval to compute `citation_count = len(citations)` instead of regex-counting `[chunk_id]` inside the answer text (v1 behavior).
    - Result: avg_citation_count became meaningful again (now ~1.45 on 20 tests).

## Day 3 update
- prompt_version: v2
- retrieval bug fixed: YES (ask_query used wrong question earlier)
- EVAL (20 tests): avg_latency_ms=6226, avg_citation_count=1.45, context_hit_rate=0.45
- bucket distribution (20): 
    - OK: 9
    - WRONG_CONTEXT: 11
    - NO_RETRIEVAL: 0
    - UNGROUNDED: 0
    - FORMAT_FAIL: 0
- main issue now: WRONG_CONTEXT (retrieval/expected_points)
- next 3 actions:
  1) Improve expected_points to match doc wording (reduce false WRONG_CONTEXT)
  2) Add overlap chunking OR sentence-based chunking (one change at a time)
  3) Add simple rerank: increase top_k to 15 then select 5 by keyword match (cheap)