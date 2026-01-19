import json
import os
import re
from datetime import datetime
from pathlib import Path

RAW_PATH = Path("data/raw/source1.txt")
OUT_PATH = Path("data/processed/chunks.jsonl")

DOC_ID = "source1"
TARGET_MIN = 400
TARGET_MAX = 800

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def split_into_paragraphs(text: str) -> list[str]:
    text = text.replace("\r\n", "\n")
    parts = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    return parts

def chunk_paragraphs(paragraphs: list[str], min_len: int, max_len: int) -> list[str]:
    chunks = []
    buf = ""
    for p in paragraphs:
        if not buf:
            buf = p
            continue

        # if adding paragraph keeps us under max, append
        if len(buf) + 2 + len(p) <= max_len:
            buf = buf + "\n\n" + p
        else:
            # flush current buffer
            chunks.append(buf.strip())
            buf = p

            # if paragraph itself is huge, hard-split
            while len(buf) > max_len:
                chunks.append(buf[:max_len].strip())
                buf = buf[max_len:].strip()

    if buf.strip():
        chunks.append(buf.strip())

    # ensure minimum length by merging tiny chunks forward
    merged = []
    i = 0
    while i < len(chunks):
        cur = chunks[i]
        while len(cur) < min_len and i + 1 < len(chunks):
            cur = (cur + "\n\n" + chunks[i + 1]).strip()
            i += 1
        merged.append(cur)
        i += 1

    return merged

def main():
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Missing {RAW_PATH}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    text = read_text(RAW_PATH)
    paras = split_into_paragraphs(text)
    chunks = chunk_paragraphs(paras, TARGET_MIN, TARGET_MAX)

    run_meta = {
        "run_type": "ingest",
        "doc_id": DOC_ID,
        "raw_path": str(RAW_PATH),
        "out_path": str(OUT_PATH),
        "ts": datetime.utcnow().isoformat() + "Z",
        "chunk_count": len(chunks),
        "target_min_chars": TARGET_MIN,
        "target_max_chars": TARGET_MAX,
        "raw_bytes": RAW_PATH.stat().st_size,
    }

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for idx, chunk in enumerate(chunks):
            obj = {
                "doc_id": DOC_ID,
                "chunk_id": f"{DOC_ID}__{idx:04d}",
                "text": chunk,
                "char_len": len(chunk),
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(json.dumps(run_meta, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
