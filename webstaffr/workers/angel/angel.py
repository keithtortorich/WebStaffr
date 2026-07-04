"""Angel -- the first AI Worker. Ties together the core prompt, a pluggable
voice/chat backend, appointment booking, and GHL logging.

Dependencies (voice backend, GHL client, DB connection) are injected via
the constructor rather than constructed internally, so tests can supply
Null implementations without needing real credentials or a real database
file. This is the same explicit-dependency pattern as WorkflowExecutor.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Optional

from ...tenant import Tenant
from .booking import Appointment, AppointmentRepository
from .ghl import GHLClient, NullGHLClient
from .voice import NullVoiceBackend, VoiceBackend

logger = logging.getLogger("webstaffr.angel")

_PROMPT_PATH = Path(__file__).parent / "angel_prompt.md"


def load_prompt_template() -> str:
    """Loads whatever is currently in angel_prompt.md. Swapping that file's
    content (e.g. for the founder's real prompt) requires no code change."""
    return _PROMPT_PATH.read_text()


class Angel:
    """One Angel instance handles conversation and booking for one tenant."""

    def __init__(
        self,
        tenant: Tenant,
        conn: sqlite3.Connection,
        voice_backend: Optional[VoiceBackend] = None,
        ghl_client: Optional[GHLClient] = None,
        business_name: str = "your business",
    ) -> None:
        self.tenant = tenant
        self.conn = conn
        self.voice_backend = voice_backend or NullVoiceBackend()
        self.ghl_client = ghl_client or NullGHLClient()
        self.business_name = business_name
        self._appointments = AppointmentRepository(conn)

    def build_context(self, extra: Optional[dict] = None) -> dict:
        """Dynamic context loading: assembles what Angel knows for this
        turn. Minimal for now (tenant + business name + whatever the
        caller passes in) -- this is the seam where richer per-tenant
        context (past appointments, CRM notes) plugs in later without
        changing the interface."""
        context = {
            "tenant_id": self.tenant.tenant_id,
            "business_name": self.business_name,
        }
        if extra:
            context.update(extra)
        return context

    def render_prompt(self, context: dict) -> str:
        template = load_prompt_template()
        return template.format(
            business_name=context.get("business_name", self.business_name),
            tenant_context=context.get("tenant_context", ""),
        )

    def respond(self, message: str, extra_context: Optional[dict] = None) -> str:
        """Handle one incoming message and return Angel's reply text."""
        context = self.build_context(extra_context)
        logger.info("angel_message_received tenant=%s", self.tenant.tenant_id)
        reply = self.voice_backend.respond(message, context)
        logger.info("angel_message_answered tenant=%s", self.tenant.tenant_id)
        return reply

    def book_appointment(
        self,
        contact_name: str,
        starts_at: str,
        contact_phone: Optional[str] = None,
        contact_email: Optional[str] = None,
        notes: Optional[str] = None,
        sync_to_ghl: bool = True,
        ghl_contact_id: Optional[str] = None,
    ) -> Appointment:
        """Books an appointment locally first -- that's the source of
        truth. GHL sync is best-effort and never rolls back the local
        booking if it fails; a failed sync is logged, not swallowed."""
        appt = Appointment(
            tenant_id=self.tenant.tenant_id,
            contact_name=contact_name,
            starts_at=starts_at,
            contact_phone=contact_phone,
            contact_email=contact_email,
            notes=notes,
        )
        self._appointments.save(appt)
        logger.info(
            "appointment_booked tenant=%s appointment_id=%s",
            self.tenant.tenant_id,
            appt.appointment_id,
        )

        if sync_to_ghl and ghl_contact_id:
            try:
                self.ghl_client.create_appointment(ghl_contact_id, starts_at, notes or "")
                self._appointments.mark_ghl_synced(self.tenant.tenant_id, appt.appointment_id)
                appt.ghl_synced = True
            except Exception as exc:  # noqa: BLE001 -- GHL failure must not break booking
                logger.warning(
                    "ghl_sync_failed tenant=%s appointment_id=%s error=%s",
                    self.tenant.tenant_id,
                    appt.appointment_id,
                    exc,
                )

        return appt

    def log_note_to_ghl(self, ghl_contact_id: str, note: str) -> bool:
        """Best-effort GHL note logging. Returns True/False instead of
        raising -- a note-logging failure is never allowed to break the
        conversation flow that triggered it."""
        try:
            self.ghl_client.log_note(ghl_contact_id, note)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("ghl_note_log_failed tenant=%s error=%s", self.tenant.tenant_id, exc)
            return False
