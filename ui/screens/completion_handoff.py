from typing import Dict, Any


def completion_handoff(doc_url: str) -> Dict[str, Any]:
    """
    Stub: tell the agent what the next step is after doc creation.
    """
    return {"next_action": "done", "doc_url": doc_url}

