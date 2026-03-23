from __future__ import annotations

import json
import os
import re
import urllib.request
from typing import Any, Dict, Optional


def _get_config() -> Dict[str, str]:
    return {
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/"),
        "key":      os.getenv("AZURE_OPENAI_KEY", ""),
        "deploy":   os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        "version":  os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    }


def call_azure(
    system: str,
    user_prompt: str,
    *,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """
    Call Azure OpenAI chat completions and return the response text.
    Reads AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT from env.
    """
    cfg = _get_config()
    if not cfg["endpoint"] or not cfg["key"]:
        raise EnvironmentError(
            "AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY must be set in .env"
        )

    url = (
        f"{cfg['endpoint']}/openai/deployments/{cfg['deploy']}"
        f"/chat/completions?api-version={cfg['version']}"
    )

    payload = json.dumps({
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens":  max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "api-key": cfg["key"],
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    return body["choices"][0]["message"]["content"]


def call_azure_json(
    system: str,
    user_prompt: str,
    *,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> Any:
    """
    Same as call_azure() but parses and returns the first JSON object in the response.
    Falls back to returning the raw text if no JSON block is found.
    """
    text = call_azure(system, user_prompt, temperature=temperature, max_tokens=max_tokens)
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return text
