# AI Customer Support Agent --- Project Guide

## 1. Project Goal

Build an educational but realistic **Agentic AI Customer Support
Agent**.

The final system should be able to:

-   Understand customer requests.
-   Answer policy/FAQ questions using RAG.
-   Look up customer and order information.
-   Perform controlled business actions through tools.
-   Handle multi-step workflows.
-   Maintain conversation context.
-   Escalate sensitive, risky, complex, or low-confidence cases.
-   Request human approval for configured high-risk actions.
-   Convert selected natural-language database questions into safe SQL.
-   Log agent actions and outcomes.
-   Be evaluated using a test dataset and measurable metrics.
-   Be runnable locally and packaged with Docker.
-   AWS deployment is optional.

### Core principle

> RAG = Knowledge\
> Tools = Actions\
> Agent = Decision / Orchestration

The LLM must **never have unrestricted access to business operations**.
Application-level validation and permissions must control tool
execution.

------------------------------------------------------------------------

# 2. Important Learning Goal

This is not just a chatbot project.

The goal is to understand and implement the concepts behind a modern
Agentic AI application.

By the end of the project, I should be able to explain:

-   The difference between an LLM application and an agentic
    application.
-   How model calling works.
-   How tool calling works.
-   How an agent chooses and uses tools.
-   How RAG provides external knowledge.
-   How conversation memory works.
-   How multi-step agent workflows work.
-   Why guardrails are required.
-   How human-in-the-loop approval works.
-   How an LLM can safely interact with a relational database.
-   How agent behavior can be evaluated.
-   How agent actions and failures can be observed and debugged.

Do not optimize only for "working code". Optimize for understanding.

------------------------------------------------------------------------

# 3. Development Approach

The project must be implemented **phase by phase** according to the
assignment document.

Do not jump ahead unnecessarily.

For every phase:

1.  Understand the requirement.
2.  Decide the architecture/design.
3.  Implement the smallest useful version.
4.  Run it.
5.  Test it.
6.  Fix problems.
7.  Verify that the concept is understood.
8.  Only then move to the next phase.

Avoid generating the entire application at once.

Prefer incremental development and small, understandable changes.

------------------------------------------------------------------------

# 4. Official Development Phases

## Phase 1 --- Basic LLM Chat

Focus:

-   LLM API integration.
-   Prompting.
-   FastAPI chat endpoint.
-   Conversation creation/storage.
-   Message storage.
-   Basic multi-turn conversation support.

Expected basic flow:

``` text
User
  ↓
FastAPI
  ↓
LLM service
  ↓
Response
  ↓
Store conversation/message
```

At the end of Phase 1, the application should support a basic chat
conversation and persist the conversation history.

------------------------------------------------------------------------

## Phase 2 --- RAG Integration

Focus:

-   Customer-support knowledge base.
-   Policy and FAQ documents.
-   Document ingestion.
-   Chunking.
-   Embeddings.
-   Vector database.
-   Similarity retrieval.
-   Supplying retrieved context to the LLM.

Knowledge examples:

-   Return policy
-   Refund policy
-   Shipping policy
-   Warranty
-   Payment policy
-   Product FAQs
-   General support knowledge

Expected flow:

``` text
User question
    ↓
Retrieve relevant knowledge
    ↓
Relevant chunks
    ↓
LLM + retrieved context
    ↓
Answer
```

Do not spend time finding documents before Phase 2.

For this educational project, realistic fictional company policies can
be created so that the policies match the database and workflows.

------------------------------------------------------------------------

## Phase 3 --- Tool Calling

Implement controlled business tools such as:

``` text
search_knowledge_base(query)
get_customer(customer_id)
get_order(order_id)
cancel_order(order_id)
create_ticket(customer_id, category, description, priority)
request_refund(order_id, reason, amount)
```

Tool inputs must be validated by the application.

The LLM should request an action; the backend should validate and
execute the action.

Expected pattern:

``` text
LLM
 ↓
Tool request
 ↓
Application validation
 ↓
Tool execution
 ↓
Tool result
 ↓
LLM
```

Do not give the LLM unrestricted database or business-operation access.

------------------------------------------------------------------------

## Phase 4 --- Agent Workflow

Turn the system from simple tool calling into an actual agent workflow.

The agent should:

1.  Understand the user's intent/request.
2.  Determine whether knowledge or a tool is required.
3.  Select the appropriate tool when necessary.
4.  Validate tool arguments.
5.  Execute the tool.
6.  Analyze the tool result.
7.  Decide whether another step is necessary.
8.  Apply business rules.
9.  Generate the final response.
10. Log the action and outcome.

Example:

``` text
User: Cancel ORD-1001
        ↓
Understand request
        ↓
ORDER_CANCELLATION
        ↓
Get order
        ↓
Check eligibility
        ↓
Eligible?
     /      \
   Yes       No
    ↓         ↓
Cancel      Explain
    ↓
Final response
```

The project may use specialized agents such as:

-   Customer Support Agent
-   Order/Database Agent
-   Knowledge/RAG Agent
-   Escalation Agent

However, do not create unnecessary agents just for the sake of calling
the system "multi-agent". Keep responsibilities clear and justify the
architecture.

------------------------------------------------------------------------

## Phase 5 --- Guardrails

Implement:

-   Input validation.
-   Tool argument validation.
-   Permission checks.
-   Business-rule checks.
-   High-risk action detection.
-   Human approval.
-   Escalation.
-   Low-confidence handling.
-   Safe behavior when tools fail.

Examples of actions that may require human approval:

-   High-value refunds.
-   Sensitive account operations.
-   Complex complaints.
-   Actions outside normal business rules.
-   Repeated failed tool calls.
-   Explicit manager escalation.
-   Low-confidence decisions where appropriate.

Example:

``` text
Refund request
      ↓
Check amount
      ↓
High value?
   /       \
 No         Yes
 ↓           ↓
Continue   Human approval
             ↓
         Approve / Reject
             ↓
          Continue
```

Never allow the model alone to bypass application guardrails.

------------------------------------------------------------------------

## Phase 6 --- Evaluation

Create at least **50--100 test cases**.

Evaluate:

-   Intent accuracy.
-   Tool-selection accuracy.
-   Tool-argument accuracy.
-   Response correctness.
-   Escalation accuracy.
-   Average latency.
-   Tool failure rate.

Suggested targets from the assignment:

``` text
Intent accuracy          > 90%
Tool selection accuracy  > 90%
Tool argument accuracy   > 95%
Escalation accuracy      > 95%
```

Include normal cases, edge cases, failures, ambiguous requests, and
multi-turn conversations.

Example test scenarios:

1.  Return-policy question.
2.  Order-status lookup.
3.  Eligible cancellation.
4.  Ineligible cancellation.
5.  Refund eligibility.
6.  High-value refund requiring approval.
7.  Customer complaint requiring escalation.
8.  Multi-turn conversation.
9.  Tool failure.
10. Unknown/unsupported question.
11. Natural-language database question.
12. Invalid tool arguments.

------------------------------------------------------------------------

## Phase 7 --- Observability

Add visibility into agent behavior.

Track:

-   Agent/tool execution traces.
-   Tool calls.
-   Tool arguments.
-   Tool results.
-   Action status.
-   Latency.
-   Token usage where available.
-   Estimated model cost where available.
-   Errors and failures.
-   Important workflow decisions.

The existing `agent_actions` database concept should be used for action
logging.

Example:

``` text
conversation_id
tool_name
arguments
result
status
created_at
```

Observability should make it possible to answer:

> What did the agent do, why did it do it, what happened, and how long
> did it take?

------------------------------------------------------------------------

## Phase 8 --- Docker and Optional AWS Deployment

Containerize the application.

Expected considerations:

-   Backend container.
-   Database/service configuration.
-   Environment variables.
-   Docker Compose for local development.
-   Production configuration where appropriate.

AWS deployment is optional unless specifically required.

Do not prioritize deployment before the core agent works correctly.

------------------------------------------------------------------------

# 5. Required Customer Scenarios

The finished system should demonstrate at least these workflows.

### 1. Return policy

User:

> What is your return policy?

Expected:

``` text
Agent → RAG → Policy information → Answer
```

### 2. Order status

User:

> Where is ORD-1001?

Expected:

``` text
Agent → get_order() → Database → Answer
```

### 3. Cancellation

User:

> Cancel ORD-1001.

Expected:

``` text
Get order
→ Check eligibility
→ Cancel if eligible
→ Respond
```

### 4. Refund

User:

> I want a refund for ORD-1001.

Expected:

``` text
Get order
→ Check refund policy
→ Determine eligibility
→ Continue refund workflow
```

### 5. High-value refund

Expected:

``` text
Refund request
→ Detect high-value operation
→ Human approval
→ Approve/reject
→ Continue safely
```

### 6. Escalation

User:

> I want to speak to a manager.

Expected:

``` text
Detect escalation
→ Create high-priority ticket
→ Inform customer
```

### 7. Multi-turn conversation

Example:

``` text
User: I want to cancel my order.
Agent: What is your order number?
User: ORD-10245.
Agent: The order is eligible. Would you like me to cancel it?
User: Yes.
Agent: The order has been cancelled.
```

The agent must retain relevant context.

### 8. Tool failure

If a tool/database fails:

-   Do not hallucinate a result.
-   Return a safe response.
-   Retry/escalate only according to the designed workflow.
-   Log the failure.

------------------------------------------------------------------------

# 6. Database Design

The assignment proposes these entities:

``` text
customers
    id
    name
    email
    phone
    membership
    created_at

orders
    id
    customer_id
    status
    total_amount
    order_date
    delivery_date
    shipping_address

order_items
    id
    order_id
    product_id
    quantity
    price

tickets
    id
    customer_id
    category
    description
    priority
    status
    assigned_to
    created_at

conversations
    id
    customer_id
    created_at
    updated_at

messages
    id
    conversation_id
    role
    content
    created_at

agent_actions
    id
    conversation_id
    tool_name
    arguments
    result
    status
    created_at
```

Use PostgreSQL as the relational business database.

Use the vector database for knowledge retrieval rather than mixing
business records and document retrieval unnecessarily.

------------------------------------------------------------------------

# 7. API Requirements

Required API concepts from the assignment:

``` text
POST /api/v1/chat

GET /api/v1/conversations/{conversation_id}

POST /api/v1/tickets

GET /api/v1/tickets/{ticket_id}

POST /api/v1/agent-actions/{action_id}/approve
```

The API should use:

-   Request schemas.
-   Response schemas.
-   Validation.
-   Structured errors.
-   Logging.
-   Authentication-ready design.

------------------------------------------------------------------------

# 8. Suggested Project Structure

Start with the structure proposed in the assignment:

``` text
backend/
│
├── app/
│   ├── api/
│   ├── agents/
│   ├── tools/
│   ├── rag/
│   ├── services/
│   ├── models/
│   ├── schemas/
│   ├── database/
│   └── main.py
│
├── tests/
│
├── knowledge_base/
│   ├── return_policy.pdf
│   ├── refund_policy.pdf
│   └── shipping_policy.pdf
│
├── docker-compose.yml
├── .env.example
└── README.md
```

Files and folders should be introduced when they become necessary rather
than creating a large empty structure immediately.

------------------------------------------------------------------------

# 9. Architecture Principles

## RAG vs Tools

Use RAG for questions such as:

> What is the refund policy?

Use tools for questions/actions such as:

> Where is my order?

> Cancel my order.

> Create a support ticket.

The distinction is:

``` text
RAG   = knowledge
Tools = actions/data access
Agent = decision/orchestration
```

## LLM vs Application

The LLM can:

-   Understand language.
-   Classify intent.
-   Decide which capability is needed.
-   Generate tool requests.
-   Interpret tool results.
-   Generate natural-language responses.

The application must control:

-   Authentication/authorization.
-   Validation.
-   Business rules.
-   Tool execution.
-   Database permissions.
-   Approval requirements.
-   Safety constraints.

------------------------------------------------------------------------

# 10. Text-to-SQL

The system should support natural-language database questions where
appropriate.

Example:

> How many orders did customer CUS-1001 place last month?

Expected flow:

``` text
Natural language
      ↓
LLM generates SQL
      ↓
Validate SQL
      ↓
Permission/safety checks
      ↓
Execute against PostgreSQL
      ↓
Result
      ↓
LLM formats answer
```

The first implementation should strongly restrict generated SQL to
safe/read-only operations.

Never blindly execute arbitrary LLM-generated SQL.

------------------------------------------------------------------------

# 11. Development Rules for the IDE

This project is being developed in an IDE with AI assistance.

AI coding assistance should be used as a development aid, not as a
replacement for understanding.

Before making a significant change:

1.  Understand what component is being changed.
2.  Know why the change is required.
3.  Keep changes small.
4.  Run the application/tests after changes.
5.  Read and understand errors.
6.  Avoid blindly accepting large generated implementations.
7.  Do not rewrite working components unnecessarily.
8.  Preserve the phase structure.

When asking an AI coding assistant to modify the project, prefer prompts
such as:

> Explain this error and identify the likely cause. Do not modify the
> code yet.

or:

> Implement only the missing function in this file. Do not change
> unrelated files.

or:

> Review this implementation against the Phase 3 requirements and
> identify gaps. Do not rewrite it.

------------------------------------------------------------------------

# 12. Definition of Done for Each Phase

A phase is complete only when:

-   The required functionality works.
-   The implementation has been tested.
-   Errors are understood.
-   The architecture is documented where useful.
-   The main concept can be explained without relying on generated code.
-   The implementation does not unnecessarily break earlier phases.

------------------------------------------------------------------------

# 13. Current Status

## Phase 1 --- Basic LLM Chat

Status: NOT STARTED

## Phase 2 --- RAG Integration

Status: NOT STARTED

## Phase 3 --- Tool Calling

Status: NOT STARTED

## Phase 4 --- Agent Workflow

Status: NOT STARTED

## Phase 5 --- Guardrails

Status: NOT STARTED

## Phase 6 --- Evaluation

Status: NOT STARTED

## Phase 7 --- Observability

Status: NOT STARTED

## Phase 8 --- Docker / Optional AWS

Status: NOT STARTED

------------------------------------------------------------------------

# 14. Immediate Next Step

Do **not** start implementing all components.

First complete **Phase 1 --- Basic LLM Chat**.

Before writing code, establish:

1.  Exact Phase 1 requirements.
2.  Technology choices.
3.  Minimal architecture.
4.  Database requirements for conversations/messages.
5.  API contract.
6.  Folder structure needed for Phase 1.
7.  A small implementation plan.

Then implement and test Phase 1 before moving to Phase 2.

------------------------------------------------------------------------

# 15. Mentor Rule

The project should be treated as both:

-   a software project, and
-   a learning project.

The final code matters, but understanding matters equally.

The desired outcome is not:

> "The AI generated an Agentic AI project."

The desired outcome is:

> "I understand how the Agentic AI system works because I built it phase
> by phase."
