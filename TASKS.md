# TASKS.md — WebStaffr

## Purpose
Single source of next actions. Sorted by smallest atomic step. No future speculation entries — only what's actually next.

## Execution Model
Claude operates this queue via a single loop: Verify → Decide → Execute → Verify. See CLAUDE.md's "Execution Model" section for the full rule, including which changes may be self-approved versus which require explicit approval.

## Current Queue
1. [ ] Founder decision: resolve Phase 1 scope conflict — full production infrastructure buildout (per 2026-07-04 autonomy directive) vs. the recorded minimal single-tenant/single-workflow slice (per ARCHITECTURE.md/DECISIONS.md, which explicitly excludes any stack/hosting/database choice) vs. a hybrid. Blocking all further Phase 1 build work.
2. [ ] Once scope is decided: record the decision in DECISIONS.md (superseding or refining the existing minimal-slice entry as applicable).
3. [ ] Once scope is decided: make the concrete stack/hosting/DB choice needed to proceed — architecture-adjacent, requires explicit approval.
4. [ ] Begin implementation of the first system slice per whichever scope is chosen — requires explicit approval (first real code).

## Completed
- Governance baseline written and committed: CLAUDE.md, PROJECT.md, ARCHITECTURE.md, DECISIONS.md (2026-07-04).
- First system behavior decided: internal workflow execution (2026-07-04).
- Minimal design recorded: tenant_context, workflow_definition, workflow_executor, execution_record (2026-07-04).
- Single-loop execution model adopted (2026-07-04) — see CLAUDE.md, DECISIONS.md.
- Resolved local/remote git divergence (unrelated histories with GitHub's auto-generated `.gitignore`/`README.md`); merged and pushed governance baseline to `github.com/keithtortorich/WebStaffr` at `fc4dc46` (2026-07-04).
- Diagnosed and cleared repeated `.git` lock-file corruption (stale `.lock`/`.lock.bak`/`.lock.bak.N` files under refs/heads, HEAD, index) caused by concurrent access from two different tool paths touching the same repo; standardized on a single real-terminal access path (Desktop Commander) going forward to eliminate the dual-writer race (2026-07-04).
- Removed stale local `master` branch (fully contained in `main`, no unique commits) (2026-07-04).
- Adopted the autonomous Engineering Director operating model in CLAUDE.md, replacing the strict per-phase approval-gate model with a Decision Framework (founder-decision vs. AI-decision categories), an AI resource/cost strategy, four concrete execution phases, and explicit self-healing/chaos-engineering practices (2026-07-04) — see DECISIONS.md.
