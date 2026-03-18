from typing import Dict, Any


def topic_selection(user_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stub: pick a topic from the user request.
    """
    return {"topic": user_request.get("topic", "")}

