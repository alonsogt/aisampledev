from typing import Dict, Any


def session_init(user_id: str, topic: str, persona: str = "default") -> Dict[str, Any]:
    """
    v1 stub: creates a session_id and initial context.
    TODO: integrate with your state store (Copilot globals, Dataverse, etc.).
    """
    return {
        "session_id": "sess_demo_001",
        "topic": topic,
        "persona": persona,
        "context": {},
    }

