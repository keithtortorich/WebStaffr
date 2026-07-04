# TASKS.md — WebStaffr

## Purpose
Single source of next actions. Sorted by smallest atomic step. No future speculation entries — only what's actually next.

## Execution Model
Claude operates this queue via a single loop: Verify → Decide → Execute → Verify. See CLAUDE.md's "Execution Model" section for the full rule, including which changes may be self-approved versus which require explicit approval.

## Current Queue
1. [ ] Draft README.md content (identity-only, per PROJECT.md/ARCHITECTURE.md) — not yet drafted.
2. [ ] Confirm GitHub connector authorization status for this session before any push is attempted.
3. [ ] Push initial commits to `github.com/keithtortorich/WebStaffr` once connector access is confirmed — requires explicit approval (external system interaction).
4. [ ] Decide branch naming: rename local `master` to `main` before first push, or leave as-is — requires explicit approval (affects remote repo state).
5. [ ] Begin implementation of tenant_context / workflow_definition / workflow_executor / execution_record — requires explicit approval (first real code, architecture-adjacent).

## Completed
- Governance baseline written and committed: CLAUDE.md, PROJECT.md, ARCHITECTURE.md, DECISIONS.md (2026-07-04).
- First system behavior decided: internal workflow execution (2026-07-04).
- Minimal design recorded: tenant_context, workflow_definition, workflow_executor, execution_record (2026-07-04).
- Single-loop execution model adopted (2026-07-04) — see CLAUDE.md, DECISIONS.md.
