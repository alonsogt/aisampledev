# How to Build a New Agent Flow

> **Where does the *production* flow live?**  
> On **Azure AI Foundry**, as the workflow **`ebook-conversation-flow`**.  
> This guide describes the **local** YAML format used by `flow_engine.py` (`ebook-flow.yaml`), which powers **local** samples (e.g. Teams bot). It is **not** the Foundry workflow format. For Foundry, edit the workflow in the Foundry portal or use `scripts/deploy_ebook_conversation_workflow.py`. See **`flows/README.md`**.

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

## Full Example — IT Support Ticket Triage

Here's a complete flow for a different use case to show it's reusable:

```yaml
name: IT Support Triage
description: Helps employees submit and prioritize IT support tickets

steps:

  - id: issue_type
    type: ask
    question: "What kind of issue are you having?"
    options:
      - Hardware problem
      - Software / application issue
      - Access / permissions
      - Network or VPN
      - Something else
    save_as: issue_type

  - id: urgency
    type: ask
    question: "How urgent is this?"
    options:
      - Critical — blocking my work completely
      - High — major slowdown
      - Medium — can still work around it
      - Low — when you get a chance
    save_as: urgency

  - id: description
    type: ask
    question: "Describe the issue in a few sentences."
    hint: "e.g. My laptop won't connect to the VPN since the update yesterday"
    save_as: description

  - id: generate_ticket
    type: generate
    action: outline
    message: "Creating your ticket summary..."
    on_complete:
      show: outline
      next: confirm_ticket

  - id: confirm_ticket
    type: approve
    question: "Here is your ticket summary. Ready to submit?"
    options:
      - id: submit
        label: "Submit the ticket"
        next: done
      - id: edit
        label: "Change something"
        next: description

  - id: done
    type: output
    message: "Your ticket has been submitted. You'll receive a confirmation email."
```

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
