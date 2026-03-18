# Pipelines

Python “pipeline” entrypoints are thin orchestrators that:
1. read configs / source specs
2. call ingestion/retrieval/logic/services
3. write outputs + stats

In v1, this sample only includes a stub ingestion pipeline.

