# RAG Eval Harness (Week 1)

## Goal (Week 1)
Build an end-to-end RAG skeleton with logging + eval harness from day 1.

## Today (Day 1) - DONE
- Qdrant local via Docker
- Ingest: data/raw -> data/processed/chunks.jsonl
- Index: embeddings -> Qdrant collection
- Query: retrieval + answer with citations
- Logs: logs/runs.jsonl contains index + query runs

## Setup
### 1) Python env
- Create venv: `.venv`
- Install: `pip install -r requirements.txt`

### 2) Qdrant
- Start: `docker compose up -d`
- Stop: `docker compose down`
- Logs: `docker compose logs -f`

## Run
1) Ingest:
- `python src/ingest.py`
2) Index:
- `python -m src.index_qdrant`
3) Query:
- `python -m src.query_rag`

## Config
- `.env` (not committed)
- Collection: `docs_v1`
- Embedding model: `text-embedding-3-small`
- LLM model (answer): `gpt-4o-mini`
