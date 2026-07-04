"""Execution Record — the full, reconstructable trace of one workflow run.

Per ARCHITECTURE.md: an Execution Record must be sufficient to fully
reconstruct what happened in any given run.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class StepTrace:
    """The record of one executed step: input, output, timestamp, status."""

    step_name: str
    status: ExecutionStatus
    input: dict
    output: Optional[dict] = None
    error: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None
    attempts: int = 0


@dataclass
class ExecutionRecord:
    """Belongs to one Tenant; references one WorkflowDefinition; holds the
    full step-by-step trace of a single run."""

    tenant_id: str
    workflow_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    steps: list = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None

    def record_step(self, trace: StepTrace) -> None:
        self.steps.append(trace)

    def to_dict(self) -> dict:
        """Serialize for logging/inspection — no persistence implied."""
        return {
            "tenant_id": self.tenant_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "steps": [
                {
                    "step_name": t.step_name,
                    "status": t.status.value,
                    "input": t.input,
                    "output": t.output,
                    "error": t.error,
                    "started_at": t.started_at,
                    "finished_at": t.finished_at,
                    "attempts": t.attempts,
                }
                for t in self.steps
            ],
        }
