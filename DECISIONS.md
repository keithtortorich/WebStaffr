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

**Decision:** Resolve the Phase 1 scope conflict by staying strictly minimal: the first implementation slice remains exactly the three in-memory components already specified in ARCHITECTURE.md (Tenant Context, Workflow Definition, Workflow Executor, plus Execution Record). CLAUDE.md's Phase 1 description of full production infrastructure (auth, DB, API, CI/CD, secrets, monitoring, deployment) is read as the eventual destination of Phase 1 across iterations, not a mandatory day-one checklist — infrastructure is added incrementally, only when a specific subsequent feature actually requires it.
**Date:** 2026-07-04
**Context:** CLAUDE.md's new autonomy directive described Phase 1 as including full production infrastructure, which on a literal reading would supersede the still-active minimal-slice decision recorded earlier the same day. Founder asked for a direct, decisive resolution with tradeoffs rather than continued escalation.
**Alternatives considered:** (a) expand to full infrastructure buildout now, before any workflow-execution logic exists; (b) a hybrid — stand up just enough real infrastructure (e.g. one database, a thin API) to persist the workflow slice, deferring auth/CI-CD/secrets/monitoring.
**Reason rejected:** (a) would mean committing to stack, hosting, and database choices before the core logic they're meant to support has been proven to work at all — cost and schedule risk with no corresponding validation benefit, and a direct reversal of an explicit, still-valid, same-day decision with no new evidence justifying the reversal. (b) was closer, but even "just enough" infrastructure is still a stack/hosting/database commitment ARCHITECTURE.md explicitly excludes from this slice, and there is no concrete next feature yet that actually needs persistence — adding it now would be speculative.
**Tradeoffs accepted:** the first implementation is throwaway-shaped in the sense that it holds no state between runs and integrates with nothing; it must be deliberately revisited once a real feature (e.g. the first customer-facing channel) needs persistence, auth, or deployment. This is accepted as the correct order of operations — prove the logic, then build only the infrastructure that logic turns out to need.
**Status:** active. Supersedes no prior entry; clarifies how the "First system behavior is internal workflow execution" and "adopt autonomous Engineering Director operating model" decisions above relate to each other.

**Decision:** Add SQLite (Python stdlib `sqlite3`, no new dependency) as the persistence mechanism for WorkflowDefinitions and ExecutionRecords, via a repository pattern (`WorkflowRepository`, `ExecutionRepository`) with file-based numbered migrations (`webstaffr/migrations/*.sql`, tracked in a `schema_migrations` table).
**Date:** 2026-07-04
**Context:** Founder directed persistence as the next concrete step, specifying SQLite. This is the first feature-driven infrastructure decision under the "minimal-first, infra added when a feature needs it" resolution recorded above -- it is scoped to exactly the need (save/load two entity types), not a general database platform decision.
**Alternatives considered:** (a) a client-server database (Postgres/MySQL); (b) an ORM (e.g. SQLAlchemy) over either database; (c) storing a Step's `fn` directly via `pickle` for a fully transparent save/load of arbitrary workflows.
**Reason rejected:** (a) requires a running server process and hosting/ops decisions not otherwise needed yet -- premature for a single-process, unshipped slice, and against the cheapest-sufficient-option resource strategy. (b) adds a dependency and an abstraction layer for two small tables; the repository classes already give swappable persistence without it. (c) was rejected as a security anti-pattern, not just an implementation choice -- deserializing arbitrary code (via pickle or similar) from a database means anything that can write to that database can execute code in this process. Instead, only step *names* are persisted, in order; a `StepRegistry` resolves names back to real callables at load time, so a rebuilt WorkflowDefinition is exactly as safe as one built in code.
**Tradeoffs accepted:** SQLite is not suited to concurrent multi-writer or multi-process production workloads, and has no native network access for a multi-instance deployment -- both acceptable now, single-process and unshipped, and both are the kind of concrete need that would justify revisiting this decision later (that revisit is not implied or scheduled by this entry). Loading a persisted workflow now requires the caller to supply a StepRegistry containing every step name the workflow uses; an unregistered name fails loudly (`UnknownStepError`) rather than silently. `created_at` on `workflow_definitions` is overwritten on every re-save (no history of first-created date) -- acceptable for this minimal version, noted as a known limitation rather than engineered around speculatively.
**Status:** active.

**Decision:** Expand WebStaffr's scope beyond the minimal in-memory/SQLite slice to include the first AI Worker ("Angel"), a FastAPI-based webhook receiver, and two named third-party integrations (GoHighLevel for CRM sync, Grok for realtime voice), per the founder's own written spec (Google Drive doc "Angel Package", id `12y6zYI7q53GC5NdGv5ff5AHXxfIS7HEMe0dUbuJWa-I`, mirrored locally at `docs/drive-mirrors/Angel_Package.md`).
**Date:** 2026-07-04
**Context:** The "minimal-first, infra added when a feature needs it" decision (recorded above) deferred infrastructure until a concrete feature required it. The founder has now specified that concrete feature directly, naming FastAPI, GoHighLevel, and Grok explicitly in their own spec document -- this satisfies that decision's condition rather than reversing it.
**Alternatives considered:** none independently evaluated for the vendor choices (GoHighLevel, Grok) -- these were specified directly by the founder, not derived by Claude, so this entry records the choice rather than justifying it against alternatives. For FastAPI specifically as the web framework: Flask was the main plausible alternative; FastAPI was named directly in the founder's spec and is a reasonable fit for an async webhook receiver, so no separate evaluation was performed.
**Reason rejected:** n/a -- vendor and framework choices were founder-specified, not selected by Claude among alternatives.
**Tradeoffs accepted:** this is the first point at which WebStaffr code depends on external services and external credentials (GoHighLevel API, Grok API). Per CLAUDE.md's Security-First Baseline, no credentials are stored in code or committed to the repo -- both integrations are built as explicit interfaces with environment-variable-based configuration, and each raises a clear, descriptive error if invoked without credentials configured, rather than silently no-op'ing or fabricating a response. This means Angel's voice and GHL-sync features will not function until the founder supplies real credentials locally -- accepted as correct: better a clear "not configured" error than a fake success path. The `angel_prompt.md` core prompt referenced in the founder's spec ("the full ... prompt I provided earlier") was not found anywhere in the connected Google Drive -- a placeholder draft is used instead, clearly labeled as a draft pending the real prompt text, rather than inventing content and presenting it as the founder's own. AOKAI (mentioned in the original integration request) is not referenced anywhere in the Angel Package spec and is treated as out of scope for this decision -- deferred, not dropped.
**Status:** active.

**Decision:** Correct the record on Grok Voice status, and adopt a founder-mediated multi-agent coordination protocol between Claude (this repo) and a separately-run Grok assistant.
**Date:** 2026-07-04
**Context:** The founder is running a second AI assistant ("Grok") in a separate, unsynced environment alongside Claude on this same repo. Grok, relayed through the founder, asserted "Angel core + Grok Voice live" as current status. On inspection, `webstaffr/workers/angel/voice.py`'s `GrokVoiceBackend.respond()` explicitly raises `NotImplementedError` by design (no live xAI/Grok account available to build or test a real integration against; falls back to `NullVoiceBackend`) -- "live" was inaccurate. The founder acknowledged the correction and then proposed a coordination protocol: file-ownership comments (`## OWNED_BY: GROK` / `## OWNED_BY: CLAUDE`), cross-agent decisions logged here, and all coordination flowing through the founder pasting content between the two assistants (neither assistant has a direct channel to the other).
**Alternatives considered:** (a) accept Grok's status claim as given, without independent verification; (b) decline any cross-agent protocol and continue as sole engineering owner of this repo; (c) adopt the protocol as proposed, including its file-ownership split, without flagging overlap against already-built work.
**Reason rejected:** (a) would violate this project's own Memory and Record Integrity rule (established facts are not silently reversed or accepted unverified) and the founder's own epistemic standard of not presenting unverified claims as fact -- the claim was checked against the actual file before being repeated. (b) is not Claude's call to make unilaterally; the founder is free to run parallel AI tooling on their own repo, and the protocol itself was explicitly founder-confirmed twice in-session. (c) is rejected in the narrow sense that the proposed ownership split (Grok: persistence, Angel runtime, Grok Voice, GHL integrations, deployment; Claude: site generator, frontend, templates, non-core logic) assigns Grok prospective ownership of files -- `webstaffr/db.py`, `webstaffr/repository.py`, `webstaffr/migrations/`, `webstaffr/workers/angel/*` -- that were built and verified in this repo/session by Claude, with 42/42 tests passing and a HEALTHY health check as of this entry, including the just-completed real-prompt integration. Adopting the split silently as covering those existing files, with no shared version control or review step between the two assistants beyond founder copy-paste, risks one assistant's unreviewed edits overwriting the other's tested work with no diff/merge step catching it.
**Tradeoffs accepted:** the protocol (ownership-tagging convention, DECISIONS.md as the shared log, founder-mediated coordination) is adopted as directed. The specific question of whether Grok's backend-core ownership applies retroactively to the existing, tested files listed above, or only prospectively to new backend work, is treated as unresolved and flagged back to the founder rather than assumed either way -- this is an ambiguous-category change under CLAUDE.md's Decision Framework (defaults to founder-decision) and a potential conflict with this repo's Memory and Record Integrity rule if resolved silently. No file ownership tags have been retroactively added to existing files pending that clarification; going forward, new files/edits made by Claude in this repo will carry `## OWNED_BY: CLAUDE`.
**Status:** active. Resolved 2026-07-04: founder clarified ownership applies prospectively only. Existing files built and tested in this repo/session (`webstaffr/db.py`, `repository.py`, `migrations/*.sql`, `workers/angel/{angel,voice,ghl,booking,router}.py`, `workers/angel/widget/angel-widget.js`, `Dockerfile`, `docker-compose.yml`) remain under Claude's active ownership and are now tagged `## OWNED_BY: CLAUDE` (or the language-appropriate comment syntax) at the top of each file; Grok will treat them as read-only unless explicitly invited to change something specific. Grok ownership applies to new files/major new modules in the backend-core area going forward (new persistence extensions, new GHL sync services, deployment scripts, etc.). `angel_prompt.md` and `docs/drive-mirrors/Angel_Package.md` are deliberately NOT tagged with an ownership comment: the former is read verbatim as Angel's live system prompt (an ownership marker would leak into what the LLM backend receives), and the latter already carries its own Drive-mirror provenance header.

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
