from typing import Dict, Any

from services.output.create_docx import create_docx


def output_generation(outline: Dict[str, Any], draft: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    v1 stub: create a doc and return output URL/path.
    TODO: integrate outline->body and use your real doc renderer.
    """
    doc_url = create_docx(outline=outline, draft=draft, metadata=context or {})
    return {"output_url": doc_url, "quality_status": "needs_review"}

