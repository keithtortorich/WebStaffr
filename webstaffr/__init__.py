"""WebStaffr — first implementation slice: internal workflow execution.

Per ARCHITECTURE.md's minimal design and DECISIONS.md's recorded scope:
three in-memory-shaped components (Tenant, WorkflowDefinition,
WorkflowExecutor) plus an ExecutionRecord. No stack, hosting, database, or
external-integration choice is made or implied by this package.
"""

__all__ = ["tenant", "workflow", "execution", "executor"]
