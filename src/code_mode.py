"""Challenge B2 runtime (Thái Hưng).

Disposable processes enforce timeouts. Restricted Python is for teaching,
not an OS security sandbox for executing hostile code.
"""
from __future__ import annotations
import ast
import builtins
import contextlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
from typing import List, Optional
from pydantic import BaseModel, Field
from src.config import config, LOGS_DIR


class CodeModeToolsProxy:
    """Read-only access confined to the configured log directory."""
    def __init__(self, logs_dir: Path = LOGS_DIR) -> None:
        self.logs_dir: Path = Path(logs_dir).resolve()

    def list_files(self, extension: str = ".log") -> List[str]:
        return sorted(p.name for p in self.logs_dir.iterdir()
                      if p.name.endswith(extension) and p.is_file()
                      and p.resolve().is_relative_to(self.logs_dir))

    def read_file(self, filename: str) -> str:
        requested = Path(filename)
        if requested.is_absolute() or ".." in requested.parts:
            raise ValueError("Only relative paths inside the log directory are allowed")
        path = (self.logs_dir / requested).resolve()
        if not path.is_relative_to(self.logs_dir):
            raise ValueError("File escapes the log directory")
        return path.read_text(encoding="utf-8")


class CodeExecutionResult(BaseModel):
    success: bool = Field(..., description="Execution succeeded")
    output: str = Field(..., description="Captured stdout and traceback on failure")
    execution_time_ms: float = Field(default=0.0, description="Elapsed wall time in ms")
    error: Optional[str] = Field(default=None, description="Exception details")


class _LimitedOutput(io.StringIO):
    def write(self, value: str) -> int:
        if self.tell() + len(value) > 64000:
            raise ValueError("Output exceeds 64000 characters; print a summary")
        return super().write(value)


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if level or name not in {"collections", "json", "math", "re", "statistics"}:
        raise ImportError(f"Import not allowed: {name}")
    return builtins.__import__(name, globals, locals, fromlist, level)


def _execute_worker(code: str, logs_dir: str) -> dict:
    output = _LimitedOutput()
    try:
        tree = ast.parse(code, filename="<code-mode>")
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
                raise ValueError("Private attribute access is not allowed")
            if isinstance(node, ast.Name) and node.id.startswith("__"):
                raise ValueError("Dunder names are not allowed")
        names = ("abs all any bool dict enumerate filter float int isinstance len list "
                 "map max min next print range reversed round set sorted str sum tuple zip "
                 "Exception ValueError TypeError RuntimeError").split()
        safe_builtins = {name: getattr(builtins, name) for name in names}
        safe_builtins["__import__"] = _safe_import
        namespace = {"__builtins__": safe_builtins, "tools": CodeModeToolsProxy(Path(logs_dir))}
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(compile(tree, "<code-mode>", "exec"), namespace)
        return {"success": True, "output": output.getvalue(), "error": None}
    except BaseException as exc:
        return {"success": False, "output": output.getvalue() + traceback.format_exc(),
                "error": f"{type(exc).__name__}: {exc}"}


class CodeExecutionRuntime:
    def __init__(self, timeout_seconds: int = config.code_exec_timeout_seconds) -> None:
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive and finite")
        self.timeout_seconds: int = timeout_seconds
        self.tools_proxy = CodeModeToolsProxy()

    def run_code(self, code: str) -> CodeExecutionResult:
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "src.code_mode"],
                input=json.dumps({"code": code, "logs_dir": str(self.tools_proxy.logs_dir)}),
                capture_output=True, text=True, encoding="utf-8", timeout=self.timeout_seconds,
                cwd=Path(__file__).resolve().parent.parent,
            )
            if completed.returncode:
                result = {"success": False, "output": completed.stderr,
                          "error": f"Worker exited with code {completed.returncode}"}
            else:
                result = json.loads(completed.stdout)
        except subprocess.TimeoutExpired:
            result = {"success": False, "output": "",
                      "error": f"TimeoutError: exceeded {self.timeout_seconds} seconds"}
        except (OSError, ValueError) as exc:
            result = {"success": False, "output": "", "error": f"{type(exc).__name__}: {exc}"}
        return CodeExecutionResult(**result, execution_time_ms=(time.perf_counter() - started) * 1000)


if __name__ == "__main__":
    request = json.load(sys.stdin)
    print(json.dumps(_execute_worker(request["code"], request["logs_dir"])))
