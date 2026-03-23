from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, List, Optional


CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"


def _post_json(url: str, body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def call_claude(
    *,
    api_key: str,
    model: str,
    system: Optional[str],
    user_prompt: str,
    max_tokens: int = 1200,
    temperature: float = 0.2,
) -> str:
    """
    Minimal Claude Messages API client using only the Python stdlib.
    Returns the first text block from the response.
    """
    headers = {
        "content-type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    messages: List[Dict[str, Any]] = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    body: Dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }
    if system:
        body["system"] = system

    res = _post_json(CLAUDE_API_URL, body=body, headers=headers)

    # Normal response has `content: [{type:'text', text:'...'}]`
    content = res.get("content") or []
    for block in content:
        if block.get("type") == "text" and block.get("text") is not None:
            return str(block["text"])

    # Fallback (still return something useful)
    return str(res)


def call_claude_json(
    *,
    api_key: str,
    model: str,
    system: Optional[str],
    user_prompt: str,
    schema_hint: str,
    max_tokens: int = 1600,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    """
    Calls Claude and forces JSON-only output. Parses and returns JSON.

    schema_hint: short description like: "Return {outline:{title:string,sections:[{heading:string,bullets:[string]}]}}"
    """
    instruction = (
        "Return ONLY valid JSON. No markdown. No extra keys.\n"
        f"Expected shape: {schema_hint}\n"
    )
    prompt = instruction + "\nUser request:\n" + user_prompt

    text = call_claude(
        api_key=api_key,
        model=model,
        system=system,
        user_prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    # Some models wrap JSON in whitespace; strip and parse.
    raw = text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Best-effort: extract first {...} block.
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = raw[start : end + 1]
            return json.loads(candidate)
        raise


def load_claude_config() -> Dict[str, str]:
    """
    Uses env vars so you don't store secrets in code.
    """
    api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or ""
    model = os.getenv("CLAUDE_MODEL") or "claude-3-5-sonnet-20240620"
    return {"api_key": api_key, "model": model}

