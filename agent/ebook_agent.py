import os
from typing import Dict, Any

from services.ingestion.build_index import build_latest_index
from services.retrieval.get_passages import get_passages
from services.logic.questionnaire_intake import questionnaire_intake
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
      - grounding_sources (list[dict], optional)
      - answers (dict, optional)
    outputs:
      - outline {title, sections:[{heading, bullets[]}]}
      - draft {title, sections:[{heading, paragraphs:[...]}]}
      - doc_url (str)
    """
    topic = (user_request.get("topic") or "").strip()
    top_k = int(user_request.get("top_k") or 5)

    answers = user_request.get("answers") or {}
    grounding_sources = user_request.get("grounding_sources") or []

    brief = user_request.get("brief") or {
        "what": "",
        "who": "",
        "never": "",
        "success": "",
    }

    if not topic:
        raise ValueError("user_request.topic is required")

    # 1) Build (or refresh) the RAG index from blueprint grounding sources.
    #    If SHAREPOINT_BEARER_TOKEN is set, real file downloads happen.
    #    Otherwise the index is built from source notes as a fallback.
    verbose = os.getenv("RAG_VERBOSE", "").lower() in {"1", "true", "yes"}
    if grounding_sources:
        build_latest_index(grounding_sources, verbose=verbose)

    # 2) Retrieve relevant passages from the freshly built index.
    passages = get_passages(query=topic, top_k=top_k, sources=grounding_sources)

    # 3) Questionnaire intake → preferences object
    preferences = questionnaire_intake(answers=answers)

    # 4) Outline (optionally shaped by questionnaire preferences)
    outline = generate_outline(topic=topic, passages=passages, brief=brief, preferences=preferences)

    # 5) Draft (outline -> paragraphs)
    draft = generate_draft(outline=outline, passages=passages, brief=brief, preferences=preferences)

    # 6) Output
    metadata = {"topic": topic, "preferences": preferences}
    doc_url = create_docx(outline=outline, draft=draft, metadata=metadata)

    return {
        "topic": topic,
        "outline": outline,
        "draft": draft,
        "doc_url": doc_url,
    }

