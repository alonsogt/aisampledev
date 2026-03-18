from typing import List, Dict, Any


def get_passages(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Contract (see contracts/retrieval/get_passages.json):
    returns passages[] with:
      - title (str)
      - url (str)
      - snippet (str)
      - score (float)
    """
    # v1 demo: return deterministic dummy results so the pipeline works.
    # TODO: replace with real retrieval from your index/vector store.
    return [
        {
            "title": f"Example source for: {query}",
            "url": "file://local/sample-source",
            "snippet": "TODO: Replace with retrieved snippet text from your index.",
            "score": 0.42,
        }
    ][: max(1, int(top_k))]

