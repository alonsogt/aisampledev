from typing import Dict, Any


def analytics_logging(session_id: str, tokens: Dict[str, Any], quality: str) -> Dict[str, Any]:
    """
    v1 stub. TODO: wire metrics storage (Dataverse, log service, etc.).
    """
    return {"stored_metrics": {"session_id": session_id, "tokens": tokens, "quality": quality}}

