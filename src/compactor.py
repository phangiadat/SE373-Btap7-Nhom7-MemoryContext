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

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from src.core_agent import AgentMessage
from src.config import config


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
        self.token_budget_limit: int = token_budget_limit
        self.warning_threshold: float = warning_threshold

    def observe_token_budget(self, messages: List[AgentMessage]) -> TokenBudgetReport:
        """
        Bước 1: Đo lường ngân sách token hiện tại.
        
        TODO: [Thành viên 4]
        - Tính tổng token trong messages.
        - Tính tỷ lệ usage_ratio = total_tokens / limit.
        - needs_compaction = (usage_ratio >= self.warning_threshold).
        - Trả về TokenBudgetReport.
        """
        raise NotImplementedError("TODO: [Thành viên 4] Triển khai hàm observe_token_budget()")

    def prune_tool_output(self, raw_output: str, max_lines_kept: int = 40) -> str:
        """
        Bước 2: Cắt gọt output công cụ lớn (Áp dụng TRUNCATE và DROP).
        
        TODO: [Thành viên 4]
        - Giữ lại header và đoạn FAILURES chính (TRUNCATE).
        - Loại bỏ toàn bộ các dòng PASSED lặp lại (DROP).
        - Trả về chuỗi output đã được rút gọn.
        """
        raise NotImplementedError("TODO: [Thành viên 4] Triển khai hàm prune_tool_output()")

    def build_structured_checkpoint(
        self,
        messages: List[AgentMessage],
        custom_checkpoint: Optional[StructuredCheckpoint] = None,
    ) -> StructuredCheckpoint:
        """
        Bước 3: Đóng gói ngữ cảnh thành StructuredCheckpoint 7 trường.
        
        TODO: [Thành viên 4]
        - Trích xuất thông tin từ messages hoặc tạo checkpoint chuẩn hóa
          đảm bảo lưu đúng thông tin race condition và failed attempt tăng TTL.
        """
        raise NotImplementedError("TODO: [Thành viên 4] Triển khai hàm build_structured_checkpoint()")

    def reinject_rules_and_plan(
        self,
        base_system_prompt: str,
        checkpoint: StructuredCheckpoint,
        active_rules: Optional[List[str]] = None,
    ) -> List[AgentMessage]:
        """
        Bước 4: Tái nạp quy ước và kế hoạch vào mảng tin nhắn mới tinh gọn.
        
        TODO: [Thành viên 4]
        - Tạo tin nhắn system mới chứa base_system_prompt + active_rules + checkpoint định dạng Markdown.
        - Tạo tin nhắn user chỉ dẫn thực hiện tiếp bước next_action.
        - Trả về danh sách messages mới.
        """
        raise NotImplementedError("TODO: [Thành viên 4] Triển khai hàm reinject_rules_and_plan()")

    def run_pipeline(
        self,
        messages: List[AgentMessage],
        base_system_prompt: str,
        active_rules: Optional[List[str]] = None,
    ) -> Tuple[List[AgentMessage], StructuredCheckpoint, Dict[str, Any]]:
        """
        Bước 5: Chạy toàn bộ 5 bước của Compaction Pipeline và tính toán số liệu tiết kiệm token.
        
        TODO: [Thành viên 4]
        - Kết hợp Bước 1 -> 4.
        - Tính initial_tokens và final_tokens.
        - Tính tỷ lệ nén (compression_ratio).
        - Trả về (compacted_messages, checkpoint, metrics_dict).
        """
        raise NotImplementedError("TODO: [Thành viên 4] Triển khai hàm run_pipeline()")

    def display_checkpoint_panel(self, checkpoint: StructuredCheckpoint, metrics: Dict[str, Any]) -> None:
        """
        Hiển thị Checkpoint 7 trường và bảng thống kê token trên terminal.
        
        TODO: [Thành viên 4] Hiển thị đẹp mắt bằng rich hoặc print formatted.
        """
        raise NotImplementedError("TODO: [Thành viên 4] Triển khai hàm display_checkpoint_panel()")
