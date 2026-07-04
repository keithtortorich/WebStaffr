# TASKS.md — WebStaffr

## Purpose
Single source of next actions. Sorted by smallest atomic step. No future speculation entries — only what's actually next.

## Execution Model
Claude operates this queue via a single loop: Verify -> Decide -> Execute -> Verify. See CLAUDE.md's "Execution Model" section for the full rule, including which changes may be self-approved versus which require explicit approval.

## Current Queue
1. [ ] Decide the first customer-facing or persistence-requiring feature to build next (this is what should drive the *next* infrastructure decision — per DECISIONS.md, infra is added when a specific feature needs it, not speculatively). Founder input needed on priority.
2. [ ] Once a next feature is chosen and it needs persistence: make the concrete stack/hosting/DB choice for that specific need — architecture-adjacent, requires explicit approval.
3. [ ] Consider wiring `scripts/health_check.py` and `python3 -m unittest discover -s tests` into a CI workflow once a CI provider is chosen (not yet chosen — no infra decision made).

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
- Added `tests/test_executor.py` (10 tests, all passing) and `scripts/health_check.py` (self-healing smoke-test runner; verified HEALTHY) (2026-07-04).
