from typing import Dict, Any


def welcome_screen(user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stub UI step: decide what the agent should ask first.
    TODO: implement real UI/UX adapter.
    """
    return {"intent": "select_topic"}

