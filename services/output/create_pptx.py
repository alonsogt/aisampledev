from __future__ import annotations

from typing import Dict, Any
from pathlib import Path


def create_pptx(outline: Dict[str, Any], slides_data: Dict[str, Any]) -> str:
    """
    Stub: return local path for v1.
    TODO: implement real PPTX generation.
    """
    topic = (slides_data or {}).get("topic") or outline.get("title") or "presentation"
    safe = str(topic).replace(" ", "_").replace("/", "_")
    out_path = Path(__file__).resolve().parents[2] / f"agent-runtime-sample_output_{safe}.pptx"

    # v1: write a placeholder "pptx" file so downstream wiring works.
    out_path.write_text(
        "PPTX placeholder (v1 sample)\n\n"
        f"title: {outline.get('title','')}\n"
        f"slides_data: {slides_data}\n",
        encoding="utf-8",
    )

    return out_path.as_uri()

