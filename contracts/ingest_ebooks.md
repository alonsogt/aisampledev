# Ingestion contract: ingest_ebooks (v1)

This contract matches the blueprint Notes for `pipelines/ingest_ebooks.py`.

## Purpose
Ingest source documents (from SharePoint or another connector) and prepare them for retrieval.

## Inputs
- SharePoint folder(s) + file types (conceptual)
  - e.g. `[{ "sharepointPath": "...", "fileTypes": ["pdf","docx"] }]`
- `index_name` (string, optional; default: `ebooks_index`)

## Outputs
- `vectorIndex.indexName` (string)
- `docId` schema (conceptual)

In v1, you can stub the actual indexing and return a summary object.

