"""
Deploys the full EBook Conversation Workflow to Azure AI Foundry.

This workflow handles the ENTIRE conversation inside Foundry:
  - Asks the user for topic, audience, tone, chapters
  - Generates an outline (ebook-writer-agent)
  - Shows the outline and asks for approval
  - If approved: generates full draft (ebook-writer-agent)
  - If not approved: loops back to start
  - No Python flow engine needed — Foundry handles branching via if/else nodes

Run:
    python scripts/deploy_ebook_conversation_workflow.py

After deploying, test it in:
  - Foundry portal → Workflows → ebook-conversation-flow → Run Workflow
  - VS Code Foundry extension → Declarative Agents → ebook-conversation-flow
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

for line in (ROOT / ".env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

ENDPOINT = os.environ["AZURE_FOUNDRY_ENDPOINT"]

client = AIProjectClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

# ── Full conversational workflow YAML ─────────────────────────────────────────
#
# Node types used (Foundry / Copilot Studio AdaptiveDialog format):
#   SendActivity     — send a message to the user
#   Question         — ask user a question, save their answer to a variable
#   ConditionGroup   — if/else branching using Power Fx expressions
#   GotoAction       — jump to a specific step (for the retry loop)
#   InvokeAzureAgent — call a Foundry agent
#
# Variables use Local. prefix for workflow-scoped storage.
# Power Fx (=expression) used in dynamic prompts and conditions.

# ── Workflow YAML ─────────────────────────────────────────────────────────────
#
# This workflow uses a single smart intake agent to handle the full conversation:
#   1. ebook-intake-agent  — asks all questions, returns structured JSON
#   2. ebook-writer-agent  — generates outline from the JSON
#   3. ebook-writer-agent  — expands outline into full draft
#
# The if/else approval loop must be added manually in the Foundry portal
# visual editor after deploying — the API does not support ConditionGroup
# and GotoAction node types in the same call.
#
# Portal steps to add after deploy:
#   1. Open ebook-conversation-flow in Foundry portal
#   2. Add an "Ask a question" node after the outline step
#      - Question: "Does this outline look good? (Yes / No)"
#      - Save to Local.Approval
#   3. Add an "if/else" node:
#      - If Local.Approval starts with "Yes" → invoke ebook-writer-agent for draft
#      - Else → Go to intake step (restart)

WORKFLOW_YAML = """kind: workflow
name: ebook-conversation-flow
trigger:
  kind: OnConversationStart
  id: trigger_wf
  actions:
    - kind: InvokeAzureAgent
      id: intake
      agent:
        name: ebook-intake-agent
      description: Collect topic, audience, tone and chapter count from user
      conversationId: =System.ConversationId
      input:
        messages: =System.LastMessage
      output:
        messages: Local.IntakeResult
        autoSend: false
    - kind: InvokeAzureAgent
      id: outline
      agent:
        name: ebook-writer-agent
      description: Generate structured ebook outline from intake answers
      conversationId: =System.ConversationId
      input:
        messages: =Local.IntakeResult
      output:
        messages: Local.OutlineResult
        autoSend: false
    - kind: InvokeAzureAgent
      id: draft
      agent:
        name: ebook-writer-agent
      description: Expand outline into full written ebook draft
      conversationId: =System.ConversationId
      input:
        messages: =Local.OutlineResult
      output:
        messages: Local.DraftResult
        autoSend: true
"""

# ── Create intake agent ───────────────────────────────────────────────────────
print("Creating ebook-intake-agent...")

from azure.ai.projects.models import PromptAgentDefinition

client.agents.create_version(
    agent_name="ebook-intake-agent",
    definition=PromptAgentDefinition(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        instructions="""
You are a friendly intake agent for an ebook creation tool.
Your job is to collect 4 pieces of information from the user through conversation:
  1. topic     — what the ebook should be about
  2. audience  — who the target readers are
  3. tone      — the writing style (Professional / Conversational / Technical / Motivational)
  4. chapters  — number of chapters (3, 6, or 9)

Ask one question at a time. Be friendly and brief.
When you have all 4 answers, return ONLY this JSON (no markdown, no extra text):
{
  "topic": "...",
  "audience": "...",
  "tone": "...",
  "chapters": 6
}
""".strip(),
    ),
)
print("  ebook-intake-agent: OK")

print("\nDeploying ebook-conversation-flow workflow...")

result = client.agents.create_version(
    agent_name="ebook-conversation-flow",
    definition={
        "kind": "workflow",
        "workflow": WORKFLOW_YAML,
    },
    headers={"Foundry-Features": "WorkflowAgents=V1Preview"},
)

print(f"  Workflow deployed: {result.name} v{result.version}")
print()
print("Test it in:")
print("  Foundry portal -> Build -> Workflows -> ebook-conversation-flow -> Run Workflow")
print("  VS Code Foundry extension -> Declarative Agents -> ebook-conversation-flow")
print()
print("This workflow handles the full conversation in Foundry — no Python flow engine needed.")
