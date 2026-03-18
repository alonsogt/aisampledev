# Connector contract: sharepoint_source (v1)

This contract matches the blueprint Notes for `connectors/sharepoint.py`.

## Purpose
Provide a list of SharePoint documents/files for ingestion.

## Inputs (conceptual)
- SharePoint base URL and target folder/path(s)
- permissions / identity info (who can read)

## Outputs (expected)
Each item should include:
- `file_id` (string)
- `url` (string)
- `filename` (string)
- `mime_type` (string)
- `last_modified` (string/ISO datetime)

In v1, you can leave the connector stubbed and return `[]`.

