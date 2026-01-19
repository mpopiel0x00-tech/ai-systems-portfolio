import json
import time
import uuid
from datetime import datetime
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_EMBED_MODEL, QDRANT_URL, QDRANT_COLLECTION

CHUNKS_PATH = Path("data/processed/chunks.jsonl")
RUNS_PATH = Path("logs/runs.jsonl")

def load_chunks(path: Path):
    chunks = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def append_run(obj: dict):
    RUNS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RUNS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def main():
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY in .env")

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Missing {CHUNKS_PATH}")

    run_id = f"index__{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}__{uuid.uuid4().hex[:8]}"
    t0 = time.time()

    chunks = load_chunks(CHUNKS_PATH)

    client = QdrantClient(url=QDRANT_URL)
    openai = OpenAI(api_key=OPENAI_API_KEY)

    # create / recreate collection (simple for day1)
    # vector size will be inferred from first embedding
    sample = openai.embeddings.create(model=OPENAI_EMBED_MODEL, input="hello").data[0].embedding
    dim = len(sample)

    client.recreate_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    # embed + upsert (na start prosto, bez batch optymalizacji)
    points = []
    embed_errors = 0

    for i, ch in enumerate(chunks):
        try:
            emb = openai.embeddings.create(model=OPENAI_EMBED_MODEL, input=ch["text"]).data[0].embedding
            points.append(
                PointStruct(
                    id=i,
                    vector=emb,
                    payload={
                        "doc_id": ch["doc_id"],
                        "chunk_id": ch["chunk_id"],
                        "text": ch["text"],
                    },
                )
            )
        except Exception as e:
            embed_errors += 1

    client.upsert(collection_name=QDRANT_COLLECTION, points=points)

    t1 = time.time()
    run = {
        "run_id": run_id,
        "run_type": "index",
        "ts": datetime.utcnow().isoformat() + "Z",
        "collection": QDRANT_COLLECTION,
        "qdrant_url": QDRANT_URL,
        "embed_model": OPENAI_EMBED_MODEL,
        "chunk_count_in": len(chunks),
        "points_written": len(points),
        "embed_errors": embed_errors,
        "elapsed_sec": round(t1 - t0, 3),
    }
    append_run(run)
    print(json.dumps(run, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()