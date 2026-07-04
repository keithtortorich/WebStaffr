import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from webstaffr.workers.angel.ghl import NullGHLClient
from webstaffr.workers.angel.router import create_app
from webstaffr.workers.angel.voice import NullVoiceBackend


class RouterTestCase(unittest.TestCase):
    """Uses a real temp-file SQLite DB rather than ':memory:' -- each
    sqlite3.connect(':memory:') call opens an independent, empty database,
    which would hide the startup migration from the router's per-request
    connections. A temp file behaves like the real deployment (one file,
    many connections)."""

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.ghl = NullGHLClient()
        app = create_app(db_path=self.db_path, voice_backend=NullVoiceBackend(), ghl_client=self.ghl)
        self.client = TestClient(app)

    def tearDown(self):
        os.remove(self.db_path)


class TestHealthEndpoint(RouterTestCase):
    def test_health_ok(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})


class TestChatEndpoint(RouterTestCase):
    def test_chat_returns_a_reply(self):
        resp = self.client.post("/chat", json={"tenant_id": "acme", "message": "Hi there"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("reply", resp.json())
        self.assertTrue(len(resp.json()["reply"]) > 0)

    def test_chat_rejects_invalid_tenant_id(self):
        resp = self.client.post("/chat", json={"tenant_id": "", "message": "Hi there"})
        self.assertEqual(resp.status_code, 400)


class TestGHLWebhookEndpoint(RouterTestCase):
    def test_website_lead_event_is_handled(self):
        resp = self.client.post(
            "/webhooks/ghl",
            json={
                "tenant_id": "acme",
                "event_type": "website_lead",
                "contact_id": "c1",
                "contact_name": "Jane Doe",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "handled")

    def test_missed_call_event_is_handled(self):
        resp = self.client.post(
            "/webhooks/ghl",
            json={"tenant_id": "acme", "event_type": "missed_call", "contact_id": "c1"},
        )
        self.assertEqual(resp.status_code, 200)

    def test_unsupported_event_type_is_rejected(self):
        resp = self.client.post(
            "/webhooks/ghl",
            json={"tenant_id": "acme", "event_type": "not_a_real_event"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_tenant_id_is_rejected(self):
        resp = self.client.post(
            "/webhooks/ghl",
            json={"tenant_id": "bad id with spaces", "event_type": "website_lead"},
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
