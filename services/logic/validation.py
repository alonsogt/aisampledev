from typing import Dict, Any, List


def validate_input(user_input: Dict[str, Any], draft: Dict[str, Any]) -> Dict[str, Any]:
    """
    v1 stub to match blueprint Notes for:
    - `contracts/logic/validation.json`

    Inputs:
      - user_input: whatever the agent received from UI/user
      - draft: the generated draft payload

    Outputs:
      - validation_flags[]: strings describing checks that were applied
      - errors[]: strings describing failures
    """
    validation_flags: List[str] = ["topic_present", "draft_has_sections"]
    errors: List[str] = []

    if not (user_input or {}).get("topic"):
        errors.append("topic is required")

    if not (draft or {}).get("sections"):
        errors.append("draft.sections is required")

    return {"validation_flags": validation_flags, "errors": errors}

