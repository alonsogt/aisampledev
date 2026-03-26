# Flow definitions — two different things

Do **not** assume one YAML file in this folder is “the” production flow.

## Production (Static Web App → Azure AI Foundry)

The **canonical** conversational flow for the hosted ebook experience is **`ebook-conversation-flow`** inside your **Azure AI Foundry** project (`agarcia-projectaif`).

- **Authoritative copy:** the workflow stored in Foundry (portal **Build → Workflows**, or API).
- **How it gets there:** `scripts/deploy_ebook_conversation_workflow.py` pushes YAML embedded in that script (and a copy/reference lives as `scripts/ebook-conversation-flow.yaml` next to it).
- **To change the live flow:** edit in the Foundry UI, or change the script / YAML there and **re-run the deploy script** — not by editing `ebook-flow.yaml` in this folder.

The chat UI’s Azure Function calls Foundry’s Responses API with `agent_reference` → **`ebook-conversation-flow`**. Nothing in `ebook-flow.yaml` is used for that path.

## Local only (`ebook-flow.yaml` in this folder)

**`ebook-flow.yaml`** is a **custom** step format consumed by **`services/flow/flow_engine.py`** — used for **local** tooling (e.g. `local-webagent/`, Teams bot samples). It is **not** Foundry workflow YAML and **is not** what Foundry executes in the cloud.

Use it when you are running the Python flow engine locally. For Foundry-only behavior, ignore this file for production and work in Foundry (or the deploy script above).

## Docs

- `HOW_TO_BUILD_A_FLOW.md` — explains the **local** YAML shape for `flow_engine.py`. For Foundry workflow authoring, use the Foundry portal or the deploy scripts under `scripts/`.
