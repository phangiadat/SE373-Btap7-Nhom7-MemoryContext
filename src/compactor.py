"""
Context Compactor and Structured Checkpoint Module.
Phụ trách: Thành viên 4 - Huy Phát.

MỤC TIÊU CỦA HUY PHÁT:
1. Định nghĩa Pydantic Schema StructuredCheckpoint với đủ 7 trường bắt buộc:
   - goal: str (Mục tiêu tổng quát)
   - current_state: str (Hiện trạng lỗi/hệ thống)
   - constraints: List[str] (Ràng buộc kỹ thuật)
   - findings: List[str] (Phát hiện từ code/log)
   - failed_attempts: List[str] (Cách đã thử nhưng thất bại - KHÔNG ĐƯỢC LẶP LẠI)
   - files: List[str] (Các file liên quan)
   - next_action: str (Hành động cụ thể kế tiếp)
2. Áp dụng Selective Compaction (KEEP / TRUNCATE / DROP):
   - KEEP: Quyết định kiến trúc, lỗi đang điều tra, ràng buộc.
   - TRUNCATE: Thu gọn log test hàng ngàn dòng còn các dòng lỗi chính và summary.
   - DROP: Loại bỏ hàng ngàn dòng test PASSED rườm rà và debug log lặp lại.
3. Cài đặt Context Compaction Pipeline 5 bước chuẩn mực:
   - Bước 1: observe_token_budget()
   - Bước 2: prune_tool_output()
   - Bước 3: build_structured_checkpoint()
   - Bước 4: reinject_rules_and_plan()
   - Bước 5: run_pipeline()
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from src.core_agent import AgentMessage
from src.config import config

try:
    import tiktoken
except ImportError:
    tiktoken = None


class StructuredCheckpoint(BaseModel):
    """
    Schema cấu trúc 7 trường thông tin cốt lõi bảo toàn trạng thái suy luận của Agent.
    """
    goal: str = Field(..., description="Mục tiêu tối thượng của task đang thực thi")
    current_state: str = Field(..., description="Trạng thái hiện tại của quá trình giải quyết vấn đề")
    constraints: List[str] = Field(default_factory=list, description="Các ràng buộc kỹ thuật bắt buộc phải tuân theo")
    findings: List[str] = Field(default_factory=list, description="Các phát hiện quan trọng từ quá trình đọc log/code")
    failed_attempts: List[str] = Field(default_factory=list, description="Các phương án đã thử nghiệm nhưng thất bại (tránh lặp lại)")
    files: List[str] = Field(default_factory=list, description="Các file liên quan trực tiếp đến vấn đề")
    next_action: str = Field(..., description="Hành động cụ thể kế tiếp cần thực hiện ngay")


class TokenBudgetReport(BaseModel):
    """Báo cáo phân tích ngân sách token."""
    current_tokens: int
    limit_tokens: int
    usage_ratio: float
    needs_compaction: bool


class ContextCompactor:
    """
    Pipeline nén ngữ cảnh chọn lọc (Selective Context Compactor).
    """

    def __init__(
        self,
        token_budget_limit: int = config.token_budget_limit,
        warning_threshold: float = config.token_budget_warning_threshold,
    ) -> None:
        if token_budget_limit <= 0:
            raise ValueError("token_budget_limit must be greater than zero")
        if not 0 <= warning_threshold <= 1:
            raise ValueError("warning_threshold must be between 0 and 1")
        self.token_budget_limit: int = token_budget_limit
        self.warning_threshold: float = warning_threshold

    @staticmethod
    def _content_of(message: Any) -> str:
        if isinstance(message, dict):
            content = message.get("content", "")
        else:
            content = getattr(message, "content", "")
        return content if isinstance(content, str) else str(content)

    @staticmethod
    def _role_of(message: Any) -> str:
        if isinstance(message, dict):
            return str(message.get("role", ""))
        return str(getattr(message, "role", ""))

    @staticmethod
    def _estimate_text_tokens(text: str) -> int:
        if not text:
            return 0
        if tiktoken is not None:
            try:
                return len(tiktoken.get_encoding("cl100k_base").encode(text))
            except (LookupError, ValueError):
                pass
        return math.ceil(len(text) / 4)

    def observe_token_budget(self, messages: List[AgentMessage]) -> TokenBudgetReport:
        """
        Bước 1: Đo lường ngân sách token hiện tại.
        
        Token count is based on message content; message framing overhead is not
        included because this project uses provider-independent mock messages.
        """
        current_tokens = sum(
            self._estimate_text_tokens(self._content_of(message))
            for message in messages
        )
        usage_ratio = current_tokens / self.token_budget_limit
        return TokenBudgetReport(
            current_tokens=current_tokens,
            limit_tokens=self.token_budget_limit,
            usage_ratio=usage_ratio,
            needs_compaction=usage_ratio >= self.warning_threshold,
        )

    def prune_tool_output(self, raw_output: str, max_lines_kept: int = 40) -> str:
        """
        Bước 2: Cắt gọt output công cụ lớn (Áp dụng TRUNCATE và DROP).
        
        Repeated PASSED rows are dropped. Headers and high-signal error lines
        are preferred when a large output must also be truncated.
        """
        if max_lines_kept < 1:
            raise ValueError("max_lines_kept must be at least 1")
        lines = raw_output.splitlines()
        if not lines:
            return raw_output

        passed_pattern = re.compile(r"\bPASSED\b", re.IGNORECASE)
        passed_count = sum(bool(passed_pattern.search(line)) for line in lines)
        non_passed = [
            (index, line)
            for index, line in enumerate(lines)
            if not passed_pattern.search(line)
        ]
        if len(lines) <= max_lines_kept and passed_count == 0:
            return raw_output

        signal_pattern = re.compile(
            r"\b(FAILURES?|ERRORS?|ERROR|EXCEPTION|TRACEBACK|ASSERTIONERROR|"
            r"WARNING|CRITICAL|TIMEOUT|RACE CONDITION|FAILED)\b",
            re.IGNORECASE,
        )
        header_pattern = re.compile(
            r"(^=+.*=+$|^[- ]{3,}$|^tests?[: ]|^running |^collected \d+)",
            re.IGNORECASE,
        )
        header_entries = [
            item for item in non_passed
            if header_pattern.search(item[1].strip())
        ][:4]
        important_entries = [
            item for item in non_passed
            if signal_pattern.search(item[1]) and item not in header_entries
        ]

        summary_lines: List[str] = []
        if passed_count:
            summary_lines.append(
                f"[Compacted: dropped {passed_count} repetitive successful test lines.]"
            )
        available = max_lines_kept - len(summary_lines)

        selected: Dict[int, str] = {}
        for index, line in header_entries + important_entries:
            if len(selected) >= available:
                break
            selected[index] = line

        if len(selected) < available:
            for index, line in non_passed:
                if index not in selected:
                    selected[index] = line
                    if len(selected) >= available:
                        break

        omitted_count = len(non_passed) - len(selected)
        if omitted_count and len(summary_lines) < max_lines_kept:
            summary_lines.append(
                f"[Compacted: omitted {omitted_count} lower-priority lines.]"
            )
            while len(selected) + len(summary_lines) > max_lines_kept:
                selected.pop(next(reversed(selected)))

        result = [selected[index] for index in sorted(selected)]
        result.extend(summary_lines)
        return "\n".join(result)

    def build_structured_checkpoint(
        self,
        messages: List[AgentMessage],
        custom_checkpoint: Optional[Any] = None,
    ) -> StructuredCheckpoint:
        """
        Bước 3: Đóng gói ngữ cảnh thành StructuredCheckpoint 7 trường.
        
        Explicitly labeled facts are retained first; high-signal lines provide
        conservative defaults when a field is not labeled in the conversation.
        """
        if isinstance(custom_checkpoint, StructuredCheckpoint):
            return custom_checkpoint.model_copy(deep=True)
        if custom_checkpoint is not None:
            return StructuredCheckpoint.model_validate(custom_checkpoint)

        text = "\n".join(self._content_of(message) for message in messages)
        labeled: Dict[str, List[str]] = {
            "goal": [],
            "current_state": [],
            "constraints": [],
            "findings": [],
            "failed_attempts": [],
            "files": [],
            "next_action": [],
        }
        label_aliases = {
            "goal": ("goal", "objective"),
            "current_state": ("current state", "status"),
            "constraints": ("constraints", "constraint"),
            "findings": ("findings", "finding"),
            "failed_attempts": ("failed attempts", "failed attempt"),
            "files": ("files", "file"),
            "next_action": ("next action", "action"),
        }
        for line in text.splitlines():
            match = re.match(r"^\s*(?:[-*]\s*)?([A-Za-z _-]+)\s*:\s*(.*?)\s*$", line)
            if not match:
                continue
            label, value = match.groups()
            normalized = label.strip().lower().replace("_", " ")
            value = value.strip().strip("`")
            for field, aliases in label_aliases.items():
                if normalized in aliases and value:
                    labeled[field].append(value)
                    break

        labeled_line_pattern = re.compile(
            r"^\s*(?:[-*]\s*)?(?:goal|objective|current state|status|"
            r"constraints?|findings?|failed attempts?|files?|file|"
            r"next action|action)\s*:",
            re.IGNORECASE,
        )
        meaningful_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
            and not labeled_line_pattern.search(line)
            and re.search(
                r"race condition|assertionerror|failed|failure|exception|"
                r"redis|redlock|database lock|refresh.?token",
                line,
                re.IGNORECASE,
            )
        ]
        critical_finding_pattern = re.compile(
            r"assertionerror|race condition|failed|failure|exception|traceback",
            re.IGNORECASE,
        )
        meaningful_lines = [
            line
            for _, line in sorted(
                enumerate(meaningful_lines),
                key=lambda item: (
                    not bool(critical_finding_pattern.search(item[1])),
                    item[0],
                ),
            )
        ]
        failed_attempt_lines = [
            line for line in meaningful_lines
            if re.search(r"ttl", line, re.IGNORECASE)
            and re.search(r"failed|unsuccessful|does not|did not|not resolve", line, re.IGNORECASE)
        ]
        findings = list(dict.fromkeys(labeled["findings"] + meaningful_lines))[:5]
        failed_attempts = labeled["failed_attempts"] or failed_attempt_lines[:3]
        files = labeled["files"]
        if not files:
            files = list(dict.fromkeys(
                re.findall(
                    r"(?<!\w)(?:[\w.-]+[\\/])*[\w.-]+\.(?:py|log|json|md)\b",
                    text,
                    re.IGNORECASE,
                )
            ))[:10]

        user_messages = [
            self._content_of(message)
            for message in messages
            if self._role_of(message) == "user"
        ]
        first_user_message = user_messages[0] if user_messages else ""
        latest_error = meaningful_lines[0] if meaningful_lines else ""
        checkpoint = StructuredCheckpoint(
            goal=labeled["goal"][0] if labeled["goal"] else (
                first_user_message[:500] or "Continue the current engineering task."
            ),
            current_state=labeled["current_state"][0] if labeled["current_state"] else (
                latest_error[:500] or "The conversation has no explicit status summary."
            ),
            constraints=labeled["constraints"] or [],
            findings=findings,
            failed_attempts=failed_attempts,
            files=files,
            next_action=labeled["next_action"][0] if labeled["next_action"] else (
                "Review the preserved findings and choose the next corrective action."
            ),
        )
        return checkpoint

    def reinject_rules_and_plan(
        self,
        base_system_prompt: str,
        checkpoint: StructuredCheckpoint,
        active_rules: Optional[List[str]] = None,
    ) -> List[AgentMessage]:
        """
        Bước 4: Tái nạp quy ước và kế hoạch vào mảng tin nhắn mới tinh gọn.
        
        Start a fresh context with the original system instructions, active
        rules, and a readable rendering of all seven checkpoint fields.
        """
        sections = [
            f"## {title}\n{value}"
            for title, value in (
                ("Goal", checkpoint.goal),
                ("Current state", checkpoint.current_state),
                ("Constraints", self._format_list(checkpoint.constraints)),
                ("Findings", self._format_list(checkpoint.findings)),
                ("Failed attempts (do not repeat)", self._format_list(checkpoint.failed_attempts)),
                ("Relevant files", self._format_list(checkpoint.files)),
                ("Next action", checkpoint.next_action),
            )
        ]
        system_parts = [base_system_prompt.strip()]
        if active_rules:
            system_parts.extend([
                "Active rules:\n" + "\n".join(f"- {rule}" for rule in active_rules)
            ])
        system_parts.append("Structured checkpoint:\n\n" + "\n\n".join(sections))
        return [
            AgentMessage(role="system", content="\n\n".join(system_parts)),
            AgentMessage(
                role="user",
                content=(
                    "Continue from the checkpoint. Do not repeat failed attempts. "
                    f"Perform this next action: {checkpoint.next_action}"
                ),
            ),
        ]

    @staticmethod
    def _format_list(values: List[str]) -> str:
        return "\n".join(f"- {value}" for value in values) if values else "- None recorded"

    def run_pipeline(
        self,
        messages: List[AgentMessage],
        base_system_prompt: str,
        active_rules: Optional[List[str]] = None,
    ) -> Tuple[List[AgentMessage], StructuredCheckpoint, Dict[str, Any]]:
        """
        Bước 5: Chạy toàn bộ 5 bước của Compaction Pipeline và tính toán số liệu tiết kiệm token.
        
        Prune tool messages before checkpoint extraction, then reinject only
        the compact checkpoint and current operating rules.
        """
        initial_report = self.observe_token_budget(messages)
        initial_tokens = initial_report.current_tokens
        pruned_messages: List[AgentMessage] = []
        for message in messages:
            content = self._content_of(message)
            if self._role_of(message) == "tool":
                content = self.prune_tool_output(content)
                pruned_messages.append(message.model_copy(update={"content": content}))
            else:
                pruned_messages.append(message)

        checkpoint = self.build_structured_checkpoint(pruned_messages)
        compacted_messages = self.reinject_rules_and_plan(
            base_system_prompt,
            checkpoint,
            active_rules,
        )
        final_tokens = self.observe_token_budget(compacted_messages).current_tokens
        tokens_saved = max(0, initial_tokens - final_tokens)
        retained_ratio = final_tokens / initial_tokens if initial_tokens else 0.0
        metrics: Dict[str, Any] = {
            "initial_tokens": initial_tokens,
            "final_tokens": final_tokens,
            "tokens_saved": tokens_saved,
            "compression_ratio": retained_ratio,
            "reduction_ratio": 1.0 - retained_ratio if initial_tokens else 0.0,
            "reduction_percent": (1.0 - retained_ratio) * 100 if initial_tokens else 0.0,
            "needs_compaction": initial_report.needs_compaction,
            "budget_limit": initial_report.limit_tokens,
            "initial_usage_ratio": initial_report.usage_ratio,
        }
        return compacted_messages, checkpoint, metrics

    def display_checkpoint_panel(self, checkpoint: StructuredCheckpoint, metrics: Dict[str, Any]) -> None:
        """
        Hiển thị Checkpoint 7 trường và bảng thống kê token trên terminal.
        
        Uses plain text so the panel remains usable without optional UI packages.
        """
        print("\n" + "=" * 72)
        print("STRUCTURED CHECKPOINT")
        print("=" * 72)
        for label, value in (
            ("Goal", checkpoint.goal),
            ("Current state", checkpoint.current_state),
            ("Constraints", self._format_list(checkpoint.constraints)),
            ("Findings", self._format_list(checkpoint.findings)),
            ("Failed attempts", self._format_list(checkpoint.failed_attempts)),
            ("Files", self._format_list(checkpoint.files)),
            ("Next action", checkpoint.next_action),
        ):
            print(f"\n{label}:\n{value}")
        print("\nToken metrics:")
        for key in (
            "initial_tokens",
            "final_tokens",
            "tokens_saved",
            "reduction_percent",
            "needs_compaction",
        ):
            if key in metrics:
                value = metrics[key]
                if key == "reduction_percent":
                    print(f"  {key}: {value:.2f}%")
                else:
                    print(f"  {key}: {value}")
        print("=" * 72)
