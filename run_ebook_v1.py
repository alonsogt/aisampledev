"""
v1 eBook demo runner.

This is a tiny "hello world" harness so developers can verify the pipeline wiring
before implementing real ingestion/retrieval/LLM calls.
"""

from __future__ import annotations

import os
import sys
import json

# Ensure imports like `from services...` work regardless of the cwd.
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agent.ebook_agent import run_ebook_agent


def _ask(prompt: str, default: str = "") -> str:
    val = input(f"{prompt}{' [' + default + ']' if default else ''}: ").strip()
    return val if val else default


def _ask_int(prompt: str, default: int) -> int:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        try:
            return int(raw)
        except ValueError:
            print("Please enter a valid integer.")


def _ask_csv(prompt: str, default: str = "") -> list[str]:
    raw = _ask(prompt, default).strip()
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def build_user_request_interactive() -> dict:
    print("=== v1 Interactive Questionnaire ===")
    topic = _ask("Topic", "AI governance for content teams")
    top_k = _ask_int("Retrieval top_k", 3)
    question_count = _ask_int("Question count (for UI simulation)", 7)

    style = _ask("Style", "professional")
    tone = _ask("Tone", "confident")
    audience = _ask("Audience", "content strategists and project managers")

    structure_options = _ask_csv(
        "Structure options (comma-separated)",
        "TOC-heavy, practical_checklists, examples",
    )

    return {
        "topic": topic,
        "top_k": top_k,
        "answers": {
            "questionCount": question_count,
            "style": style,
            "tone": tone,
            "audience": audience,
            "structureOptions": structure_options,
        },
    }

def _extract_sources_from_notes(notes: str) -> list[dict]:
    """
    Parses the BA/PM notes text format used by tracker app for grounding sources.

    Expected (roughly):
      kind: reference
      sources:
        - name: ...
          url: ...
          type: ...
          owner: ...
          notes: ...
    """
    if not notes:
        return []
    if "sources:" not in notes:
        return []

    lines = str(notes).splitlines()
    in_sources = False
    sources: list[dict] = []
    current: dict | None = None

    def lstrip_key(line: str) -> str:
        return line.lstrip()

    for line in lines:
        raw = line.rstrip("\n")
        stripped = lstrip_key(raw)
        if not stripped:
            continue

        if stripped.startswith("sources:"):
            in_sources = True
            continue

        if not in_sources:
            continue

        # End when other top-level blocks start.
        if stripped.startswith("usage:") or stripped.startswith("gaps:") or stripped.startswith("runbook:"):
            break

        if stripped.startswith("- name:"):
            if current:
                sources.append(current)
            current = {"name": stripped.split(":", 1)[1].strip()}
            continue

        if current is None:
            continue

        # Key-value lines inside a source item.
        if stripped.startswith("url:"):
            current["url"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("type:"):
            current["type"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("owner:"):
            current["owner"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("notes:"):
            current["notes"] = stripped.split(":", 1)[1].strip()

    if current:
        sources.append(current)

    return sources


def load_blueprint_for_runtime(blueprint_path: str) -> dict:
    """
    Loads a blueprint JSON (tracker data.json or sample_blueprint.json) and
    converts it into runtime inputs.

    Handles two source formats:
      1. sample_blueprint.json: item.notes = "local://data/sample_sources/file.txt"
         → source is the item itself, URL taken from notes field
      2. tracker data.json: item.notes = YAML-style sources: block
         → sources parsed from the notes text via _extract_sources_from_notes()

    Returns:
      - brief: blueprint.brief
      - grounding_sources: flattened list of {name, url, type, notes}
    """
    raw = open(blueprint_path, "r", encoding="utf-8").read()
    blueprint = json.loads(raw)

    brief = blueprint.get("brief") or {}
    grounding_sources: list[dict] = []

    for sec in blueprint.get("sections") or []:
        if sec.get("id") != "grounding":
            continue
        for item in sec.get("items") or []:
            notes = (item.get("notes") or "").strip()

            # Format 1: notes is a direct file/URL reference.
            if notes.startswith("local://") or notes.startswith("file://") or notes.startswith("http"):
                grounding_sources.append({
                    "name":  item.get("name") or "Source",
                    "url":   notes,
                    "type":  item.get("type") or "",
                    "owner": item.get("owner") or "",
                    "notes": item.get("desc") or "",
                })
                continue

            # Format 2: notes is a YAML-style sources: block (tracker app format).
            parsed = _extract_sources_from_notes(notes)
            if parsed:
                grounding_sources.extend(parsed)

    return {"brief": brief, "grounding_sources": grounding_sources}


def main() -> None:
    interactive = "--interactive" in sys.argv
    blueprint_path = None
    if "--blueprint" in sys.argv:
        idx = sys.argv.index("--blueprint")
        if idx + 1 < len(sys.argv):
            blueprint_path = sys.argv[idx + 1]

    user_request = build_user_request_interactive() if interactive else {
        "topic": "AI governance for content teams",
        "top_k": 3,
        "answers": {
            "questionCount": 7,
            "style": "professional",
            "tone": "confident",
            "audience": "content strategists and project managers",
            "structureOptions": ["TOC-heavy", "practical_checklists", "examples"],
        },
    }

    if blueprint_path:
        loaded = load_blueprint_for_runtime(blueprint_path)
        user_request["brief"] = loaded["brief"]
        user_request["grounding_sources"] = loaded["grounding_sources"]
        if "--debugBlueprint" in sys.argv:
            gs = user_request.get("grounding_sources") or []
            print(f"[debugBlueprint] brief.what_len={len(user_request['brief'].get('what',''))}")
            print(f"[debugBlueprint] grounding_sources_count={len(gs)}")
            if gs:
                print("[debugBlueprint] first_source=", gs[0])

    result = run_ebook_agent(user_request)
    print("\n=== v1 result ===")
    print("outline_title:", result["outline"]["title"])
    print("outline_sections:", [s["heading"] for s in result["outline"]["sections"]])
    print("draft_headings:", [s["heading"] for s in result["draft"]["sections"]])
    print("docx_output:", result["doc_url"])


if __name__ == "__main__":
    main()

