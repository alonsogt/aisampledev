AI AGENT EBOOK v1 — SAMPLE DATA LIBRARY
=========================================
This folder is the source of truth for the EBook Agent's grounding knowledge.
Upload this entire folder to SharePoint > Samples Library to enable real RAG.

FOLDER STRUCTURE
----------------
grounding/
  brand/          Brand voice, style guides, tone of voice
  examples/       Completed ebook examples the agent learns structure from
  research/       SME transcripts, industry benchmarks, reference material

models/           Chapter templates and topic taxonomy

output/           Sample output drafts used as quality benchmarks

HOW THE AGENT USES THESE FILES
-------------------------------
1. At runtime, the agent downloads all files in grounding/
2. Text is extracted and chunked into passages (approx. 180 words each)
3. Passages are scored by relevance to the ebook topic
4. Top passages are injected into the GPT-4o prompt as context
5. GPT-4o generates the outline and draft grounded in this content

TO ADD NEW SOURCES
------------------
1. Add the file to the correct subfolder
2. Update the source URL in the blueprint tracker app (data.json)
3. Re-run the agent — the index rebuilds automatically

MAINTAINED BY: Bridge Partners AI Practice
VERSION: 1.0  |  LAST UPDATED: 2025-Q1
