from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


def _deterministic_outline(topic: str) -> Dict[str, Any]:
    return {
        "title": f"Ebook Outline: {topic}",
        "sections": [
            {"heading": "Introduction",   "bullets": ["Define the topic", "Explain why it matters", "Set expectations"]},
            {"heading": "Core Concepts",  "bullets": ["Key idea 1", "Key idea 2", "Practical example"]},
            {"heading": "Conclusion",     "bullets": ["Summary", "Next steps"]},
        ],
    }


def generate_outline(
    topic: str,
    passages: List[Dict[str, Any]],
    brief: Dict[str, str],
    preferences: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate ebook outline using Azure OpenAI (preferred) or Claude (fallback).
    Falls back to a deterministic outline if neither key is configured.

    Outline shape:
      { "title": str, "sections": [{"heading": str, "bullets": [str]}] }
    """
    azure_key      = os.getenv("AZURE_OPENAI_KEY", "")
    claude_key     = os.getenv("CLAUDE_API_KEY", "")

    what    = (brief or {}).get("what")    or ""
    who     = (brief or {}).get("who")     or ""
    never   = (brief or {}).get("never")   or ""
    success = (brief or {}).get("success") or ""

    prefs     = preferences or {}
    audience  = prefs.get("audience")  or ""
    tone      = prefs.get("tone")      or ""
    structure = prefs.get("structure") or ""

    passages_text = "\n\n".join(
        [f"- {p.get('title','')}\n  snippet: {p.get('snippet','')}" for p in (passages or [])[:5]]
    )

    system = (
        "You are a blueprint runtime assistant that generates an ebook outline.\n"
        "Follow the Brief constraints and use the provided passages to ground headings and bullets.\n"
        "Never fabricate citations; only use the passages provided.\n"
    )

    user_prompt = (
        f"Topic: {topic}\n\n"
        f"Brief.what: {what}\nBrief.who: {who}\nBrief.never: {never}\nBrief.success: {success}\n\n"
        f"Preferences (questionnaire-derived):\n"
        f"- audience: {audience}\n- tone: {tone}\n- structure: {structure}\n\n"
        f"Passages/examples:\n{passages_text}\n\n"
        "Return an outline with 5-7 sections.\n"
        "Each section must include 3-5 bullets that reflect the passages and the selected style/tone.\n"
        "Return JSON only, shape: {\"outline\":{\"title\":\"...\",\"sections\":[{\"heading\":\"...\",\"bullets\":[\"...\"]}]}}\n"
    )

    # ── Azure OpenAI (preferred) ─────────────────────────────────────────────
    if azure_key:
        try:
            from llm.azure_openai_http import call_azure_json
            data    = call_azure_json(system, user_prompt)
            outline = (data.get("outline") if isinstance(data, dict) else None) or data
            if isinstance(outline, dict) and outline.get("sections"):
                return {
                    "title":    outline.get("title", f"Ebook Outline: {topic}"),
                    "sections": outline.get("sections") or [],
                }
        except Exception as exc:
            print(f"[outline] Azure OpenAI error: {exc} — trying Claude fallback")

    # ── Claude fallback ──────────────────────────────────────────────────────
    if claude_key:
        try:
            from llm.claude_http import call_claude_json
            schema_hint = "{outline:{title:string, sections:[{heading:string, bullets:[string]}]}}"
            data    = call_claude_json(api_key=claude_key, model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
                                       system=system, user_prompt=user_prompt, schema_hint=schema_hint)
            outline = (data.get("outline") if isinstance(data, dict) else None) or data
            if isinstance(outline, dict) and outline.get("sections"):
                return {
                    "title":    outline.get("title", f"Ebook Outline: {topic}"),
                    "sections": outline.get("sections") or [],
                }
        except Exception as exc:
            print(f"[outline] Claude error: {exc} — using deterministic fallback")

    return _deterministic_outline(topic)
