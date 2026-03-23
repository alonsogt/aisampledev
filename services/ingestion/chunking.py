from __future__ import annotations

import re
from typing import List


def chunk_text(
    text: str,
    *,
    chunk_words: int = 180,
    overlap_words: int = 40,
) -> List[str]:
    """
    Split text into overlapping word-count chunks.

    chunk_words:   target words per chunk (default 180 ~ 1 short paragraph)
    overlap_words: words to repeat at the start of the next chunk for context
    """
    t = (text or "").strip()
    if not t:
        return []

    words = re.split(r"\s+", t)
    n = len(words)
    if n == 0:
        return []

    step = max(1, chunk_words - overlap_words)
    chunks: List[str] = []
    i = 0
    while i < n:
        part = words[i : i + chunk_words]
        chunk = " ".join(part).strip()
        if chunk:
            chunks.append(chunk)
        i += step

    return chunks
