from __future__ import annotations

import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# SharePoint URL helpers
# ---------------------------------------------------------------------------

def _is_sharepoint_url(url: str) -> bool:
    return ".sharepoint.com" in url.lower()


def _parse_sharepoint_url(url: str) -> Tuple[str, str]:
    """
    Returns (site_root, server_relative_path) from any SharePoint URL.

    Handles both:
      - Direct file paths:
          https://tenant.sharepoint.com/sites/MySite/Shared Documents/file.pdf
      - Web viewer / AllItems URLs with ?id= param:
          https://tenant.sharepoint.com/.../AllItems.aspx?id=%2Fsites%2F...%2Ffile.pdf
    """
    parsed = urllib.parse.urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"   # https://tenant.sharepoint.com

    # Web viewer URL — extract server-relative path from ?id= query param.
    qs = urllib.parse.parse_qs(parsed.query)
    if "id" in qs:
        server_rel = urllib.parse.unquote(qs["id"][0])
        # Derive site root from server-relative path (first 3 segments: /sites/Name).
        parts = server_rel.lstrip("/").split("/")
        if len(parts) >= 2 and parts[0].lower() == "sites":
            site_root = f"{origin}/sites/{parts[1]}"
        else:
            site_root = origin
        return site_root, server_rel

    # Direct file path — the path IS the server-relative path.
    path = urllib.parse.unquote(parsed.path)
    parts = path.lstrip("/").split("/")
    if len(parts) >= 2 and parts[0].lower() == "sites":
        site_root = f"{origin}/sites/{parts[1]}"
    else:
        site_root = origin
    return site_root, path


def _to_sharepoint_rest_url(url: str) -> str:
    """
    Convert any SharePoint URL to the REST API download endpoint.
    /_api/web/GetFileByServerRelativeUrl('...')/$value
    """
    site_root, server_rel = _parse_sharepoint_url(url)
    encoded = urllib.parse.quote(server_rel)
    return f"{site_root}/_api/web/GetFileByServerRelativeUrl('{encoded}')/$value"


# ---------------------------------------------------------------------------
# Token management — auto-refresh via Azure CLI when needed
# ---------------------------------------------------------------------------

_token_cache: Dict[str, Any] = {}   # {"token": str, "expires_at": float}


def _get_sharepoint_token(sharepoint_host: str) -> Optional[str]:
    """
    Return a valid Bearer token for SharePoint.
    Priority:
      1. SHAREPOINT_BEARER_TOKEN env var (use as-is, assumed valid)
      2. Auto-fetch from Azure CLI (az account get-access-token)
      3. None — caller must handle graceful fallback
    """
    # Env var takes priority (user can always override).
    env_token = os.getenv("SHAREPOINT_BEARER_TOKEN", "").strip()
    if env_token:
        return env_token

    resource = f"https://{sharepoint_host}"
    cached = _token_cache.get(resource)
    if cached and cached["expires_at"] > time.time() + 60:
        return cached["token"]

    # Try to fetch via az CLI (works if user is logged in via `az login`).
    az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    try:
        result = subprocess.run(
            [az_cmd, "account", "get-access-token",
             "--resource", resource,
             "--query", "accessToken",
             "-o", "tsv"],
            capture_output=True, text=True, timeout=20
        )
        token = result.stdout.strip()
        if token and result.returncode == 0:
            _token_cache[resource] = {
                "token": token,
                "expires_at": time.time() + 3500,  # tokens last ~1 hour
            }
            return token
    except Exception:
        pass

    return None


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def _download_bytes(
    url: str,
    *,
    bearer_token: Optional[str] = None,
    timeout_s: int = 60,
    max_retries: int = 2,
) -> bytes:
    headers: Dict[str, str] = {"Accept": "*/*"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    last_exc: Exception = RuntimeError("no attempts made")
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            last_exc = exc
            # 401/403: no point retrying with same token.
            if exc.code in (401, 403):
                raise
            if attempt < max_retries:
                time.sleep(1.5 * (attempt + 1))
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries:
                time.sleep(1.5 * (attempt + 1))
    raise last_exc


def _download_sharepoint(url: str, timeout_s: int = 60) -> bytes:
    """
    Download a SharePoint file via REST API with auto-token acquisition.
    Falls back to direct URL if REST conversion fails.
    """
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc   # e.g. bridgepartnersconsulting.sharepoint.com
    token = _get_sharepoint_token(host)

    rest_url = _to_sharepoint_rest_url(url)

    try:
        return _download_bytes(rest_url, bearer_token=token, timeout_s=timeout_s)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            # Token might be for wrong audience — try direct URL as last resort.
            return _download_bytes(url, bearer_token=token, timeout_s=timeout_s)
        raise


# ---------------------------------------------------------------------------
# Type detection
# ---------------------------------------------------------------------------

def _detect_type(source: Dict[str, Any]) -> str:
    t = (source.get("type") or "").strip().lower()
    if t and t not in {"other", "folder", ""}:
        return t
    path = str(source.get("url") or "")
    m = re.search(r"\.([a-zA-Z0-9]+)(?:\?|#|$)", path)
    if m:
        return m.group(1).lower()
    return "other"


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def _extract_docx(data: bytes) -> str:
    try:
        from docx import Document  # type: ignore
    except ImportError:
        return ""
    tmp = Path(os.getenv("TMP") or os.getenv("TMPDIR") or ".") / "_rag_tmp.docx"
    tmp.write_bytes(data)
    try:
        doc = Document(str(tmp))
        return "\n".join(p.text.strip() for p in doc.paragraphs if (p.text or "").strip())
    finally:
        try:
            tmp.unlink()
        except Exception:
            pass


def _extract_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return ""
    tmp = Path(os.getenv("TMP") or os.getenv("TMPDIR") or ".") / "_rag_tmp.pdf"
    tmp.write_bytes(data)
    try:
        reader = PdfReader(str(tmp))
        parts = []
        for page in reader.pages:
            try:
                txt = (page.extract_text() or "").strip()
                if txt:
                    parts.append(txt)
            except Exception:
                continue
        return "\n\n".join(parts)
    finally:
        try:
            tmp.unlink()
        except Exception:
            pass


def _extract_text(data: bytes, source_type: str) -> str:
    if source_type in {"docx", "doc"}:
        return _extract_docx(data)
    if source_type == "pdf":
        return _extract_pdf(data)
    try:
        return data.decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def download_and_extract(source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Download a source and extract plaintext.

    Authentication:
      - SharePoint URLs: auto-fetches Bearer token via Azure CLI or
        uses SHAREPOINT_BEARER_TOKEN env var.
      - Other URLs: plain HTTP GET.

    Always returns a dict with:
      text           - extracted text (falls back to source.notes on failure)
      bytes_len      - bytes downloaded (0 on failure)
      download_error - error description or None
    """
    url = str(source.get("url") or "").strip()

    # Skip non-downloadable entries.
    if not url or url.startswith("repo="):
        return {
            "text": str(source.get("notes") or ""),
            "bytes_len": 0,
            "download_error": "skipped (no downloadable URL)",
        }

    # Local file path — read directly from disk.
    if url.startswith("file://") or url.startswith("local://"):
        local_path = url.replace("file:///", "").replace("file://", "").replace("local://", "")
        # Resolve relative to agent-runtime-sample root.
        if not Path(local_path).is_absolute():
            local_path = str(Path(__file__).resolve().parents[2] / local_path)
        local_type = _detect_type({"url": local_path, "type": source.get("type") or ""})
        try:
            data = Path(local_path).read_bytes()
            text = _extract_text(data, local_type)
            if not text.strip():
                text = str(source.get("notes") or "")
            return {"text": text, "bytes_len": len(data), "download_error": None}
        except Exception as exc:
            return {
                "text": str(source.get("notes") or ""),
                "bytes_len": 0,
                "download_error": f"local file error: {exc}",
            }

    source_type = _detect_type(source)

    # Skip folder-type entries — no file to download.
    if source_type == "folder":
        return {
            "text": str(source.get("notes") or ""),
            "bytes_len": 0,
            "download_error": "skipped (folder — no single file to download)",
        }

    try:
        if _is_sharepoint_url(url):
            data = _download_sharepoint(url)
        else:
            data = _download_bytes(url)
    except Exception as exc:
        return {
            "text": str(source.get("notes") or ""),
            "bytes_len": 0,
            "download_error": str(exc),
        }

    text = _extract_text(data, source_type)
    if not text.strip():
        text = str(source.get("notes") or "")

    return {"text": text, "bytes_len": len(data), "download_error": None}
