def assign_bucket(result: dict) -> str:
    # result is one eval record
    if not result.get("format_valid", True):
        return "FORMAT_FAIL"

    retrieved = result.get("retrieved_chunk_ids", [])
    if not retrieved or len(retrieved) == 0:
        return "NO_RETRIEVAL"

    if not result.get("context_hit", False):
        return "WRONG_CONTEXT"

    if result.get("citation_count", 0) == 0:
        return "UNGROUNDED"

    return "OK"
