# Agent Runtime Sample

Azure AI Foundry deployment scripts, flow definitions, and services.
Everything here runs on Azure — no local servers, no ngrok.

## What's deployed to Azure

| Component | Where | What it does |
|---|---|---|
| `ebook-writer-agent` | Azure AI Foundry | Generates outlines and drafts, grounded in SharePoint |
| `ebook-intake-agent` | Azure AI Foundry | Conversationally collects topic, audience, tone, chapters |
| `ebook-conversation-flow` | Azure AI Foundry Workflow | Full conversation: questions → outline → approval → draft |
| `ebook-generate` | Azure AI Foundry Workflow | Sequential: outline then draft (no questions) |

## Folder structure

```
agent-runtime-sample/
  scripts/                  Deploy scripts — run once to set up Azure resources
    deploy_foundry_workflow.py          Deploy ebook-generate workflow
    deploy_ebook_conversation_workflow.py  Deploy ebook-conversation-flow to Foundry
    ebook-conversation-flow.yaml        Copy of / reference for Foundry workflow YAML (deploy script is canonical)
    create_foundry_agent.py             Create agents in Foundry
    setup_foundry_knowledge.py          Set up Foundry Knowledge (AI Search)

  flows/                    See flows/README.md — two different “flow” concepts
    ebook-flow.yaml         LOCAL ONLY: Python flow_engine / local-webagent (not Foundry)
    NEW-FLOW-TEMPLATE.yaml  Blank template for local flow_engine YAML
    README.md               Where the production flow lives (Foundry vs local YAML)
    HOW_TO_BUILD_A_FLOW.md  Guide for local flow_engine YAML

  services/                 Python services (used by deploy scripts)
    flow/flow_engine.py     YAML flow engine
    ingestion/              Document chunking + ingestion
    retrieval/              Passage retrieval
    outline/                Outline + draft generation
    logic/                  Branching, validation, fallback

  llm/                      Azure AI clients
    foundry_client.py       AIProjectClient wrapper
    azure_openai_http.py    Direct Azure OpenAI HTTP calls

  connectors/
    sharepoint.py           SharePoint document connector

  data/                     Grounding documents (uploaded to SharePoint/Foundry)
    AI-Agent-EBook-v1/      Brand guidelines, examples, research

  contracts/                JSON schemas for each service interface
```

## Run deploy scripts

```bash
# Set up your .env (copy from .env.example, fill in Azure credentials)
# Then deploy agents and workflows to Foundry:

pip install -r requirements.txt
az login

python scripts/deploy_foundry_workflow.py
python scripts/deploy_ebook_conversation_workflow.py
```

## Architecture

```
Azure Static Web Apps (index.html)
         |
Azure Functions (api/chat)
         |
Azure AI Foundry (ebook-conversation-flow)
         |
ebook-intake-agent + ebook-writer-agent
         |
SharePoint (grounding knowledge)
```

## Local development

See `../local-webagent/` for local dev tools (FastAPI + uvicorn + ngrok for Teams testing).
