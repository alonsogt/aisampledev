from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from services.ingestion.chunking import chunk_text
from services.ingestion.download_and_extract import download_and_extract


# Cap chunks per source to keep the index fast for v1.
MAX_CHUNKS_PER_SOURCE = 50


def build_latest_index(
    sources: List[Dict[str, Any]],
    *,
    out_path: Optional[str] = None,
    chunk_words: int = 180,
    overlap_words: int = 40,
    verbose: bool = False,
) -> str:
    """
    For each source in the blueprint's grounding list:
      1. Download the file (if a real URL + token is available).
      2. Extract plaintext.
      3. Chunk the text.
      4. Write all chunks to `data/latest_index.json`.

    If download fails or token is not set, falls back to using
    `sources[].notes` as the snippet text so the pipeline always has
    something to retrieve from.

    Returns the path to the written index file.
    """
    repo_root = Path(__file__).resolve().parents[3]
    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    if not out_path:
        out_path = str(data_dir / "latest_index.json")

    idx: Dict[str, Any] = {
        "indexName": "blueprint_latest",
        "sourceCount": len(sources or []),
        "createdAt": datetime.datetime.utcnow().isoformat(),
        "passages": [],
    }

    for src in (sources or []):
        name = str(src.get("name") or "Source")
        url  = str(src.get("url")  or "")
        typ  = str(src.get("type") or "")

        if verbose:
            print(f"  [ingest] {name} ({typ}) -> {url[:80]}...")

        extracted = download_and_extract(src)
        text = extracted.get("text") or ""
        err  = extracted.get("download_error")

        if err and verbose:
            print(f"    [warn] download/extract: {err}")

        if not text.strip():
            # Absolute last resort: empty placeholder so pipeline doesn't break.
            text = f"Source: {name}"

        chunks = chunk_text(text, chunk_words=chunk_words, overlap_words=overlap_words)
        if not chunks:
            chunks = [text.strip()]

        for i, ch in enumerate(chunks[:MAX_CHUNKS_PER_SOURCE]):
            idx["passages"].append(
                {
                    "title": name,
                    "url":   url,
                    "type":  typ,
                    "chunk_no": i + 1,
                    "snippet":  ch,
                }
            )

    Path(out_path).write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")

    if verbose:
        print(f"  [ingest] wrote {len(idx['passages'])} passages -> {out_path}")

    return out_path
