#!/usr/bin/env python3
"""Self-healing health check for the WebStaffr in-memory + SQLite slice.

Run any time to verify the core components import cleanly, a minimal
smoke-test workflow still executes correctly end to end, and the SQLite
persistence layer can migrate, save, and load correctly. Exits non-zero on
any failure so it can be wired into CI later without modification.

Per CLAUDE.md's Key Practices: self-healing scripts validate system health
and every check performed is logged to stdout.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    checks = []

    def check(name, fn):
        try:
            fn()
            checks.append((name, True, ""))
        except Exception as exc:  # noqa: BLE001
            checks.append((name, False, f"{type(exc).__name__}: {exc}"))

    def check_imports():
        from webstaffr.tenant import Tenant  # noqa: F401
        from webstaffr.workflow import Step, WorkflowDefinition, StepRegistry  # noqa: F401
        from webstaffr.execution import ExecutionRecord, ExecutionStatus  # noqa: F401
        from webstaffr.executor import WorkflowExecutor  # noqa: F401
        from webstaffr.db import connect, migrate  # noqa: F401
        from webstaffr.repository import WorkflowRepository, ExecutionRepository  # noqa: F401

    def check_smoke_workflow():
        from webstaffr.tenant import Tenant
        from webstaffr.workflow import Step, WorkflowDefinition
        from webstaffr.execution import ExecutionStatus
        from webstaffr.executor import WorkflowExecutor

        tenant = Tenant(tenant_id="healthcheck")
        workflow = WorkflowDefinition(
            workflow_id="smoke_test",
            tenant=tenant,
            steps=(
                Step("double", lambda d: {"value": d["value"] * 2}),
                Step("add_ten", lambda d: {"value": d["value"] + 10}),
            ),
        )
        record = WorkflowExecutor().run(tenant, workflow, {"value": 5})
        assert record.status == ExecutionStatus.SUCCEEDED, f"unexpected status: {record.status}"
        assert record.steps[-1].output == {"value": 20}, f"unexpected output: {record.steps[-1].output}"

    def check_tenant_isolation_enforced():
        from webstaffr.tenant import Tenant
        from webstaffr.workflow import Step, WorkflowDefinition
        from webstaffr.executor import WorkflowExecutor, TenantScopeViolation

        tenant_a = Tenant(tenant_id="tenant_a")
        tenant_b = Tenant(tenant_id="tenant_b")
        workflow = WorkflowDefinition(
            workflow_id="wf",
            tenant=tenant_a,
            steps=(Step("noop", lambda d: d),),
        )
        try:
            WorkflowExecutor().run(tenant_b, workflow, {})
            raise AssertionError("expected TenantScopeViolation, none raised")
        except TenantScopeViolation:
            pass

    def check_failed_step_does_not_crash_executor():
        from webstaffr.tenant import Tenant
        from webstaffr.workflow import Step, WorkflowDefinition
        from webstaffr.execution import ExecutionStatus
        from webstaffr.executor import WorkflowExecutor

        def boom(_d):
            raise RuntimeError("intentional failure for health check")

        tenant = Tenant(tenant_id="healthcheck")
        workflow = WorkflowDefinition(
            workflow_id="failure_smoke_test",
            tenant=tenant,
            steps=(Step("boom", boom),),
        )
        record = WorkflowExecutor().run(tenant, workflow, {})
        assert record.status == ExecutionStatus.FAILED
        assert "intentional failure" in record.steps[-1].error

    def check_sqlite_persistence_round_trip():
        from webstaffr.tenant import Tenant
        from webstaffr.workflow import Step, StepRegistry, WorkflowDefinition
        from webstaffr.execution import ExecutionStatus
        from webstaffr.executor import WorkflowExecutor
        from webstaffr.db import connect, migrate
        from webstaffr.repository import ExecutionRepository, WorkflowRepository

        with connect(":memory:") as conn:
            applied = migrate(conn)
            assert isinstance(applied, list)

            tenant = Tenant(tenant_id="healthcheck")
            registry = StepRegistry()
            registry.register("double", lambda d: {"value": d["value"] * 2})

            workflow = WorkflowDefinition(
                workflow_id="persist_smoke_test",
                tenant=tenant,
                steps=(Step("double", registry.get("double")),),
            )
            WorkflowRepository(conn).save(workflow)
            loaded_workflow = WorkflowRepository(conn).load(
                "healthcheck", "persist_smoke_test", registry
            )
            assert loaded_workflow is not None, "workflow failed to round-trip"

            record = WorkflowExecutor().run(tenant, loaded_workflow, {"value": 4})
            assert record.status == ExecutionStatus.SUCCEEDED

            execution_id = ExecutionRepository(conn).save(record)
            loaded_record = ExecutionRepository(conn).load("healthcheck", execution_id)
            assert loaded_record is not None, "execution record failed to round-trip"
            assert loaded_record.steps[-1].output == {"value": 8}

            # Tenant isolation must hold at the storage layer too.
            assert WorkflowRepository(conn).load("someone_else", "persist_smoke_test", registry) is None

    check("imports", check_imports)
    check("smoke_workflow_executes_and_succeeds", check_smoke_workflow)
    check("tenant_isolation_enforced", check_tenant_isolation_enforced)
    check("failed_step_degrades_gracefully", check_failed_step_does_not_crash_executor)
    check("sqlite_persistence_round_trip", check_sqlite_persistence_round_trip)

    print("WebStaffr health check")
    print("=" * 40)
    all_ok = True
    for name, ok, error in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}" + (f" -- {error}" if error else ""))
        all_ok = all_ok and ok

    print("=" * 40)
    print("Result: " + ("HEALTHY" if all_ok else "UNHEALTHY"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
