# How to Build a New Agent Flow

> **Where does the *production* flow live?**  
> On **Azure AI Foundry** as **`ebook-conversation-flow`**.  
> This file describes the **local** YAML format for `flow_engine.py` only (e.g. Teams bot). For Foundry, use the portal or `scripts/deploy_ebook_conversation_workflow.py`.

### Local flow engine only: edit the YAML, restart the server — done.

---

## What is a Flow?

A flow is a conversation script for your AI agent.  
You define:
- **What questions to ask** the user
- **What options** to give them (buttons)
- **When to generate** AI content
- **Where to go next** based on their answer

The agent follows this script automatically. You never touch Python.

---

## The 4 Step Types

### 1. `ask` — Ask the user a question

```yaml
- id: my_question
  type: ask
  question: "What do you need help with?"
  hint: "e.g. onboarding, compliance, training"
  save_as: user_need
```

- `question` — what the agent says
- `hint` — small grey text under the question (optional)
- `save_as` — the name you'll use to reference their answer later
- `options` — if you want buttons instead of free text (optional):

```yaml
  options:
    - Option A
    - Option B
    - Option C
```

---

### 2. `generate` — Ask the AI to produce something

```yaml
- id: create_document
  type: generate
  action: outline        # or: draft
  message: "Creating your document, please wait..."
  on_complete:
    show: outline        # or: draft_preview
    next: review_step
```

- Use `action: outline` for the first AI generation (structure/plan)
- Use `action: draft` for the full written content
- `next` — which step to go to when done

---

### 3. `approve` — Show AI output and ask what to do next

```yaml
- id: review_step
  type: approve
  question: "Here is your draft. What would you like to do?"
  options:
    - id: approve
      label: "Looks good, continue"
      next: final_step
    - id: redo
      label: "Try again"
      next: create_document
    - id: change
      label: "I want to change something"
      next: feedback_step
```

- Each option has an `id`, a `label` (button text), and a `next` (where to go)
- The `next` can jump forward **or backward** — that's how you create loops

---

### 4. `output` — End of the flow

```yaml
- id: final_step
  type: output
  message: "Your document is ready!"
```

---

## How to Link Steps

Every step runs in order by default. To jump to a specific step, add `next:`:

```yaml
- id: feedback
  type: ask
  question: "What should change?"
  save_as: feedback
  next: create_document    # ← go back and regenerate
```

You can jump forward, backward, or to any step by its `id`.

---

## Quick Checklist Before You Save

- [ ] Every step has a unique `id` (no duplicates)
- [ ] Every `next:` points to an `id` that exists
- [ ] Every `save_as:` uses a simple word, no spaces (use `_` instead)
- [ ] The flow ends with a step of `type: output`
- [ ] Each `approve` option has an `id`, a `label`, and a `next`

---

## How to Apply Your Flow

1. Edit or create a `.yaml` file in this `flows/` folder
2. In `.env`, update: `FLOW_FILE=flows/your-flow-name.yaml` *(optional — defaults to ebook-flow.yaml)*
3. Restart the server: `python api.py`
4. Open the chat UI — your new flow is live

That's it. No Python, no deployment, no code review needed.
