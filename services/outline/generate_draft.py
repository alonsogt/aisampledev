from typing import Dict, Any, List


def generate_draft(outline: Dict[str, Any], passages: List[Dict[str, Any]], brief: Dict[str, str]) -> Dict[str, Any]:
    """
    Draft contract (see contracts/outline/generate_draft.json):
    inputs:
      - outline {title, sections:[{heading, bullets[]}]}
      - passages[] {title,url,snippet,score}
      - brief {what,who,never,success}
    outputs:
      - draft {title, sections:[{heading, paragraphs:[...]}]}
    """
    title = outline.get("title", "")
    sections_out = []

    for s in (outline.get("sections") or []):
        heading = s.get("heading", "Section")
        bullets = s.get("bullets") or []

        # v1 demo: convert bullets -> paragraphs using snippets as inspiration.
        snippet = (passages[0].get("snippet") if passages else "") or ""
        paragraphs = [
            f"{heading}: {bullets[0] if bullets else 'Overview'}",
            f"Expanded context: {snippet[:180]}{'...' if len(snippet) > 180 else ''}".strip(),
        ]

        sections_out.append({"heading": heading, "paragraphs": paragraphs})

    return {"title": title, "sections": sections_out}

