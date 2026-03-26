# Contracts

Expected input/output shapes for pipeline steps. Blueprint `Notes` can reference these paths, e.g. `contract: repo=agent-runtime path=contracts/output/create_docx.json`.

---

## Connector: `sharepoint_source` (v1)

Matches `connectors/sharepoint.py`.

**Purpose:** List SharePoint documents for ingestion.

**Outputs per item:** `file_id`, `url`, `filename`, `mime_type`, `last_modified` (ISO). v1 may return `[]`.

---

## Ingestion: `ingest_ebooks` (v1)

**Purpose:** Ingest documents and prepare for retrieval.

**Inputs:** SharePoint folder(s) + file types; optional `index_name` (default `ebooks_index`).

**Outputs:** `vectorIndex.indexName`, `docId` schema (conceptual). v1 may stub.

---

## Logic: completion criteria

**Purpose:** Define “done” after drafting/review.

**Inputs:** `draft`, optional rubric results. **Outputs:** `done` or `needs_review`. v1 may be a placeholder.
