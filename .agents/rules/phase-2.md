---
trigger: always_on
---

# AI Customer Support Agent — Workspace Rule

## 1. Source of Truth

The file:

`AI_Customer_Support_Agent_Project_Guide.md`

is the primary source of truth for the project's requirements, architecture, phases, capabilities, and constraints.

Follow the project's 8 phases in order.

Do not skip phases or implement future-phase functionality unless explicitly requested.

---

## 2. Current Phase

**Current Phase: Phase 2 — RAG Integration**

Phase 1 — Basic LLM Chat is completed.

Phase 1 implemented:

- FastAPI backend
- Pydantic request validation
- Google Gemini through LangChain
- MySQL with SQLAlchemy
- Conversation persistence
- Message persistence
- Conversation ID based sessions
- Basic multi-turn conversation memory

Phase 2 is now focused on adding the knowledge/RAG layer.

---

## 3. Phase 2 Scope

Phase 2 should focus only on:

- Understanding RAG architecture
- Creating the customer-support knowledge base
- Loading documents
- Document splitting/chunking
- Embeddings
- Vector database
- Similarity search
- Retrieval
- Connecting retrieval with LangChain
- Providing retrieved context to Gemini
- Testing knowledge-based questions
- Integrating RAG with the existing Phase 1 chat flow

Knowledge areas should include:

- Return policy
- Refund policy
- Shipping policy
- Warranty policy
- Product FAQs

---

## 4. Explicitly Do NOT Implement Yet

Do not implement or introduce these unless explicitly requested:

- Tool calling
- Customer/order tools
- Order cancellation
- Refund execution
- Ticket creation tools
- AI agents
- Multi-agent architecture
- Agent orchestration
- Human-in-the-loop approval
- Escalation workflows
- Text-to-SQL
- Advanced guardrails
- Evaluation framework
- Observability/tracing
- Token/cost tracking
- Docker
- AWS deployment

These belong to later phases.

---

## 5. Learning-First Development

This project is being developed as a learning project.

Do not blindly generate large amounts of code or build an entire phase automatically.

Before implementing a significant component:

1. Explain what it is.
2. Explain why it is needed.
3. Explain where it fits in the architecture.
4. Explain the relevant files/components.
5. Make the smallest reasonable implementation.
6. Test it.
7. Explain what was implemented.
8. Check the user's understanding before considering the milestone complete.

The goal is not only to make the application work.

The user should understand:

- What was built
- Why it was built that way
- How the components interact
- What happens when a request passes through the system

Do not claim that the user understands something merely because the code works.

---

## 6. Incremental Changes

Prefer small, understandable changes.

Do not:

- Rewrite large parts of the project unnecessarily
- Refactor unrelated code
- Change the architecture without explanation
- Add dependencies without explaining why
- Introduce future-phase functionality
- Replace working Phase 1 components without a reason

Preserve the existing Phase 1 architecture unless a Phase 2 requirement genuinely requires a change.

---

## 7. RAG Architecture

Maintain the distinction:

**RAG = Knowledge**

**Tools = Actions**

**Agent = Decision / Orchestration**

For Phase 2, the primary flow is:

```text
Client
   ↓
FastAPI
   ↓
Chat Service
   ↓
Knowledge Retrieval
   ↓
Relevant Context
   ↓
LangChain
   ↓
Gemini
   ↓
Response
   ↓
MySQL

The RAG pipeline should conceptually follow:

Documents
   ↓
Document Loading
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Database
   ↓
Similarity Search
   ↓
Relevant Chunks
   ↓
Gemini
   ↓
Answer

Keep the distinction between the existing conversation memory stored in MySQL and the new knowledge retrieval system.

8. Documentation

Maintain these project documents:

LEARNING_LOG.md

Track:

Concepts learned
Implementation completed
Architecture understood
Things the user can explain
Things that are unclear
Important mistakes/errors
User's own explanations
Phase completion status

Do not write that the user understands a concept until it has been checked.

ARCHITECTURE.md

Track the actual current architecture.

Update it when meaningful architectural changes are introduced.

Do not use it as a learning diary.

ERRORS_AND_LESSONS.md

Record meaningful:

Errors
Debugging discoveries
Architectural lessons
Important implementation decisions

Avoid recording trivial errors that provide no useful lesson.

9. Milestone Learning Check

At meaningful milestones, ask the user:

What did I build?
Why did I build it this way?
What happens when a request goes through it?

Use the user's answers to update LEARNING_LOG.md.

Do not automatically move to the next phase after a milestone.

The user should explicitly decide when to proceed.

10. Testing

After each meaningful implementation:

Run the relevant application/test.
Verify expected behavior.
Check errors before proceeding.
Explain failures rather than hiding or bypassing them.

Do not treat warnings as errors unless they actually affect functionality.

11. Development Control

The coding assistant may:

Explain concepts
Suggest approaches
Implement requested changes
Run tests
Help debug errors
Update technical documentation

The coding assistant should not silently make major architectural decisions.

When multiple reasonable architectural choices exist, explain the trade-offs before making the decision.

12. Phase Boundary

Do not automatically begin Phase 3 after completing Phase 2.

Phase completion requires:

Implementation completed
Relevant tests passing
Architecture understood
Learning check completed
Documentation updated

Only then should the user decide to move to the next phase.