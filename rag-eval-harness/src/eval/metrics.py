import re

def format_valid(answer: str) -> bool:
    return isinstance(answer, str) and len(answer.strip()) > 0

def citation_count(answer: str) -> int:
    return len(re.findall(r"\[.+?__\d+\]", answer))

def citation_coverage(answer: str) -> bool:
    return citation_count(answer) > 0

def context_hit(retrieved_chunks: list[str], expected_points: list[str]) -> bool:
    joined = " ".join(retrieved_chunks).lower()
    return all(p.lower() in joined for p in expected_points)
