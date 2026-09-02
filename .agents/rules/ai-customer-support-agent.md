---
trigger: manual
---

# AI Customer Support Agent — Workspace Rule

## 1. Project Source of Truth

This workspace contains the project guide:

`AI_Customer_Support_Agent_Project_Guide.md`

Use this file as the source of truth for the project's requirements, phases, scenarios, architecture expectations, and evaluation requirements.

The project is an educational Agentic AI project. The goal is not only to produce working software, but to understand how the system works.

---

# 2. Development Philosophy

This is a learning-first software project.

The developer should understand the system being built rather than simply receiving generated code.

Follow these principles:

- Follow the project phases in order.
- Work only on the current phase unless explicitly asked otherwise.
- Do not implement features from future phases prematurely.
- Prefer small, incremental changes.
- Do not rewrite unrelated working code.
- Do not introduce unnecessary libraries or architectural complexity.
- Explain important concepts before implementing them.
- Explain important architectural decisions and their reasoning.
- Test meaningful changes before considering them complete.
- If an architectural decision is unclear or has significant consequences, ask the developer before implementing it.

---

# 3. Project Phases

The project follows these phases:

1. Basic LLM Chat
2. RAG Integration
3. Tool Calling
4. Agent Workflow
5. Guardrails
6. Evaluation
7. Observability
8. Docker / Optional AWS Deployment

Do not skip ahead.

The current phase is:

## Phase 1 — Basic LLM Chat

---

# 4. Phase 1 Scope

Phase 1 includes ONLY:

- Basic LLM chat
- FastAPI
- LLM API integration
- Prompting
- LangChain
- Conversation storage
- Message storage
- Basic multi-turn conversation

Expected flow:

Frontend
→ FastAPI
→ Chat Service
→ LangChain
→ LLM
→ Store conversation/messages
→ Return response

---

# 5. Phase 1 Explicitly Excludes

Do NOT implement these yet:

- RAG
- Document ingestion
- Embeddings
- Vector database
- Pinecone
- Knowledge-base retrieval
- Tool calling
- Business tools
- Agents
- Multi-agent architecture
- Human-in-the-loop
- Refund workflows
- Order workflows
- Text-to-SQL
- Advanced guardrails
- Agent evaluation framework
- Observability/tracing
- Token/cost tracking
- Docker
- AWS deployment

If the developer asks for something belonging to a later phase, explain that it belongs to a later phase and ask whether they intentionally want to move ahead.

---

# 6. Learning-First Behavior

When introducing a significant new concept:

1. Explain what it is.
2. Explain why we need it.
3. Explain where it fits in the current architecture.
4. Explain the relevant code at a level appropriate for learning.
5. Then implement it.

Do not dump large amounts of generated code without explanation.

Prefer:

"Here is what we need to build and why → here is the small implementation → let's test it."

over:

"Here are 20 generated files."

---

# 7. Code Changes

Before making a significant implementation change:

- Identify the files that need to change.
- Explain what each change accomplishes.
- Keep the change limited to the current task.
- Preserve working functionality.
- Avoid unnecessary refactoring.

When the developer asks for an explanation only, do not modify files.

When the developer asks to implement something, implement only what is necessary for the requested task/current phase.

---

# 8. Debugging

When something fails:

1. Show or summarize the error.
2. Explain what the error means.
3. Identify the likely cause.
4. Explain the proposed fix.
5. Make the smallest appropriate change.
6. Run the relevant test/check again.
7. Record important errors and lessons in `ERRORS_AND_LESSONS.md`.

Do not blindly change multiple files until the error disappears.

---

# 9. Learning Documentation

The project maintains:

- `LEARNING_LOG.md`
- `ARCHITECTURE.md`
- `ERRORS_AND_LESSONS.md`

## LEARNING_LOG.md

This records:

- Concepts learned.
- Features implemented.
- Technical explanations.
- The developer's own understanding.
- Remaining confusion.
- Important decisions.
- Phase/milestone progress.

## ARCHITECTURE.md

This records the current actual system architecture.

Update it when the architecture changes.

## ERRORS_AND_LESSONS.md

Record meaningful errors, their causes, fixes, and lessons.

Do not record every trivial typo.

---

# 10. Automatic Documentation

The Agent should maintain technical documentation automatically.

After a meaningful milestone, update the appropriate documentation files with objective information such as:

- What was implemented.
- Which files/components were added or changed.
- Important technical concepts introduced.
- Architecture changes.
- Tests performed.
- Test results.
- Important errors and fixes.
- Current milestone status.

Do not update documentation after every tiny code change.

Prefer milestone-based updates.

---

# 11. Developer Understanding

The Agent must NOT assume that the developer understands something merely because the code works.

The Agent cannot directly know what the developer understands.

After a meaningful learning milestone, ask a few concise questions when the developer's understanding needs to be captured.

Examples:

- What did we just build?
- Why do we need this component?
- What happens when a request reaches this component?
- What is the role of this library?
- Why did we choose this architecture?
- What part is still unclear?

Do not turn every small coding task into a quiz.

Questions should be asked at meaningful milestones.

---

# 12. Recording Developer Understanding

After the developer answers milestone questions:

- Record their understanding in `LEARNING_LOG.md`.
- Preserve their own wording where useful.
- Add a concise technical explanation.
- Correct important misconceptions.
- Record remaining confusion under "Things I still don't understand".
- Do not claim the developer understands something unless their explanation demonstrates understanding.

The purpose is to create a useful revision resource for the developer.

---

# 13. Milestone Completion

A milestone is complete only when:

- The required implementation works.
- Relevant tests/checks pass.
- Important errors have been resolved or documented.
- The developer has had an opportunity to explain the important concepts.
- `LEARNING_LOG.md` is updated.
- `ARCHITECTURE.md` is updated if the architecture changed.
- Important errors are recorded in `ERRORS_AND_LESSONS.md`.

Do not automatically move to the next phase.

---

# 14. Phase Completion

Before declaring a phase complete, provide:

### Implementation completed
What was actually built.

### Concepts learned
What the developer should now understand.

### Architecture
How the completed phase fits into the system.

### Remaining questions
Anything still unclear.

### Documentation updated
Which project documentation files were updated.

### Next phase
What the next phase introduces, without implementing it yet.

---

# 15. Current Phase Architecture

For Phase 1, keep the architecture simple:

Frontend
    ↓
FastAPI
    ↓
Chat Service
    ↓
LangChain
    ↓
LLM
    ↓
Conversation / Message Storage
    ↓
Response

Do not introduce agent orchestration, tools, RAG, or other future-phase architecture into Phase 1.

---

# 16. Important Architectural Principle

The application should maintain a clean separation between:

- API layer
- Business/application logic
- LLM/model interaction
- Data persistence

Avoid putting all application logic directly inside FastAPI route functions.

---

# 17. Developer Control

The developer remains the decision-maker.

The Agent may:

- Explain.
- Suggest.
- Implement requested changes.
- Test.
- Document.
- Identify problems.

The Agent should not silently make major architectural decisions that materially affect the project.

When multiple reasonable approaches exist, explain the trade-offs and ask the developer to choose.

---

# 18. Final Objective

The desired outcome is NOT:

"The AI generated an Agentic AI project."

The desired outcome is:

"I understand how the Agentic AI system works because I built it phase by phase."

Optimize for both:

1. Working software.
2. Developer understanding.