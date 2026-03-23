from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


def _deterministic_draft(outline: Dict[str, Any], passages: List[Dict[str, Any]], preferences: Dict[str, Any]) -> Dict[str, Any]:
    title        = outline.get("title", "")
    section_list = outline.get("sections") or []
    audience     = preferences.get("audience") or ""
    style        = preferences.get("style")    or ""
    sections_out = []
    for s in section_list:
        heading = s.get("heading", "Section")
        bullets = s.get("bullets") or []
        snippet = (passages[0].get("snippet") if passages else "") or ""
        paragraphs = [
            f"{heading}: {bullets[0] if bullets else 'Overview'}",
            f"Expanded context: {snippet[:180]}{'...' if len(snippet) > 180 else ''}".strip(),
            (f"Adaptation: Write this for {audience} in a {style} tone." if (audience or style) else ""),
        ]
        sections_out.append({"heading": heading, "paragraphs": [p for p in paragraphs if p]})
    return {"title": title, "sections": sections_out}


def generate_draft(
    outline: Dict[str, Any],
    passages: List[Dict[str, Any]],
    brief: Dict[str, str],
    preferences: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Expand outline into a full draft using Azure OpenAI (preferred) or Claude (fallback).

    Draft shape:
      { "title": str, "sections": [{"heading": str, "paragraphs": [str]}] }
    """
    azure_key  = os.getenv("AZURE_OPENAI_KEY", "")
    claude_key = os.getenv("CLAUDE_API_KEY", "")

    prefs     = preferences or {}
    style     = prefs.get("style")     or ""
    tone      = prefs.get("tone")      or ""
    audience  = prefs.get("audience")  or ""
    structure = prefs.get("structure") or ""

    title        = outline.get("title", "")
    what    = (brief or {}).get("what")    or ""
    who     = (brief or {}).get("who")     or ""
    never   = (brief or {}).get("never")   or ""
    success = (brief or {}).get("success") or ""

    passages_text = "\n\n".join(
        [f"- {p.get('title','')}\n  snippet: {p.get('snippet','')}" for p in (passages or [])[:5]]
    )

    system = (
        "You are a blueprint runtime assistant that expands an ebook outline into a draft.\n"
        "Follow the Brief constraints and write in the requested tone/style.\n"
        "Base key factual claims only on the provided passages; never fabricate citations.\n"
    )

    user_prompt = (
        f"Brief.what: {what}\nBrief.who: {who}\nBrief.never: {never}\nBrief.success: {success}\n\n"
        f"Preferences:\n- audience: {audience}\n- tone: {tone}\n- style: {style}\n- structure: {structure}\n\n"
        f"Outline JSON:\n{outline}\n\n"
        f"Passages/examples (use to ground content):\n{passages_text}\n\n"
        "Write the draft following the outline order.\n"
        "For each section write 3-5 paragraphs. Paragraphs should be practical, clear, and match the tone/style.\n"
        "Avoid quoting verbatim from sources; paraphrase.\n"
        "Return JSON only, shape: {\"draft\":{\"title\":\"...\",\"sections\":[{\"heading\":\"...\",\"paragraphs\":[\"...\"]}]}}\n"
    )

    # ── Azure OpenAI (preferred) ─────────────────────────────────────────────
    if azure_key:
        try:
            from llm.azure_openai_http import call_azure_json
            data  = call_azure_json(system, user_prompt, max_tokens=4096)
            draft = (data.get("draft") if isinstance(data, dict) else None) or data
            if isinstance(draft, dict) and draft.get("sections"):
                return {"title": draft.get("title", title), "sections": draft.get("sections") or []}
        except Exception as exc:
            print(f"[draft] Azure OpenAI error: {exc} — trying Claude fallback")

    # ── Claude fallback ──────────────────────────────────────────────────────
    if claude_key:
        try:
            from llm.claude_http import call_claude_json
            schema_hint = "{draft:{title:string, sections:[{heading:string, paragraphs:[string]}]}}"
            data  = call_claude_json(api_key=claude_key, model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
                                     system=system, user_prompt=user_prompt,
                                     schema_hint=schema_hint, max_tokens=4096)
            draft = (data.get("draft") if isinstance(data, dict) else None) or data
            if isinstance(draft, dict) and draft.get("sections"):
                return {"title": draft.get("title", title), "sections": draft.get("sections") or []}
        except Exception as exc:
            print(f"[draft] Claude error: {exc} — using deterministic fallback")

    return _deterministic_draft(outline, passages, prefs)
