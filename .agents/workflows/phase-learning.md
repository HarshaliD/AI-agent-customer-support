---
description: Use this workflow when working on a meaningful task or milestone in the AI Customer Support Agent project , like before or after a phase
---

# Phase Learning Workflow

## Purpose

Use this workflow when working on a meaningful task or milestone in the AI Customer Support Agent project.

The goal is to implement the requested functionality while ensuring that the developer understands what was built.

---

## Step 1 — Identify the Current Phase

Read:

`AI_Customer_Support_Agent_Project_Guide.md`

Determine:

- Current project phase.
- Current phase requirements.
- What is explicitly out of scope.

Do not implement later-phase functionality.

---

## Step 2 — Understand Before Coding

Before modifying code, briefly explain:

1. What we are building.
2. Why we need it.
3. Where it fits in the architecture.
4. Which files/components will be affected.
5. What the implementation will NOT include.

If an important architectural choice is unclear, ask the developer before proceeding.

---

## Step 3 — Implement Incrementally

Implement the smallest useful change that satisfies the current task.

Rules:

- Keep changes focused.
- Avoid unrelated refactoring.
- Follow the existing project structure.
- Reuse existing components where appropriate.
- Do not introduce unnecessary dependencies.

---

## Step 4 — Verify

After implementation:

- Run the relevant application/test/check.
- Verify the expected behavior.
- Report what was tested.
- If something fails, diagnose and fix it rather than hiding the failure.

---

## Step 5 — Explain

After the implementation works, explain:

- What changed.
- Why it works.
- The important code/components.
- How the request flows through the system.
- Any important design decisions.

Keep the explanation focused on learning.

---

## Step 6 — Learning Check

If this was a meaningful milestone, ask the developer a few short questions to verify understanding.

Prefer questions such as:

- What did we just build?
- Why is this component needed?
- What happens when a request reaches it?
- Why did we choose this approach?
- What is still unclear?

Do not ask unnecessary questions for trivial changes.

---

## Step 7 — Update Documentation

After the milestone:

Update:

`LEARNING_LOG.md`

with:

- What was implemented.
- Concepts learned.
- Developer's understanding.
- Technical explanation.
- Remaining questions.
- Milestone status.

Update:

`ARCHITECTURE.md`

if the architecture changed.

Update:

`ERRORS_AND_LESSONS.md`

if a meaningful error or debugging lesson occurred.

Do not overwrite useful previous learning.

---

## Step 8 — Confirm Milestone

Report:

### Completed
What works.

### Learned
What concepts were covered.

### Still unclear
Anything the developer has not yet understood.

### Documentation
Which files were updated.

### Next
The next task within the CURRENT phase.

Do not automatically begin the next phase.

---

## Step 9 — Phase Boundary

When all milestones in the current phase are complete:

Do NOT immediately implement the next phase.

Instead provide:

- Phase completion summary.
- Final learning summary.
- Architecture summary.
- Remaining questions.
- Test results.
- Documentation status.
- Brief explanation of what the next phase will introduce.

Wait for the developer to explicitly begin the next phase.