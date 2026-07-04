# TASKS.md — WebStaffr

## Purpose
Single source of next actions. Sorted by smallest atomic step. No future speculation entries — only what's actually next.

## Execution Model
Claude operates this queue via a single loop: Verify -> Decide -> Execute -> Verify. See CLAUDE.md's "Execution Model" section for the full rule, including which changes may be self-approved versus which require explicit approval.

## Current Queue
1. [ ] Founder to clarify scope of the Grok/Claude file-ownership split: does Grok's "backend core" ownership (persistence, Angel runtime, Grok Voice, GHL, deployment) apply retroactively to `webstaffr/db.py`, `repository.py`, `migrations/`, and `workers/angel/*` -- already built and verified here (42/42 tests, HEALTHY) -- or only to new backend work going forward? See DECISIONS.md, "Correct the record on Grok Voice status, and adopt a founder-mediated multi-agent coordination protocol."
2. [ ] Founder to supply real GHL_API_KEY / GHL_LOCATION_ID and/or GROK_API_KEY (as env vars, never committed) to exercise the real integrations locally. Without them the service runs safely on Null backends.
3. [ ] Implement the actual Grok realtime API call in `GrokVoiceBackend.respond()` once credentials and API docs are available to test against -- currently raises `NotImplementedError` by design.
4. [ ] Verify Dockerfile/docker-compose.yml actually build and run -- not possible on this machine (no Docker installed). Confirmed instead via direct `uvicorn` run (see DECISIONS.md / session notes).
5. [ ] AOKAI: still entirely unspecified anywhere in Drive or the Angel Package spec. Deferred, not started.
6. [ ] Decide what's next after Angel: a `/book` endpoint exposing `Angel.book_appointment` over HTTP (currently only reachable in-process), and/or wiring the widget onto an actual generated site.

## Completed
- Founder updated the Angel Package Drive doc with the real core prompt (previously referenced as "provided earlier" but missing). Re-synced `docs/drive-mirrors/Angel_Package.md`, replaced the draft placeholder in `webstaffr/workers/angel/angel_prompt.md` with the real text, reworked `Angel.render_prompt()` to append dynamic context as a structured block (the real prompt has no `{business_name}`-style template placeholders), and wired the rendered prompt into `respond()` via `context["system_prompt"]` so it's actually used, not dead code. Updated tests accordingly (42/42 passing); health check HEALTHY (2026-07-04).
- Governance baseline written and committed: CLAUDE.md, PROJECT.md, ARCHITECTURE.md, DECISIONS.md (2026-07-04).
- First system behavior decided: internal workflow execution (2026-07-04).
- Minimal design recorded: tenant_context, workflow_definition, workflow_executor, execution_record (2026-07-04).
- Single-loop execution model adopted (2026-07-04) -- see CLAUDE.md, DECISIONS.md.
- Resolved local/remote git divergence; merged and pushed governance baseline to `github.com/keithtortorich/WebStaffr` at `fc4dc46` (2026-07-04).
- Diagnosed and cleared repeated `.git` lock-file corruption; standardized on Desktop Commander for all git operations (2026-07-04).
- Removed stale local `master` branch (2026-07-04).
- Adopted the autonomous Engineering Director operating model in CLAUDE.md (2026-07-04) -- see DECISIONS.md.
- Resolved the Phase 1 scope conflict: minimal-first, infra added only when a specific feature needs it (2026-07-04) -- see DECISIONS.md.
- Implemented the first slice: `webstaffr/tenant.py`, `workflow.py`, `execution.py`, `executor.py` (2026-07-04).
- Added `tests/test_executor.py` (10 tests) and `scripts/health_check.py` (2026-07-04).
- Recorded model-usage guideline in CLAUDE.md: Sonnet 5 default, Opus for high-stakes work only (2026-07-04).
- Added SQLite persistence: `webstaffr/db.py`, `webstaffr/migrations/0001_initial.sql`, `webstaffr/repository.py`. 21/21 tests passing (2026-07-04) -- see DECISIONS.md.
- Fixed a stray backslash-backtick escaping artifact in CLAUDE.md (2026-07-04).
- Investigated Google Drive as source of truth for a larger integration request; found significant version sprawl (5+ Business Plan copies, 4 Financial Model copies) and no Angel/AOKAI spec docs at the time; escalated via clarifying questions rather than guessing (2026-07-04).
- Founder supplied "Angel Package" spec doc in Drive; mirrored locally (labeled, non-authoritative copy) at `docs/drive-mirrors/Angel_Package.md` (2026-07-04).
- Recorded scope-expansion decision: Angel worker, FastAPI, GoHighLevel, Grok voice, per founder's own spec (2026-07-04) -- see DECISIONS.md.
- Built Angel worker: `webstaffr/workers/angel/{angel.py, voice.py, ghl.py, booking.py, angel_prompt.md}`. Voice (Grok) and GHL clients are credential-checked interfaces with safe Null defaults for testing/offline use -- neither is a working live integration yet (no credentials available to build/test against). Draft placeholder prompt used since the founder's real prompt wasn't found in Drive (2026-07-04).
- Added `webstaffr/migrations/0002_angel_appointments.sql` (tenant-scoped appointments table) (2026-07-04).
- Built FastAPI router (`webstaffr/workers/angel/router.py`): `/health`, `/chat`, `/webhooks/ghl` (website_lead, missed_call). Added `fastapi`, `uvicorn`, `httpx` as new pinned dependencies (`requirements.txt`), first dependencies this repo has ever had (2026-07-04) -- see DECISIONS.md.
- Built `webstaffr/workers/angel/widget/angel-widget.js` -- vanilla JS embeddable chat widget; voice button present but explicitly informs the visitor voice isn't available yet, rather than silently doing nothing (2026-07-04).
- Added `Dockerfile`, `docker-compose.yml`, `.dockerignore` for local testing. Not build-verified (no Docker on this machine) -- instead verified the same code path directly via `uvicorn`, hitting `/health`, `/chat`, `/webhooks/ghl` over real HTTP with a real file-based SQLite DB (2026-07-04).
- Added `tests/test_angel.py` (13 tests) and `tests/test_router.py` (7 tests). Total 40/40 tests passing. Extended `scripts/health_check.py` with `angel_imports`, `angel_booking_round_trip`, `angel_router_smoke` checks -- HEALTHY (2026-07-04).
- Updated README.md with local dev setup instructions (2026-07-04).
- Corrected a factual claim from a second AI assistant ("Grok," run separately by the founder) that "Grok Voice" was live -- verified against `voice.py` that `GrokVoiceBackend.respond()` still raises `NotImplementedError` by design. Founder confirmed the correction and proposed a founder-mediated Claude/Grok coordination protocol (file-ownership comments, DECISIONS.md as shared log); adopted, with the ownership split's overlap against already-built backend files flagged back to the founder rather than assumed (2026-07-04) -- see DECISIONS.md.
