# Agent Runtime Sample (Developer Starter)

This folder is a **sample runtime implementation** for the Blueprint JSON v2.0 you maintain in the tracker app.

It is intentionally **small, stubby, and contract-driven**:
- Each Python file contains a function that returns data in the exact shape described by the corresponding `contracts/*` file.
- Junior/low-code developers should implement the `TODO:` blocks, then set the related blueprint item `status` to `done`.

## How to use

1. Copy this folder into your runtime repo (or keep it as your runtime repo).
2. Implement the TODOs in:
   - `pipelines/*`
   - `connectors/*`
   - `services/*`
   - `flows/*`
   - `ui/screens/*`
3. Run the v1 eBook “hello world” locally from inside this folder:

```bash
cd agent-runtime-sample
python run_ebook_v1.py
```

## Runtime expectations (v1)

For the “eBook v1” scenario, your blueprint should describe this pipeline:
1. Retrieval (`services/retrieval/get_passages.py`)
2. Outline + draft generation (see:
   - `services/outline/generate_outline.py` (optional stub)
   - `services/outline/generate_draft.py` (used by blueprint step contract))
3. Docx output generation (`services/output/create_docx.py`)

If your contracts differ, update code to match contracts in `contracts/*`.

## Notes on dependencies

This sample uses Python’s standard library only. If you want real `.docx` output, install `python-docx`:

```bash
pip install python-docx
```

