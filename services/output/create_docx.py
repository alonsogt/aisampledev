from typing import Dict, Any


def create_docx(outline: Dict[str, Any], draft: Dict[str, Any], metadata: Dict[str, Any]) -> str:
    """
    Contract (see contracts/output/create_docx.json):
    inputs:
      - outline
      - draft
      - metadata
    outputs:
      - sharepoint_url OR local_file_path
    """
    # v1 demo implementation:
    # - creates a local .txt "document" as a placeholder so there are no heavy deps
    # - later replace with real .docx rendering (python-docx) and/or SharePoint upload.
    topic = (metadata or {}).get("topic") or ""
    preferences = (metadata or {}).get("preferences") or {}
    out_path = f"agent-runtime-sample_output_{topic.replace(' ', '_')}.txt"

    lines = []
    lines.append(draft.get("title") or outline.get("title") or "Draft")
    lines.append("")
    if preferences:
        lines.append("Questionnaire preferences:")
        for k, v in preferences.items():
            lines.append(f"- {k}: {v}")
        lines.append("")
    for sec in draft.get("sections") or []:
        lines.append(str(sec.get("heading") or "Section"))
        lines.append("")
        for p in sec.get("paragraphs") or []:
            lines.append(str(p))
            lines.append("")
        lines.append("---")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path

