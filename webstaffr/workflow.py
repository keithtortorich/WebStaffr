"""Workflow Definition — an ordered sequence of steps, scoped to one Tenant.

Per ARCHITECTURE.md: every step input is treated as untrusted and validated
before execution. No secrets belong in a WorkflowDefinition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .tenant import Tenant

StepFn = Callable[[dict], dict]


class InvalidWorkflowError(ValueError):
    """Raised when a workflow definition or one of its steps is malformed."""


@dataclass(frozen=True)
class Step:
    """One step in a workflow: a name and the function it runs.

    The function receives the step's input dict and must return an output
    dict. It must not reach outside the process (no network, no disk, no
    external system) — this slice explicitly excludes external integrations.
    """

    name: str
    fn: StepFn

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvalidWorkflowError("Step name must be a non-empty string.")
        if not callable(self.fn):
            raise InvalidWorkflowError(f"Step {self.name!r} fn must be callable.")


@dataclass(frozen=True)
class WorkflowDefinition:
    """An ordered list of steps, scoped to exactly one Tenant."""

    workflow_id: str
    tenant: Tenant
    steps: tuple = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.workflow_id or not self.workflow_id.strip():
            raise InvalidWorkflowError("workflow_id must be a non-empty string.")
        if not isinstance(self.tenant, Tenant):
            raise InvalidWorkflowError("WorkflowDefinition.tenant must be a Tenant instance.")
        if not self.steps:
            raise InvalidWorkflowError(f"Workflow {self.workflow_id!r} must have at least one step.")
        names = [s.name for s in self.steps]
        if len(names) != len(set(names)):
            raise InvalidWorkflowError(f"Workflow {self.workflow_id!r} has duplicate step names: {names}")
