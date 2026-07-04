# DECISIONS.md — WebStaffr

## Purpose
This document is the record of irreversible or significant choices made during the lifecycle of WebStaffr. It captures why the system is the way it is — not what the system is (PROJECT.md), not how it is structured (ARCHITECTURE.md), and not how work proceeds (CLAUDE.md).

## Rule
A decision exists in this document only once it has been explicitly made and recorded here. Nothing is assumed, inferred, or carried forward as a decision — including from the legacy `webstaff` repository, which holds no authority over decisions for WebStaffr. Prior implementation choices in `webstaff` are not treated as precedent, default, or already-decided for this system.

## Decision Entry Format
Each recorded decision includes:
- **Decision:** what was decided
- **Date:** when it was decided
- **Context:** what prompted the decision
- **Alternatives considered:** what else was evaluated
- **Reason rejected (for alternatives):** why each alternative was not chosen
- **Tradeoffs accepted:** what was given up in choosing this option
- **Status:** active / superseded / reversed

## Architectural Decisions

**Decision:** First system behavior is internal workflow execution.
**Date:** 2026-07-04
**Context:** Four candidate first-functions were identified from PROJECT.md's capability list (internal workflow execution, inbound chat, inbound voice, outbound automation); one had to be selected to define the narrowest functional MVP boundary.
**Alternatives considered:** inbound chat handling, inbound voice handling, outbound automation.
**Reason rejected:** inbound chat and inbound voice both depend on a channel-input mechanism not yet built. Outbound automation depends on a triggering condition or data source not yet present. Internal workflow execution was the only candidate with no dependency on an external-facing channel.
**Tradeoffs accepted:** the system's first working slice will not be customer-facing or channel-facing; voice/chat/integration capability (central to the product vision) is deferred past this first slice.
**Status:** active.

**Decision:** Governance documents (`CLAUDE.md`, `PROJECT.md`, `ARCHITECTURE.md`, `DECISIONS.md`) are written with full content as the canonical system baseline, not as headers-only placeholders.
**Date:** 2026-07-04
**Context:** An interim execution-protocol draft specified governance files should be "headers only initially" at repository initialization. Full content for these four files had already been drafted and approved earlier in the same process.
**Alternatives considered:** headers-only skeletons, to be filled in later.
**Reason rejected:** would discard already-approved work for no benefit; full content does not conflict with any phase-gating rule, since these are documents, not implementation code.
**Tradeoffs accepted:** none identified — full-content governance docs carry no scope or implementation risk.
**Status:** active, permanent — the "headers-only" rule for these four files does not apply going forward.

**Decision:** Adopt a single-loop execution model (Verify → Decide → Execute → Verify) for routine, self-approvable work, in place of speculating further phases (e.g., Legacy Audit, Foundation Build, Feature Loop) in detail before they're reached.
**Date:** 2026-07-04
**Context:** A multi-phase system (7 named phases, a proposed skill YAML, a proposed CI enforcement layer) had been specified in increasing detail before any runtime existed to enforce it, causing repeated rework and drift across sessions.
**Alternatives considered:** continuing to expand the multi-phase system in more detail; adding a CI-enforcement YAML and skill-schema file to gate phase transitions.
**Reason rejected:** both add process weight with no corresponding runtime to enforce them — the actual enforcement mechanism in this project has always been conversational discipline (phase rules followed turn by turn), which the single-loop model uses directly instead of simulating through unused CI/YAML scaffolding.
**Tradeoffs accepted:** less upfront specification of long-term phases in exchange for less speculative work; self-approval for a narrowly-defined safe category (reversible, no external interaction, no architecture/data-model shift, no new dependency) trades a small amount of oversight for reduced founder involvement, mitigated by mandatory logging of every self-approved change in commit messages and `TASKS.md`.
**Status:** active.

**Decision:** Adopt an autonomous Engineering Director operating model in CLAUDE.md, replacing the strict per-phase approval-gate model (Assessment → Design → Build with mandatory stop-and-wait between phases) with a Decision Framework (founder-decision vs. AI-decision categories), an AI resource/cost strategy, four concrete execution phases (Governance & Foundation, Legacy Audit & Migration, Iterative Feature Development, Continuous Improvement), and explicit self-healing/chaos-engineering practices.
**Date:** 2026-07-04
**Context:** The founder provided a new operating directive in-session, explicitly stating it should replace prior strategy and thought-process rules, after a session in which strict per-item approval gating on git/repo mechanics created friction disproportionate to the risk of the actions involved.
**Alternatives considered:** keeping the existing Assessment/Design/Build gate model unchanged; adopting the new directive's language verbatim with no reconciliation against existing repo state.
**Reason rejected:** the old model's blanket stop-and-wait ceremony did not scale to routine, low-risk repo mechanics and was explicitly identified by the founder as not working; adopting the new directive verbatim without reconciliation would have silently overridden the still-active, explicitly recorded minimal-first-slice decision below without surfacing the conflict, violating this project's own Memory and Record Integrity rule.
**Tradeoffs accepted:** less per-item founder involvement in exchange for founder-declared trust in best-practice autonomous execution; safety is preserved by keeping an unchanged, explicit escalation list (product direction, budget, legal/compliance, vendor selection, major architecture, material cost/schedule impact, and anything reversing a recorded decision) rather than removing escalation altogether.
**Status:** active. Note: this decision governs *how Claude operates*; it does not itself resolve the still-open Phase 1 scope question raised the same day (see "First system behavior is internal workflow execution" above, and TASKS.md item 1).

## Tradeoffs Accepted
See individual decisions above.

## Rejected Alternatives
See individual decisions above.

## Strategic Choices (Scalability, Cost, Structure)
None recorded yet beyond the architectural decisions above.

## Security-Related Decisions
None recorded yet.

## Multi-Tenant Model Decisions
None recorded yet — multi-tenancy is a standing baseline requirement (see ARCHITECTURE.md), not yet a specific implementation decision.

## Integration Approach Decisions
None recorded yet.
