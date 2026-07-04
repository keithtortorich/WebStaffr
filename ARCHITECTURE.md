# ARCHITECTURE.md — WebStaffr

## Purpose
Defines the high-level system design direction for WebStaffr — how the platform should be structured conceptually to deliver the product defined in PROJECT.md. This is direction, not implementation.

## System Architecture Approach
WebStaffr should be architected as a coordinated system of specialized AI workers operating over a shared communication and integration layer, rather than as a single undifferentiated application. The system's shape follows the product's shape: distinct workers performing distinct roles, coordinated toward a common outcome for a given customer.

## Core System Components
- **AI Worker Layer** — individual AI workers, each responsible for a bounded function (e.g., handling inbound conversation, following up, coordinating a process). Conceptually independent units of capability, addable and removable per customer.
- **Orchestration Layer** — coordinates handoffs and sequencing between workers, so a single customer interaction can span multiple workers without the customer experiencing a seam.
- **Communication Layer** — the channel-handling surface (voice, chat, and future channels) that normalizes external interaction into a form workers can act on, and worker output back into the right channel.
- **Integration Layer** — the boundary through which the system connects to external tools a customer already uses, abstracted so worker logic isn't tied to any one external system.
- **Customer/Account Layer** — a customer as a bounded context: their configuration, active workers, and data, distinct from every other customer.

## Data Flow Principles
- Data flows toward the point of decision, not the reverse — a worker receives what it needs to act, rather than pulling broadly from shared state.
- Customer data is always attributable to a specific customer context; it does not flow across customer boundaries implicitly.
- Interaction data enters through the communication layer, is normalized, is acted on by the appropriate worker(s) via orchestration, and its outcome flows back through the same layer.
- Data entering through the integration layer is treated as untrusted until validated, regardless of source.

## Service Decomposition Philosophy
Decomposition should follow boundaries of responsibility (per-worker, per-capability), not the accident of what was easiest to build first. The system should tolerate being built initially in a more consolidated form and later split along those same responsibility boundaries without redrawing them — modular now or modular later, never a form that resists ever splitting. Whether an initial build is one deployable unit or several is a later decision; the responsibility boundaries are the durable part.

## Integration Strategy Principles
- External tools connect through a common integration boundary, not through direct, one-off couplings from individual workers.
- Integrations are additive — a customer's set of connected tools grows without requiring changes to core worker or orchestration logic.
- The system degrades gracefully when an integration is unavailable, rather than one missing integration affecting unrelated capability.

## Scalability Philosophy
- The system scales along two independent axes — number of customers, and workload per customer. Growth in one should not force redesign to accommodate the other.
- Capacity added to serve growth is additive to the existing system, not a restructuring of it.
- Cost of serving a customer scales with that customer's actual usage, not with the platform's total size.

## Security Principles (System Level)
- Customer data is isolated by default; crossing a customer boundary is the exception requiring explicit justification, never the default assumption.
- Every external interaction, inbound or outbound, is treated as a trust boundary — verified and constrained, not implicitly trusted because it arrived through an established channel.
- A failure or compromise in one component or one customer's context must not cascade into another's.
- Actions affecting a customer's real-world operations or data require a traceable basis for why the system took that action.

## Multi-Tenant Model (Abstract)
WebStaffr is inherently multi-tenant: many customer accounts operate within a shared platform while remaining logically isolated from one another. Each customer's workers, configuration, integrations, and data exist within a bounded context that does not leak into another customer's context, even while sharing the same underlying system. The degree of physical versus logical isolation is a later decision; the conceptual requirement is that isolation is real, not assumed.

## Reliability Philosophy
- Individual worker failure degrades gracefully — a failure in one capability should not take down unrelated capabilities or other customers.
- The system defines a fallback behavior for when an AI worker cannot confidently act (e.g., deferring to a human, or a safe default response), rather than acting unpredictably under uncertainty.
- Reliability is designed around the customer's experience of continuity, not any single component's uptime in isolation — the system as experienced by a customer should be more reliable than its least-reliable individual part.

## First System Slice — Minimal Design (Internal Workflow Execution)
Selected as the system's first real-world function (see PROJECT.md, DECISIONS.md). Minimal viable architecture for this slice only:

- **Components (three, no more):** Tenant Context (bounded scope every other entity belongs to); Workflow Definition (an ordered sequence of steps, scoped to one Tenant); Workflow Executor (runs one Workflow Definition instance step by step to completion, producing an Execution Record).
- **Execution model:** sequential, single-instance, run-to-completion. No concurrency, retry/scheduling, or multi-instance coordination in this slice.
- **Data flow:** Workflow Definition → Executor reads next step → step executes using only Tenant-scoped data → result written to Execution Record → next step or completion. Nothing leaves the Tenant boundary; no external system is called.
- **Data model (minimal):** `Tenant` (identifier only); `WorkflowDefinition` (belongs to one Tenant; ordered list of steps); `ExecutionRecord` (belongs to one Tenant; references one WorkflowDefinition; holds a step-by-step trace — input, output, timestamp, status per step).
- **Constraints:** every entity is Tenant-scoped from the first field; every step input is treated as untrusted and validated before execution; no secrets in Workflow Definitions or Execution Records; an Execution Record must be sufficient to fully reconstruct what happened in any given run.
- **Explicitly excluded from this slice:** voice handling, chat handling, outbound automation, external integrations, multi-workflow orchestration, agency/multi-account management, any UI, any stack/hosting/database choice.

## Relationship to Prior Documents
This architecture is defined independent of the legacy `webstaff` implementation and does not assume any existing repository structure is correct. It builds on PROJECT.md's product definition. It does not define operating rules, approval gates, or execution sequencing — those remain the domain of CLAUDE.md.
