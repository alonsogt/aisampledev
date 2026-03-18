# Connector contract: sharepoint_source

Implements source connectors for ingestion.

## Inputs (conceptual)
- `source_spec`: describes SharePoint site/folder + auth/permissions

## Outputs (expected)
Each returned item should include:
- `file_id` (string)
- `url` (string)
- `filename` (string)
- `mime_type` (string)
- `last_modified` (string/ISO datetime)

## Notes
In v1 you can leave the connector stubbed and return empty lists while you focus on the contracts flow.

