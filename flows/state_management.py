from typing import Dict, Any


def state_management(session_id: str, operation: str, state_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    v1 stub. TODO: implement read/write/update to your persistence layer.
    operation: read|write|update
    """
    # v1 stub: treat `state_data` as the "updated_state" payload.
    return {"session_id": session_id, "operation": operation, "updated_state": state_data}

