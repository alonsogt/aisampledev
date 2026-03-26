from typing import Dict, Any, List


def list_sharepoint_files(source_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Stub connector for SharePoint-like sources.

    Contract summary: see contracts/README.md (Connector: sharepoint_source)

    Expected output items should include:
      - file_id
      - url
      - filename
      - mime_type
      - last_modified
    """
    return []

