#!/usr/bin/env python3
"""Self-healing health check for the WebStaffr in-memory workflow slice.

Run any time to verify the core components import cleanly and a minimal
smoke-test workflow still executes correctly end to end. Exits non-zero on
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
        from webstaffr.workflow import Step, WorkflowDefinition  # noqa: F401
        from webstaffr.execution import ExecutionRecord, ExecutionStatus  # noqa: F401
        from webstaffr.executor import WorkflowExecutor  # noqa: F401

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

    check("imports", check_imports)
    check("smoke_workflow_executes_and_succeeds", check_smoke_workflow)
    check("tenant_isolation_enforced", check_tenant_isolation_enforced)
    check("failed_step_degrades_gracefully", check_failed_step_does_not_crash_executor)

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
