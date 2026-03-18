from typing import Dict, Any


def branch_next_step(quality_score: int, user_intent: str) -> str:
    """
    v1 stub: choose next step.
    TODO: implement branching rules.
    """
    if quality_score >= 7:
        return "complete"
    return "revise"

