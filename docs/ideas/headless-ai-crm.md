# Headless AI CRM

## Problem Statement
How might we strip the visual bloat of traditional CRMs (like WACRM) and adapt their core pipelines and campaign features into a purely "Headless CRM"—managed entirely in the background by Gemini on behalf of an AI-powered solo founder?

## Recommended Direction
**The "Invisible" AI-Automated Pipeline & Local Engine**
Instead of building React dashboards and Kanban boards, we turn `wa-desktop-mcp` into an invisible local data engine. Gemini acts as the sole orchestrator. When a new message arrives, Gemini reads the chat, automatically determines the intent, updates a local SQLite database to move the contact across deal stages (Lead -> Negotiating -> Won), and fires off broadcasts—all without you ever opening a CRM window. 

## Key Assumptions to Validate
- [ ] **LLM Reliability**: We are betting that Gemini can accurately parse unstructured WhatsApp conversations and correctly classify deal stages without human verification. (Test: Run it in "shadow mode" first where it proposes stages).
- [ ] **State Concurrency**: We are assuming a local JSON/SQLite database can handle rapid read/write cycles from background MCP tools without race conditions.
- [ ] **Context Limits**: We assume we can pass enough historical chat context to Gemini so it understands the full deal history before changing a pipeline stage.

## MVP Scope
**IN:**
- A local SQLite/JSON database in `wa-desktop-mcp` tracking Contacts, Tags, and Deal Stages.
- New MCP Tools: `move_deal_stage`, `update_contact_notes`, `get_pipeline_summary`, `search_contacts`.
- A background automation loop where Gemini reviews unread messages and updates the CRM state automatically.

**OUT:**
- Visual Kanban boards or web dashboards (Gemini IS the interface).
- Multi-agent or team features (built strictly for a solo founder).
- Complex visual flow builders for automations (automations are handled by the LLM's natural reasoning).

## Not Doing (and Why)
- **A local web dashboard for the CRM** — Defeats the purpose of max automation. If you have to log in and drag cards around, you're losing time. Gemini should drag the cards.
- **Postgres / Supabase sync** — Unnecessary complexity and latency. A local SQLite file is lightning fast, 100% private, and perfectly suits a solo local setup.
- **Complex UI-based Automations (like WACRM)** — Hardcoding visual if/then branches is obsolete when an LLM can just read a natural language rule: "If they ask for a price, quote $29."

## Open Questions
- Should Gemini autonomously send the replies as it updates the CRM, or should it just draft them locally for you to hit "Approve" in the WhatsApp Web UI?
