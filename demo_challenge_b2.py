"""Challenge B2 demo (Thái Hưng): a fixed sample script, no LLM/API calls.

Token counts estimate context payload sizes, not actual multi-turn API usage.
"""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from rich.console import Console
from rich.table import Table
from src.config import LOGS_DIR, ROOT_DIR
from src.code_mode import CodeExecutionRuntime, CodeModeToolsProxy
from src.core_agent import estimate_tokens
from src.mock_env import generate_mock_server_logs


ANALYSIS_CODE = r'''
import re
import json
from collections import Counter
counts = Counter()
files = tools.list_files()
parsed = 0
skipped = 0
pattern = re.compile(r"^\[([^\]]+)\]\s+\[([^\]]+)\]\s+\[?(/[^\s\]]+)\]?\s+status=(\d{3})\b")
for filename in files:
    for line in tools.read_file(filename).splitlines():
        match = pattern.match(line)
        if not match:
            skipped += 1
            continue
        parsed += 1
        if 500 <= int(match.group(4)) < 600:
            counts[match.group(3)] += 1
print(json.dumps({"files": len(files), "parsed_lines": parsed,
                  "skipped_lines": skipped, "total_5xx": sum(counts.values()),
                  "top_5": sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:5]}))
'''.strip()


def _fallback_logs(target_dir: Path) -> None:
    """Temporary deterministic fixture until the shared generator is implemented."""
    endpoints = ["/api/auth", "/api/orders", "/api/users", "/api/payments", "/api/search", "/health"]
    statuses = [200, 200, 401, 429, 500, 502, 504]
    for server in range(1, 21):
        lines = []
        for index in range(200):
            status = statuses[(server + index) % len(statuses)]
            endpoint = endpoints[(server * 3 + index) % len(endpoints)]
            level = "ERROR" if status >= 500 else "INFO"
            lines.append(f"[2026-01-01T00:{index // 60:02d}:{index % 60:02d}Z] "
                         f"[{level}] [{endpoint}] status={status} latency={index + 1}ms - request completed\n")
        (target_dir / f"server_{server:02d}.log").write_text("".join(lines), encoding="utf-8")


def _token_count(text: str) -> int:
    try:
        return estimate_tokens(text)
    except NotImplementedError:
        return (len(text) + 3) // 4


def _show_demo(logs_dir: Path, console: Console) -> None:
    runtime = CodeExecutionRuntime()
    runtime.tools_proxy = CodeModeToolsProxy(logs_dir)
    result = runtime.run_code(ANALYSIS_CODE)
    if not result.success:
        raise RuntimeError(f"Code Mode failed: {result.error}\n{result.output}")
    summary = json.loads(result.output)
    if summary["files"] != 20 or not summary["parsed_lines"]:
        raise ValueError("Demo requires 20 log files with valid records in the specified format")
    table = Table(title="Top 5 endpoints with HTTP 5xx errors")
    table.add_column("Endpoint")
    table.add_column("Count", justify="right")
    for endpoint, count in summary["top_5"]:
        table.add_row(endpoint, str(count))
    console.print(table)
    console.print(f"Files: {summary['files']} | Parsed: {summary['parsed_lines']} | "
                  f"Skipped: {summary['skipped_lines']} | Total 5xx: {summary['total_5xx']}")
    # Local measurement only: raw contents are never sent to an LLM.
    native_tokens = sum(_token_count(runtime.tools_proxy.read_file(name))
                        for name in runtime.tools_proxy.list_files())
    summary_tokens = _token_count(result.output)
    code_tokens = _token_count(ANALYSIS_CODE)
    # A stated example rate makes the comparison reproducible without implying
    # a current price for any particular LLM provider.
    illustrative_usd_per_million = 1.0
    comparison = Table(title="Estimated context payload and illustrative input cost")
    comparison.add_column("Approach")
    comparison.add_column("Tokens", justify="right")
    comparison.add_column("USD at $1 / 1M tokens", justify="right")
    for label, tokens in (
        ("Native: raw log tool results", native_tokens),
        ("Code Mode: summary tool result", summary_tokens),
        ("Code Mode: script + summary", code_tokens + summary_tokens),
    ):
        comparison.add_row(label, str(tokens), f"${tokens * illustrative_usd_per_million / 1_000_000:.6f}")
    console.print(comparison)
    savings = 100 * (1 - (code_tokens + summary_tokens) / native_tokens) if native_tokens else 0
    console.print(f"Context reduction including script: {savings:.2f}%")
    console.print(f"Runtime: {result.execution_time_ms:.1f} ms")
    console.print("Token estimates: shared counter, or ceil(characters / 4) while it is unfinished.")
    console.print("Cost uses an illustrative input rate of $1 per million tokens, not a provider quote.")
    console.print("Common prompts, tool schemas and cumulative conversation costs are excluded.")


def run_challenge_b2_demo() -> None:
    console = Console()
    console.print("=== CHALLENGE B2: CODE MODE ===")
    if LOGS_DIR.is_dir() and any(LOGS_DIR.glob("*.log")):
        console.print("Data source: existing project logs")
        _show_demo(LOGS_DIR, console)
        return
    with TemporaryDirectory(prefix="challenge_b2_", dir=ROOT_DIR) as temporary:
        logs_dir = Path(temporary)
        try:
            generate_mock_server_logs(target_dir=logs_dir, num_files=20)
            console.print("Data source: shared generator (temporary directory)")
        except NotImplementedError:
            _fallback_logs(logs_dir)
            console.print("Data source: temporary B2 fixture; shared log generator is unfinished")
        _show_demo(logs_dir, console)


if __name__ == "__main__":
    run_challenge_b2_demo()
