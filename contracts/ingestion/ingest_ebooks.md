# Ingestion contract: ingest_ebooks

This contract defines what `pipelines/ingest_ebooks.py` must do (v1).

## Purpose
Turn source docs (PDF/DOCX/PPTX/etc.) into embedded chunks and write them into a retrieval index.

## Inputs
- `source_items[]`: list of items that represent docs to ingest.
- `index_name`: destination index name (default `ebooks_index`).

## Outputs
- `docs_seen` (int)
- `upserted_chunks` (int)
- `errors[]` (array of error objects/messages)

## Required index schema (must match retrieval)
Your retrieval step should be able to produce passages with:
- title (string)
- url (string)
- snippet (string)
- score (number)

## Notes
In v1, you can stub ingestion and use `data/sample_index.json` for retrieval.

