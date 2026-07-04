## OWNED_BY: CLAUDE
"""FastAPI webhook handler for GoHighLevel events. Starts an Angel session
for the relevant tenant when GHL sends a website-lead or missed-call event.

Kept intentionally thin: the router's job is to validate the incoming
payload, resolve a Tenant, and hand off to Angel -- not to contain Angel's
own logic.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ...db import connect, migrate
from ...tenant import InvalidTenantError, Tenant
from .angel import Angel
from .ghl import GHLClient
from .voice import VoiceBackend

logger = logging.getLogger("webstaffr.angel.router")


class GHLWebhookEvent(BaseModel):
    """Minimal shape of the GHL events this router handles. GHL's real
    payloads carry more fields than this -- extra fields are ignored by
    pydantic by default, so this stays intentionally narrow to what Angel
    actually needs, carrying forward the "treat external input as
    untrusted, validate before use" principle from the core executor."""

    tenant_id: str
    event_type: str  # e.g. "website_lead", "missed_call"
    contact_id: Optional[str] = None
    contact_name: Optional[str] = None
    message: Optional[str] = None


class ChatRequest(BaseModel):
    tenant_id: str
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


SUPPORTED_EVENT_TYPES = {"website_lead", "missed_call"}


def create_app(
    db_path: str = "webstaffr.db",
    voice_backend: Optional[VoiceBackend] = None,
    ghl_client: Optional[GHLClient] = None,
) -> FastAPI:
    """Factory rather than a module-level app instance, so tests (and
    Docker, and any future multi-tenant deployment shape) can construct an
    app pointed at a specific database and specific backends instead of
    relying on hidden global state."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        with connect(db_path) as conn:
            migrate(conn)
        yield

    app = FastAPI(title="WebStaffr Angel Router", lifespan=lifespan)

    # The widget is embedded on customer websites (arbitrary origins), so it
    # needs CORS enabled for the endpoints it calls. Scoped to /chat only in
    # spirit -- FastAPI's CORS middleware is app-wide, so this is revisited
    # if/when an endpoint here should NOT be publicly callable cross-origin.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )

    def get_connection() -> sqlite3.Connection:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/chat", response_model=ChatResponse)
    def chat(req: ChatRequest) -> ChatResponse:
        """Used by angel-widget.js on generated customer sites -- a direct
        chat turn, separate from the GHL webhook flow above."""
        try:
            tenant = Tenant(tenant_id=req.tenant_id)
        except InvalidTenantError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        conn = get_connection()
        try:
            angel = Angel(tenant=tenant, conn=conn, voice_backend=voice_backend, ghl_client=ghl_client)
            reply = angel.respond(req.message)
            conn.commit()
        finally:
            conn.close()

        logger.info("chat_handled tenant=%s", req.tenant_id)
        return ChatResponse(reply=reply)

    @app.post("/webhooks/ghl")
    def ghl_webhook(event: GHLWebhookEvent) -> dict:
        try:
            tenant = Tenant(tenant_id=event.tenant_id)
        except InvalidTenantError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        if event.event_type not in SUPPORTED_EVENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported event_type: {event.event_type!r}. "
                f"Supported: {sorted(SUPPORTED_EVENT_TYPES)}",
            )

        conn = get_connection()
        try:
            angel = Angel(
                tenant=tenant,
                conn=conn,
                voice_backend=voice_backend,
                ghl_client=ghl_client,
            )
            reply = angel.respond(
                event.message or f"New {event.event_type} from {event.contact_name or 'a contact'}.",
                extra_context={"event_type": event.event_type, "contact_id": event.contact_id},
            )
            conn.commit()
        finally:
            conn.close()

        logger.info(
            "ghl_webhook_handled tenant=%s event_type=%s",
            event.tenant_id,
            event.event_type,
        )
        return {"status": "handled", "reply": reply}

    return app


def _backend_from_env() -> Optional[VoiceBackend]:
    """GrokVoiceBackend only if GROK_API_KEY is actually set -- otherwise
    None, so create_app() falls back to NullVoiceBackend. Never silently
    construct a backend that will fail on first real use."""
    import os

    if os.environ.get("GROK_API_KEY"):
        from .voice import GrokVoiceBackend

        return GrokVoiceBackend()
    return None


def _ghl_client_from_env() -> Optional[GHLClient]:
    import os

    if os.environ.get("GHL_API_KEY") and os.environ.get("GHL_LOCATION_ID"):
        from .ghl import GoHighLevelClient

        return GoHighLevelClient()
    return None


# Default app instance for `uvicorn webstaffr.workers.angel.router:app`.
# db_path and backends are picked up from environment at process start --
# see Dockerfile (WEBSTAFFR_DB_PATH) and docker-compose.yml (credentials).
import os as _os  # noqa: E402

app = create_app(
    db_path=_os.environ.get("WEBSTAFFR_DB_PATH", "webstaffr.db"),
    voice_backend=_backend_from_env(),
    ghl_client=_ghl_client_from_env(),
)
