"""
Demo Challenge B1: Context Compaction Pipeline & Structured Checkpoint.
Phụ trách: Thành viên 4 - Huy Phát.

Mô phỏng session dài với source code và test log, sau đó chạy eval suite
10 cases cho Context Compaction và Structured Checkpoint.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from src.compactor import ContextCompactor, StructuredCheckpoint
from src.core_agent import AgentMessage, CoreAgent


def _make_mock_source_code(total_lines: int = 2000) -> str:
    lines = [
        "# Simulated auth_service.py",
        "class AuthService:",
        "    def refresh_access_token(self, refresh_token):",
        "        # Concurrent refreshes can both pass validation and rotate the token.",
        "        return self.token_store.rotate(refresh_token)",
    ]
    lines.extend(
        f"    # Simulated auth helper implementation line {line_number:04d} "
        "preserved in the oversized source dump."
        for line_number in range(len(lines), total_lines)
    )
    return "\n".join(lines)


def _make_mock_test_logs(total_lines: int = 7000) -> str:
    header = [
        "============================= test session starts =============================",
        "Platform: simulated Python test environment",
        "Collected 6988 tests",
        "============================= test progress =============================",
    ]
    failures = [
        "=================================== FAILURES ===================================",
        "test_refresh_token_concurrent_requests",
        "AssertionError: refresh-token race condition: two requests rotated the same token",
        "Observed: one request returned a stale access token after refresh.",
        "Increasing token TTL did not resolve the refresh-token race condition.",
        "=========================== short test summary info ============================",
        "FAILED tests/test_auth_service.py::test_refresh_token_concurrent_requests",
        "1 failed, 6987 passed",
        "The refresh operation needs an atomic distributed lock.",
    ]
    passed_count = max(0, total_lines - len(header) - len(failures))
    passed = [
        f"tests/test_auth_service.py::test_case_{index:05d} PASSED "
        "in 0.01s (routine test output repeated for context-bloat simulation)"
        for index in range(passed_count)
    ]
    lines = header + passed + failures
    return "\n".join(lines[:total_lines])


def run_eval_suite(
    compactor: ContextCompactor,
    agent_messages: List[AgentMessage],
    system_prompt: str,
) -> bool:
    """Run ten independent checks and print their results in a Rich table."""
    console = Console()
    baseline_result: Optional[
        Tuple[List[AgentMessage], StructuredCheckpoint, Dict[str, Any]]
    ] = None

    def get_baseline() -> Tuple[
        List[AgentMessage], StructuredCheckpoint, Dict[str, Any]
    ]:
        nonlocal baseline_result
        if baseline_result is None:
            baseline_result = compactor.run_pipeline(
                messages=agent_messages,
                base_system_prompt=system_prompt,
                active_rules=[
                    "Never repeat a failed attempt recorded in the checkpoint.",
                    "Use an atomic lock for concurrent refresh-token rotation.",
                ],
            )
        return baseline_result

    def case_remembers_race_condition() -> bool:
        _, checkpoint, _ = get_baseline()
        return any(
            "refresh-token race condition" in finding.lower()
            for finding in checkpoint.findings
        )

    def case_records_ttl_failure() -> bool:
        _, checkpoint, _ = get_baseline()
        return any("ttl" in attempt.lower() for attempt in checkpoint.failed_attempts)

    def case_suggests_lock() -> bool:
        _, checkpoint, _ = get_baseline()
        action = checkpoint.next_action.lower()
        return "redis" in action and ("lock" in action or "redlock" in action) or (
            "database lock" in action or "db lock" in action
        )

    def case_has_seven_nonempty_fields() -> bool:
        _, checkpoint, _ = get_baseline()
        for value in checkpoint.model_dump().values():
            if isinstance(value, str) and not value.strip():
                return False
            if isinstance(value, list) and not value:
                return False
        return len(checkpoint.model_dump()) == 7

    def case_drops_passed_lines() -> bool:
        test_logs = next(
            message.content
            for message in agent_messages
            if message.role == "tool" and message.name == "mock_run_tests"
        )
        pruned = compactor.prune_tool_output(test_logs)
        return "PASSED" not in pruned and "refresh-token race condition" in pruned

    def case_reduces_context_over_ninety_percent() -> bool:
        _, _, metrics = get_baseline()
        return metrics["reduction_percent"] > 90

    def case_handles_empty_messages() -> bool:
        compacted, checkpoint, metrics = compactor.run_pipeline([], system_prompt)
        return (
            len(compacted) == 2
            and bool(checkpoint.goal.strip())
            and metrics["initial_tokens"] == 0
        )

    def case_handles_passed_only_logs() -> bool:
        passed_only = "\n".join(
            f"tests/test_only_passed.py::test_{index} PASSED" for index in range(100)
        )
        pruned = compactor.prune_tool_output(passed_only)
        return "PASSED" not in pruned and "dropped 100" in pruned

    def case_handles_double_sized_payload() -> bool:
        doubled_messages = [
            message.model_copy(
                update={"content": message.content * 2}
            ) if message.role == "tool" and message.name == "mock_run_tests"
            else message
            for message in agent_messages
        ]
        _, checkpoint, metrics = compactor.run_pipeline(
            messages=doubled_messages,
            base_system_prompt=system_prompt,
        )
        return (
            metrics["initial_tokens"] > 0
            and metrics["final_tokens"] < metrics["initial_tokens"]
            and metrics["reduction_percent"] > 90
            and any(
                "refresh-token race condition" in finding.lower()
                for finding in checkpoint.findings
            )
        )

    def case_rejects_incomplete_custom_checkpoint() -> bool:
        incomplete_checkpoint = {
            "goal": "Fix token refresh concurrency.",
            "current_state": "Concurrent refresh calls race.",
            "constraints": ["Do not change token TTL."],
            "findings": ["Token rotation needs atomic coordination."],
            "failed_attempts": ["Increasing token TTL did not fix the race."],
            "files": ["src/auth_service.py"],
        }
        try:
            compactor.build_structured_checkpoint(
                messages=[],
                custom_checkpoint=incomplete_checkpoint,
            )
        except ValidationError:
            return True
        return False

    cases: List[Tuple[str, str, Callable[[], bool]]] = [
        ("B1-01", "Remembers refresh-token race condition", case_remembers_race_condition),
        ("B1-02", "Records increasing TTL as a failed attempt", case_records_ttl_failure),
        ("B1-03", "Suggests a Redis or database lock", case_suggests_lock),
        ("B1-04", "Checkpoint has all 7 fields populated", case_has_seven_nonempty_fields),
        ("B1-05", "Removes repetitive PASSED test log lines", case_drops_passed_lines),
        ("B1-06", "Compression reduces tokens by more than 90%", case_reduces_context_over_ninety_percent),
        ("B1-07", "Empty input messages do not crash", case_handles_empty_messages),
        ("B1-08", "PASSED-only logs are safely compacted", case_handles_passed_only_logs),
        ("B1-09", "Double-sized log payload is handled safely", case_handles_double_sized_payload),
        ("B1-10", "Incomplete custom checkpoint is rejected", case_rejects_incomplete_custom_checkpoint),
    ]

    table = Table(title="Challenge B1 Eval Suite")
    table.add_column("Case ID", style="cyan", no_wrap=True)
    table.add_column("Description")
    table.add_column("Status (PASSED/FAILED)", justify="center")

    failures: List[Tuple[str, str]] = []
    for case_id, description, check in cases:
        try:
            passed = check()
            error = ""
        except Exception as exc:
            passed = False
            error = f"{type(exc).__name__}: {exc}"

        status = "PASSED" if passed else "FAILED"
        table.add_row(
            case_id,
            description,
            f"[green]{status}[/green]" if passed else f"[red]{status}[/red]",
        )
        if not passed:
            failures.append((case_id, error or "Case condition was not satisfied."))

    console.print(table)
    if failures:
        for case_id, error in failures:
            console.print(f"[red]{case_id} detail:[/red] {error}")
    passed_count = len(cases) - len(failures)
    console.print(
        f"Eval result: [bold]{passed_count}/{len(cases)} passed[/bold]"
    )
    return not failures


def run_challenge_b1_demo() -> None:
    """Build the oversized mock session and run the ten-case eval suite."""
    print("=== CHALLENGE B1: CONTEXT COMPACTION ===")
    system_prompt = (
        "You are a software engineering agent. Preserve verified findings, "
        "honor constraints, and continue from the checkpoint."
    )
    agent = CoreAgent(system_prompt=system_prompt)
    agent.messages.extend(
        [
            AgentMessage(
                role="user",
                content=(
                    "Goal: Fix the refresh-token race condition.\n"
                    "Current state: Concurrent refresh requests can rotate the same token "
                    "and return a stale access token.\n"
                    "Constraint: Do not increase token TTL as a workaround.\n"
                    "Constraint: Preserve token rotation and authentication behavior.\n"
                    "Constraint: Add a concurrency regression test.\n"
                    "Finding: refresh_access_token has no atomic coordination around rotation.\n"
                    "Failed attempt: Increasing token TTL did not resolve the race condition.\n"
                    "File: src/auth_service.py\n"
                    "File: tests/test_auth_service.py\n"
                    "Next action: Implement a distributed lock using Redis Redlock or a "
                    "database lock, then add a concurrency regression test."
                ),
            ),
            AgentMessage(
                role="tool",
                name="mock_read_file",
                content=_make_mock_source_code(total_lines=2000),
            ),
            AgentMessage(
                role="tool",
                name="mock_run_tests",
                content=_make_mock_test_logs(total_lines=7000),
            ),
        ]
    )

    compactor = ContextCompactor()
    passed = run_eval_suite(compactor, agent.messages, system_prompt)
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    run_challenge_b1_demo()
