from typing import Dict, Any


def fallback_on_failure(retrieval_context: Dict[str, Any], failures: str) -> Dict[str, Any]:
    """
    v1 stub: safe fallback response.
    TODO: implement fallback prompts/strategies.
    """
    return {
        "safe_response": "I couldn't retrieve enough sources. Please narrow the topic or add more documents.",
        "next_actions": ["narrow_topic", "rerun_ingestion"],
    }

