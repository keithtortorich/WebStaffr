# WebStaffr
Production repository for the WebStaffr AI workforce platform.

## Local development

```
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m unittest discover -s tests
./.venv/bin/python scripts/health_check.py
```

Run the Angel service locally:

```
./.venv/bin/uvicorn webstaffr.workers.angel.router:app --reload
```

Or via Docker (builds the same service; not yet verified on this machine -- no Docker install available here):

```
docker compose up --build
```

Optional environment variables (unset by default -- the service runs safely with no external calls when they're absent):

- `GROK_API_KEY` -- enables `GrokVoiceBackend` (credential-checked; the realtime API call itself is not yet implemented, see `webstaffr/workers/angel/voice.py`)
- `GHL_API_KEY`, `GHL_LOCATION_ID` -- enables the real `GoHighLevelClient`
- `WEBSTAFFR_DB_PATH` -- SQLite file path (default `webstaffr.db`; Docker sets this to `/data/webstaffr.db`)

See `CLAUDE.md` for how this repository is governed, `PROJECT.md`/`ARCHITECTURE.md` for product and system design, and `DECISIONS.md` for the record of why things are built the way they are.
