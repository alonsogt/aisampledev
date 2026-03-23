from __future__ import annotations

from typing import Dict, Any


def questionnaire_intake(answers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contract: see contracts/logic/questionnaire_intake.json

    Inputs (conceptual):
      - answers: questionCount, style, tone, audience, structureOptions[]

    Outputs:
      - preferences: normalized options used by outline/draft generation
    """
    answers = answers or {}

    question_count = int(answers.get("questionCount") or answers.get("question_count") or 6)
    style = str(answers.get("style") or "professional").strip()
    tone = str(answers.get("tone") or "confident").strip()
    audience = str(answers.get("audience") or "content teams").strip()

    structure_options = answers.get("structureOptions") or answers.get("structure_options") or []
    if not isinstance(structure_options, list):
        structure_options = [str(structure_options)]

    # v1 normalization: collapse options into a stable "structure" descriptor.
    structure = ",".join([str(x).strip() for x in structure_options if str(x).strip()]) or "default"

    return {
        "questionCount": question_count,
        "style": style,
        "tone": tone,
        "audience": audience,
        "structure": structure,
    }

