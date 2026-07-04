# TASKS.md — WebStaffr

## Purpose
Single source of next actions. Sorted by smallest atomic step. No future speculation entries — only what's actually next.

## Execution Model
Claude operates this queue via a single loop: Verify -> Decide -> Execute -> Verify. See CLAUDE.md's "Execution Model" section for the full rule, including which changes may be self-approved versus which require explicit approval.

## Current Queue
1. [ ] Decide the first customer-facing or persistence-driven feature to build next -- founder input needed on priority. Any further infrastructure (API, auth, CI/CD, hosting) is added only when a specific feature needs it, per the resolved Phase 1 scope.
2. [ ] Once a next feature is chosen: make any concrete stack/hosting choice that specific feature needs -- architecture-adjacent, requires explicit approval.
3. [ ] Consider wiring `scripts/health_check.py` and `python3 -m unittest discover -s tests` into a CI workflow once a CI provider is chosen (not yet chosen -- no infra decision made).

## Completed
- Governance baseline written and committed: CLAUDE.md, PROJECT.md, ARCHITECTURE.md, DECISIONS.md (2026-07-04).
- First system behavior decided: internal workflow execution (2026-07-04).
- Minimal design recorded: tenant_context, workflow_definition, workflow_executor, execution_record (2026-07-04).
- Single-loop execution model adopted (2026-07-04) -- see CLAUDE.md, DECISIONS.md.
- Resolved local/remote git divergence (unrelated histories with GitHub's auto-generated `.gitignore`/`README.md`); merged and pushed governance baseline to `github.com/keithtortorich/WebStaffr` at `fc4dc46` (2026-07-04).
- Diagnosed and cleared repeated `.git` lock-file corruption caused by concurrent access from two different tool paths touching the same repo; standardized on a single real-terminal access path (Desktop Commander) going forward (2026-07-04).
- Removed stale local `master` branch (2026-07-04).
- Adopted the autonomous Engineering Director operating model in CLAUDE.md (2026-07-04) -- see DECISIONS.md.
- Resolved the Phase 1 scope conflict: staying strictly minimal, infra added only when a specific feature needs it (2026-07-04) -- see DECISIONS.md.
- Implemented the first slice: `webstaffr/tenant.py`, `webstaffr/workflow.py`, `webstaffr/execution.py`, `webstaffr/executor.py` -- stdlib-only, in-memory, tenant-scoped, untrusted-input validation on every step, bounded per-step retry, full execution trace (2026-07-04).
- Added `tests/test_executor.py` (10 tests) and `scripts/health_check.py` (self-healing smoke-test runner) (2026-07-04).
- Recorded model-usage guideline in CLAUDE.md: Sonnet 5 default, Opus only for high-stakes architecture/security/governance-conflict work, no Fable for engineering (2026-07-04).
- Added SQLite persistence for WorkflowDefinitions and ExecutionRecords: `webstaffr/db.py` (connection + migrations), `webstaffr/migrations/0001_initial.sql`, `webstaffr/repository.py` (WorkflowRepository, ExecutionRepository), `StepRegistry`/`UnknownStepError`/`step_names`/`from_step_names` added to `webstaffr/workflow.py`, `to_dict`/`from_dict` added to `webstaffr/execution.py`. `tests/test_repository.py` added (11 tests); `scripts/health_check.py` extended with a persistence round-trip check. 21/21 tests passing, health check HEALTHY. Decision recorded in DECISIONS.md (2026-07-04).
- Fixed a stray escaping artifact in CLAUDE.md (literal backslash-backtick sequences from an earlier heredoc write) -- self-healing, logged here (2026-07-04).
