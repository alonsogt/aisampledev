from typing import Dict, Any, List


def generate_outline(topic: str, passages: List[Dict[str, Any]], brief: Dict[str, str]) -> Dict[str, Any]:
    """
    Optional stub to make the v1 runner work end-to-end.

    Outline shape:
      {
        "title": str,
        "sections": [
          {"heading": str, "bullets": [str, ...]}
        ]
      }
    """
    # v1 demo: simple deterministic outline.
    return {
        "title": f"Ebook Outline: {topic}",
        "sections": [
            {"heading": "Introduction", "bullets": ["Define the topic", "Explain why it matters", "Set expectations"]},
            {"heading": "Core Concepts", "bullets": ["Key idea 1", "Key idea 2", "Practical example"]},
            {"heading": "Conclusion", "bullets": ["Summary", "Next steps"]},
        ],
    }

