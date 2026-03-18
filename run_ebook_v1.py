"""
v1 eBook demo runner.

This is a tiny "hello world" harness so developers can verify the pipeline wiring
before implementing real ingestion/retrieval/LLM calls.
"""

from __future__ import annotations

import os
import sys

# Ensure imports like `from services...` work regardless of the cwd.
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agent.ebook_agent import run_ebook_agent


def main() -> None:
    user_request = {
        "topic": "AI governance for content teams",
        "top_k": 3,
    }

    result = run_ebook_agent(user_request)
    print("\n=== v1 result ===")
    print("outline_title:", result["outline"]["title"])
    print("draft_headings:", [s["heading"] for s in result["draft"]["sections"]])
    print("docx_output:", result["doc_url"])


if __name__ == "__main__":
    main()

