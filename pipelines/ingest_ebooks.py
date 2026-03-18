from typing import Any, Dict, List


def ingest(source_items: List[Dict[str, Any]], index_name: str = "ebooks_index") -> Dict[str, Any]:
    """
    Contract (see contracts/ingest_ebooks.md):
    - read sources
    - parse + chunk + embed
    - upsert into the retrieval index
    outputs: index_stats {docs_seen, upserted_chunks, errors[]}
    """
    # v1 demo: do nothing but return a predictable stats payload.
    # TODO: implement real parsing/chunking/embedding and index writes.
    docs_seen = len(source_items or [])
    return {"docs_seen": docs_seen, "upserted_chunks": 0, "errors": []}


if __name__ == "__main__":
    print(ingest(source_items=[], index_name="ebooks_index"))

