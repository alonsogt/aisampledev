from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_passages(
    query: str,
    top_k: int = 5,
    sources: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Contract: contracts/retrieval/get_passages.json
    Returns passages[] with: title, url, snippet, score

    Priority order:
    1. latest_index.json  (built by build_index.py from real blueprint sources)
    2. sample_index.json  (static demo data, shipped with the repo)
    3. Inline source notes from the blueprint (last resort / demo fallback)
    """
    sources = sources or []
    repo_root = Path(__file__).resolve().parents[2]

    # ------------------------------------------------------------------
    # Try the live index first, then fall back to the shipped sample.
    # ------------------------------------------------------------------
    passages: List[Dict[str, Any]] = []

    for idx_name in ("latest_index.json", "sample_index.json"):
        idx_path = repo_root / "data" / idx_name
        if not idx_path.exists():
            continue

        try:
            raw = json.loads(idx_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        # latest_index.json uses flat "passages" list (output of build_index.py).
        flat_passages = raw.get("passages") or []
        if flat_passages:
            passages = [
                {
                    "title":   p.get("title") or "Source",
                    "url":     p.get("url") or "",
                    "snippet": p.get("snippet") or "",
                    "score":   0.0,
                }
                for p in flat_passages
            ]
            break

        # sample_index.json has a nested "ebooks_index.documents" structure.
        docs = (raw.get("ebooks_index") or {}).get("documents") or []
        if docs:
            for d in docs:
                title = d.get("title") or "Untitled"
                url   = d.get("source_url") or ""
                for ch in d.get("chunks") or []:
                    passages.append(
                        {
                            "title":   title,
                            "url":     url,
                            "snippet": ch.get("chunk_text") or "",
                            "score":   0.0,
                        }
                    )
            break

    # ------------------------------------------------------------------
    # Score passages by keyword overlap with the query.
    # ------------------------------------------------------------------
    q = (query or "").strip().lower()
    q_tokens = {t for t in re.split(r"\W+", q) if len(t) > 2}

    for p in passages:
        text = (p["title"] + " " + p["snippet"]).lower()
        overlap = sum(1 for t in q_tokens if t in text) if q_tokens else 0
        p["score"] = round(0.25 + min(overlap, 5) * 0.15, 3)

    passages.sort(key=lambda x: x.get("score", 0), reverse=True)

    k = max(1, int(top_k or 1))
    top = passages[:k]

    # ------------------------------------------------------------------
    # Last-resort fallback: use inline notes from blueprint sources.
    # ------------------------------------------------------------------
    if not top and sources:
        for s in sources[:k]:
            top.append(
                {
                    "title":   s.get("name") or "Source",
                    "url":     s.get("url")  or "",
                    "snippet": s.get("notes") or "",
                    "score":   0.5,
                }
            )

    return top
