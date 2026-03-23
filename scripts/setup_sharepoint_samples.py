"""
Creates "Samples Library" folder in SharePoint and uploads all sample source files.
Prints the direct download URL for each file so you can paste them into data.json.

Usage:
    python scripts/setup_sharepoint_samples.py

Requirements:
    - Logged in via `az login` (already done)
    - Access to the SharePoint site below
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
SHAREPOINT_SITE  = "https://bridgepartnersconsulting.sharepoint.com/sites/GTMTechAI-GTMTechandAITeam-Developers"
LIBRARY_NAME     = "Shared Documents"
FOLDER_PATH      = "Samples Library"          # will be created if it doesn't exist
SITE_REL_BASE    = "/sites/GTMTechAI-GTMTechandAITeam-Developers"

# Sample files to upload (relative to this script's parent = agent-runtime-sample/)
SAMPLE_FILES = [
    ("data/sample_sources/StyleGuide-2024.txt",    "StyleGuide-2024.txt",    "txt"),
    ("data/sample_sources/EBook-Example-1.txt",    "EBook-Example-1.txt",    "txt"),
    ("data/sample_sources/EBook-Example-2.txt",    "EBook-Example-2.txt",    "txt"),
    ("data/sample_sources/SME-Transcript-1.txt",   "SME-Transcript-1.txt",   "txt"),
    ("data/sample_sources/Generic-Reference.txt",  "Generic-Reference.txt",  "txt"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

AZ_CMD = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"


def get_token(resource: str) -> str:
    result = subprocess.run(
        [AZ_CMD, "account", "get-access-token", "--resource", resource, "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, timeout=30, shell=False
    )
    token = result.stdout.strip()
    if not token or result.returncode != 0:
        raise RuntimeError(f"Could not get token for {resource}.\nRun `az login` first.\n{result.stderr}")
    return token


def get_form_digest(site: str, token: str) -> str:
    """Fetch the SharePoint form digest value required for write operations."""
    url = f"{site}/_api/contextinfo"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json;odata=verbose",
        "Content-Length": "0",
    }
    req = urllib.request.Request(url, data=b"", headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["d"]["GetContextWebInformation"]["FormDigestValue"]


def sp_request(method: str, url: str, token: str, digest: str = "", body: bytes = b"", content_type: str = "application/json;odata=verbose") -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json;odata=verbose",
        "Content-Type": content_type,
    }
    if digest:
        headers["X-RequestDigest"] = digest
    req = urllib.request.Request(url, data=body or None, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {exc.code} {exc.reason} — {url}\n{body_text[:400]}") from exc


def ensure_folder(site: str, library: str, folder: str, token: str, digest: str = "") -> str:
    """
    Creates folder inside library if it doesn't exist.
    Returns server-relative path of the folder.
    """
    parsed     = urllib.parse.urlparse(site)
    site_rel   = parsed.path.rstrip("/")                     # /sites/GTMTechAI-...
    server_rel = f"{site_rel}/{library}/{folder}"
    encoded    = urllib.parse.quote(server_rel)

    # Check if folder exists.
    check_url = f"{site}/_api/web/GetFolderByServerRelativeUrl('{encoded}')"
    try:
        sp_request("GET", check_url, token)
        print(f"  [folder] already exists: {server_rel}")
        return server_rel
    except RuntimeError:
        pass  # folder doesn't exist — create it

    # Create folder.
    create_url = f"{site}/_api/web/folders"
    payload    = json.dumps({
        "__metadata": {"type": "SP.Folder"},
        "ServerRelativeUrl": server_rel,
    }).encode("utf-8")
    sp_request("POST", create_url, token, digest=digest, body=payload)
    print(f"  [folder] created: {server_rel}")
    return server_rel


def upload_file(site: str, folder_server_rel: str, filename: str, data: bytes, token: str, digest: str = "") -> str:
    """
    Uploads file to SharePoint folder. Returns the server-relative URL of the file.
    """
    encoded_folder = urllib.parse.quote(folder_server_rel)
    encoded_name   = urllib.parse.quote(filename)
    upload_url     = (
        f"{site}/_api/web/GetFolderByServerRelativeUrl('{encoded_folder}')"
        f"/Files/add(url='{encoded_name}',overwrite=true)"
    )
    sp_request("POST", upload_url, token, digest=digest, body=data, content_type="application/octet-stream")
    return f"{folder_server_rel}/{filename}"


def get_direct_url(site: str, server_rel: str) -> str:
    """Returns the direct browser/download URL for a file."""
    parsed = urllib.parse.urlparse(site)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return origin + urllib.parse.quote(server_rel)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    root = Path(__file__).resolve().parent.parent   # agent-runtime-sample/

    print("=== SharePoint Sample Setup ===")
    print(f"Site:   {SHAREPOINT_SITE}")
    print(f"Folder: {LIBRARY_NAME}/{FOLDER_PATH}")
    print()

    # Get token.
    print("Fetching SharePoint token via Azure CLI...")
    sp_host    = urllib.parse.urlparse(SHAREPOINT_SITE).netloc
    token      = get_token(f"https://{sp_host}")
    print("  Token acquired.\n")

    # Get form digest (required for all write operations).
    print("Fetching SharePoint form digest...")
    digest = get_form_digest(SHAREPOINT_SITE, token)
    print("  Form digest acquired.\n")

    # Ensure folder exists.
    print("Ensuring folder exists...")
    folder_rel = ensure_folder(SHAREPOINT_SITE, LIBRARY_NAME, FOLDER_PATH, token, digest)
    print()

    # Upload files.
    results = []
    print("Uploading files...")
    for local_rel, sp_filename, _ in SAMPLE_FILES:
        local_path = root / local_rel
        if not local_path.exists():
            print(f"  [skip] not found: {local_path}")
            continue

        data = local_path.read_bytes()
        server_rel = upload_file(SHAREPOINT_SITE, folder_rel, sp_filename, data, token, digest)
        direct_url = get_direct_url(SHAREPOINT_SITE, server_rel)
        print(f"  [ok] {sp_filename}")
        print(f"       {direct_url}")
        results.append({"name": sp_filename, "url": direct_url, "server_rel": server_rel})

    # Write results to a JSON file for easy copy-paste.
    out_path = root / "data" / "sharepoint_sources.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"\n=== Done ===")
    print(f"URLs saved to: {out_path}")
    print("\nPaste these URLs into your blueprint sources to enable real SharePoint RAG.\n")
    for r in results:
        print(f"  {r['name']}")
        print(f"  {r['url']}\n")


if __name__ == "__main__":
    main()
