from __future__ import annotations

from typing import Any, Dict
from pathlib import Path


def create_pdf(docx_or_url: str) -> str:
    """
    Stub: v1 returns a placeholder local path.
    TODO: implement real PDF conversion.
    """
    safe = "document"
    p = Path(__file__).resolve().parents[2]
    out_path = p / "agent-runtime-sample_output.pdf"

    # v1: create a placeholder PDF-like file (text content).
    out_path.write_text(
        "PDF placeholder (v1 sample)\n\n"
        f"input: {docx_or_url}\n",
        encoding="utf-8",
    )
    return out_path.as_uri()

