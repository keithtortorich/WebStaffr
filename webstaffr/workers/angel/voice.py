"""Voice/chat backend abstraction for Angel.

Kept as an explicit interface so Angel's logic never depends on a specific
vendor. GrokVoiceBackend requires a real API key via environment variable
and raises a clear, descriptive error if not configured -- it never
silently no-ops or fabricates a response. NullVoiceBackend is the safe
default for tests and offline/text-only operation.
"""

from __future__ import annotations

import os
from typing import Optional, Protocol


class VoiceBackendNotConfiguredError(RuntimeError):
    """Raised when a voice backend is used without its required credentials."""


class VoiceBackend(Protocol):
    def respond(self, message: str, context: dict) -> str:
        """Given an incoming message and context, return Angel's reply text."""
        ...


class NullVoiceBackend:
    """Safe default: deterministic, no external calls. Used for tests and
    for any tenant that hasn't configured a real voice backend yet."""

    def respond(self, message: str, context: dict) -> str:
        return (
            "Thanks for reaching out! I'm not fully set up to respond yet -- "
            "a real person will follow up with you shortly."
        )


class GrokVoiceBackend:
    """Realtime voice + chat via Grok. Requires GROK_API_KEY.

    This class enforces the credential requirement (fails loudly at
    construction if not configured) but does NOT implement the actual
    realtime audio transport -- that requires a live, testable Grok
    account this environment does not have. `respond` raises
    NotImplementedError rather than pretending to call a real API, so a
    caller can never mistake an untested stub for a working integration.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("GROK_API_KEY")
        if not self.api_key:
            raise VoiceBackendNotConfiguredError(
                "GrokVoiceBackend requires GROK_API_KEY to be set (env var or constructor arg). "
                "Refusing to start with no credentials rather than failing later, silently."
            )

    def respond(self, message: str, context: dict) -> str:
        raise NotImplementedError(
            "Grok realtime chat/voice is not implemented in this environment -- there is no "
            "live Grok account available here to build and verify a real integration against. "
            "The credential check above is real; wire the actual API call once credentials and "
            "Grok's API docs are available to test against."
        )
