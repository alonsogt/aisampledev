from typing import Dict, Any

from services.retrieval.get_passages import get_passages
from services.outline.generate_outline import generate_outline
from services.outline.generate_draft import generate_draft
from services.output.create_docx import create_docx


def run_ebook_agent(user_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    v1 contract (keep it simple):
    inputs:
      - topic (str)
      - top_k (int, optional)
      - brief (dict optional)
    outputs:
      - outline {title, sections:[{heading, bullets[]}]}
      - draft {title, sections:[{heading, paragraphs:[...]}]}
      - doc_url (str)
    """
    topic = (user_request.get("topic") or "").strip()
    top_k = int(user_request.get("top_k") or 5)

    brief = user_request.get("brief") or {
        "what": "",
        "who": "",
        "never": "",
        "success": "",
    }

    if not topic:
        raise ValueError("user_request.topic is required")

    # 1) retrieval
    passages = get_passages(query=topic, top_k=top_k)

    # 2) outline
    outline = generate_outline(topic=topic, passages=passages, brief=brief)

    # 3) draft (outline -> paragraphs)
    draft = generate_draft(outline=outline, passages=passages, brief=brief)

    # 4) output
    metadata = {"topic": topic}
    doc_url = create_docx(outline=outline, draft=draft, metadata=metadata)

    return {
        "topic": topic,
        "outline": outline,
        "draft": draft,
        "doc_url": doc_url,
    }

