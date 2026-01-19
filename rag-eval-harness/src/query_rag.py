import json
import time
import uuid
from datetime import datetime
from pathlib import Path

from qdrant_client import QdrantClient
from openai import OpenAI

from src.config import (
    OPENAI_API_KEY,
    OPENAI_EMBED_MODEL,
    QDRANT_URL,
    QDRANT_COLLECTION,
)

PROMPT_PATH = Path("prompts/rag_answer_v1.txt")
RUNS_PATH = Path("logs/runs.jsonl")

TOP_K = 5

def append_run(obj: dict):
    RUNS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RUNS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def build_context(points):
    blocks = []
    for p in points:
        cid = p.payload["chunk_id"]
        txt = p.payload["text"]
        blocks.append(f"[{cid}]\n{txt}")
    return "\n\n".join(blocks)

def main():
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY")

    question = "What is Qdrant and how does it store vectors?"

    client = QdrantClient(url=QDRANT_URL)
    openai = OpenAI(api_key=OPENAI_API_KEY)

    run_id = f"query__{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}__{uuid.uuid4().hex[:8]}"
    t0 = time.time()

    # embed query
    q_emb = openai.embeddings.create(
        model=OPENAI_EMBED_MODEL,
        input=question
    ).data[0].embedding

    # search
    res = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=q_emb,
        limit=TOP_K,
        with_payload=True,
    )
    hits = res.points

    retrieved_ids = [p.payload["chunk_id"] for p in hits]
    context = build_context(hits)

    prompt = PROMPT_PATH.read_text(encoding="utf-8").format(
        context=context,
        question=question,
    )

    # generate answer
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    answer = resp.choices[0].message.content

    t1 = time.time()

    run = {
        "run_id": run_id,
        "run_type": "query",
        "ts": datetime.utcnow().isoformat() + "Z",
        "question": question,
        "top_k": TOP_K,
        "retrieved_chunk_ids": retrieved_ids,
        "answer": answer,
        "elapsed_sec": round(t1 - t0, 3),
    }

    append_run(run)

    print("ANSWER:\n")
    print(answer)
    print("\nRUN LOGGED:", run_id)

if __name__ == "__main__":
    main()
