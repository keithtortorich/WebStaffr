"""WebStaffr — first implementation slice: internal workflow execution.

Per ARCHITECTURE.md's minimal design and DECISIONS.md's recorded scope:
three core components (Tenant, WorkflowDefinition, WorkflowExecutor) plus
an ExecutionRecord, with an additive SQLite persistence layer (db,
repository, StepRegistry). No hosting, auth, or external-integration
choice is made or implied by this package.
"""

__all__ = ["tenant", "workflow", "execution", "executor", "db", "repository"]
