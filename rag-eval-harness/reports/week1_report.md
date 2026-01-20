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

## Next improvements (3)
1) Improve expected_points quality (make them appear in retrieved context)
2) Tune retrieval params (top_k, chunk size) and rerun eval
3) Return retrieved chunk texts in /ask response (for better debugging)
