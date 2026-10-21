"""
Configuration Module for Lab 07 - Memory, Context Engineering & Prompt Caching.

Defines global environment paths, token budgets, execution timeouts,
and LLM runtime parameters.
"""

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass

# Đường dẫn thư mục gốc dự án (bt_buoi07_memory_context)
ROOT_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = ROOT_DIR / "data"
LOGS_DIR: Path = DATA_DIR / "logs"
MEMORY_FILE_PATH: Path = DATA_DIR / "project_memory.json"
DOCS_DIR: Path = ROOT_DIR / "docs"

# Load biến môi trường từ .env nếu có python-dotenv
try:
    import dotenv
    dotenv.load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass


@dataclass(frozen=True)
class AppConfig:
    """Cấu hình tập trung cho toàn bộ hệ thống Agent."""

    # LLM Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock").lower()
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Token Budget Limits (Dành cho Challenge B1 Compactor)
    token_budget_limit: int = int(os.getenv("TOKEN_BUDGET_LIMIT", "8000"))
    token_budget_warning_threshold: float = float(os.getenv("TOKEN_BUDGET_WARNING_THRESHOLD", "0.75"))
    token_budget_compact_target: int = int(os.getenv("TOKEN_BUDGET_COMPACT_TARGET", "3000"))

    # Runtime Execution Limits (Dành cho Challenge B2 Code Mode)
    code_exec_timeout_seconds: int = int(os.getenv("CODE_EXEC_TIMEOUT_SECONDS", "10"))

    # File paths
    root_dir: Path = ROOT_DIR
    data_dir: Path = DATA_DIR
    logs_dir: Path = LOGS_DIR
    memory_file: Path = MEMORY_FILE_PATH


config = AppConfig()
