from typing import Dict, Any, List
from services.retrieval.get_passages import get_passages


def knowledge_retrieval(query: str, session_id: str = "", top_k: int = 5) -> Dict[str, Any]:
    """
    v1 stub wrapper around services.retrieval.get_passages.
    TODO: connect to your runtime context/session store.
    """
    passages = get_passages(query=query, top_k=top_k)
    return {"session_id": session_id, "query": query, "passages": passages, "citations": []}

