import os
import unittest

from webstaffr.db import connect, migrate
from webstaffr.tenant import Tenant
from webstaffr.workers.angel.angel import Angel, load_prompt_template
from webstaffr.workers.angel.booking import AppointmentRepository
from webstaffr.workers.angel.ghl import (
    GHLNotConfiguredError,
    GoHighLevelClient,
    NullGHLClient,
)
from webstaffr.workers.angel.voice import (
    GrokVoiceBackend,
    NullVoiceBackend,
    VoiceBackendNotConfiguredError,
)


class AngelTestCase(unittest.TestCase):
    def setUp(self):
        self._ctx = connect(":memory:")
        self.conn = self._ctx.__enter__()
        migrate(self.conn)
        self.tenant = Tenant(tenant_id="acme")

    def tearDown(self):
        self._ctx.__exit__(None, None, None)


class TestPromptTemplate(unittest.TestCase):
    def test_prompt_template_loads_and_is_labeled_as_draft(self):
        text = load_prompt_template()
        self.assertIn("Angel", text)
        # It must be honest about being a placeholder until the real prompt exists.
        self.assertIn("DRAFT PLACEHOLDER", text)


class TestAngelRespond(AngelTestCase):
    def test_respond_uses_null_backend_by_default(self):
        angel = Angel(tenant=self.tenant, conn=self.conn)
        reply = angel.respond("Hi, can I book an appointment?")
        self.assertIsInstance(reply, str)
        self.assertTrue(len(reply) > 0)


class TestAngelBooking(AngelTestCase):
    def test_book_appointment_persists_locally(self):
        angel = Angel(tenant=self.tenant, conn=self.conn)
        appt = angel.book_appointment(
            contact_name="Jane Doe",
            starts_at="2026-08-01T15:00:00Z",
            contact_phone="555-1234",
            sync_to_ghl=False,
        )
        self.assertIsNotNone(appt.appointment_id)
        self.assertFalse(appt.ghl_synced)

        stored_ids = AppointmentRepository(self.conn).list_for_tenant("acme")
        self.assertEqual(stored_ids, [appt.appointment_id])

    def test_book_appointment_syncs_to_ghl_when_requested(self):
        ghl = NullGHLClient()
        angel = Angel(tenant=self.tenant, conn=self.conn, ghl_client=ghl)
        appt = angel.book_appointment(
            contact_name="Jane Doe",
            starts_at="2026-08-01T15:00:00Z",
            sync_to_ghl=True,
            ghl_contact_id="ghl_contact_123",
        )
        self.assertTrue(appt.ghl_synced)
        self.assertEqual(len(ghl.created_appointments), 1)

    def test_ghl_sync_failure_does_not_break_local_booking(self):
        class BoomGHLClient:
            def log_note(self, contact_id, note):
                raise RuntimeError("simulated GHL outage")

            def create_appointment(self, contact_id, starts_at, notes):
                raise RuntimeError("simulated GHL outage")

        angel = Angel(tenant=self.tenant, conn=self.conn, ghl_client=BoomGHLClient())
        appt = angel.book_appointment(
            contact_name="Jane Doe",
            starts_at="2026-08-01T15:00:00Z",
            sync_to_ghl=True,
            ghl_contact_id="ghl_contact_123",
        )
        # Local booking must still have succeeded despite the GHL failure.
        self.assertIsNotNone(appt.appointment_id)
        self.assertFalse(appt.ghl_synced)


class TestAngelGHLNotes(AngelTestCase):
    def test_log_note_to_ghl_returns_true_on_success(self):
        ghl = NullGHLClient()
        angel = Angel(tenant=self.tenant, conn=self.conn, ghl_client=ghl)
        ok = angel.log_note_to_ghl("ghl_contact_123", "Called about pricing.")
        self.assertTrue(ok)
        self.assertEqual(len(ghl.logged_notes), 1)

    def test_log_note_to_ghl_returns_false_on_failure_without_raising(self):
        class BoomGHLClient:
            def log_note(self, contact_id, note):
                raise RuntimeError("simulated GHL outage")

            def create_appointment(self, contact_id, starts_at, notes):
                raise RuntimeError("simulated GHL outage")

        angel = Angel(tenant=self.tenant, conn=self.conn, ghl_client=BoomGHLClient())
        ok = angel.log_note_to_ghl("ghl_contact_123", "Called about pricing.")
        self.assertFalse(ok)


class TestVoiceBackends(unittest.TestCase):
    def test_null_backend_responds_without_external_calls(self):
        backend = NullVoiceBackend()
        reply = backend.respond("hello", {})
        self.assertIsInstance(reply, str)

    def test_grok_backend_requires_api_key(self):
        old = os.environ.pop("GROK_API_KEY", None)
        try:
            with self.assertRaises(VoiceBackendNotConfiguredError):
                GrokVoiceBackend()
        finally:
            if old is not None:
                os.environ["GROK_API_KEY"] = old

    def test_grok_backend_accepts_explicit_key_but_respond_is_not_implemented(self):
        backend = GrokVoiceBackend(api_key="test-key")
        with self.assertRaises(NotImplementedError):
            backend.respond("hello", {})


class TestGHLClients(unittest.TestCase):
    def test_null_client_records_calls(self):
        client = NullGHLClient()
        client.log_note("c1", "note text")
        client.create_appointment("c1", "2026-08-01T15:00:00Z", "notes")
        self.assertEqual(len(client.logged_notes), 1)
        self.assertEqual(len(client.created_appointments), 1)

    def test_real_client_requires_credentials(self):
        old_key = os.environ.pop("GHL_API_KEY", None)
        old_loc = os.environ.pop("GHL_LOCATION_ID", None)
        try:
            with self.assertRaises(GHLNotConfiguredError):
                GoHighLevelClient()
        finally:
            if old_key is not None:
                os.environ["GHL_API_KEY"] = old_key
            if old_loc is not None:
                os.environ["GHL_LOCATION_ID"] = old_loc


if __name__ == "__main__":
    unittest.main()
