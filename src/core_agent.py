"""
Core Agent Loop and Token Tracking Module.
Phụ trách: Thành viên 1 - Phan Gia Đạt (Leader).

MỤC TIÊU CỦA PHAN GIA ĐẠT:
1. Hoàn thiện hàm estimate_tokens(text: str) -> int:
   - Ước tính số token của chuỗi (dùng tiktoken hoặc bộ đếm xấp xỉ).
2. Hoàn thiện lớp CoreAgent:
   - Quản lý danh sách tin nhắn: messages (List[AgentMessage]).
   - Hàm get_current_input_tokens() -> int: Tính tổng input tokens hiện tại trong messages.
   - Hàm add_message(role, content, name) -> AgentMessage: Thêm tin nhắn vào context.
   - Hàm execute_tool(tool_name, **kwargs) -> str: Dispatch thực thi tool được đăng ký.
   - Hàm step(user_input, simulate_llm_response) -> str: Vòng lặp 1 turn của Agent và cập nhật usage.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field
from src.config import config


class AgentMessage(BaseModel):
    """Cấu trúc một tin nhắn trong ngữ cảnh hội thoại của Agent."""
    role: str = Field(..., description="Vai trò: system | user | assistant | tool")
    content: str = Field(..., description="Nội dung văn bản của tin nhắn")
    name: Optional[str] = Field(default=None, description="Tên tool nếu role == 'tool'")
    tool_call_id: Optional[str] = Field(default=None, description="ID liên kết tool call nếu có")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata bổ sung")


class TokenUsage(BaseModel):
    """Thống kê token tiêu thụ của lượt gọi LLM."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


def estimate_tokens(text: str) -> int:
    """
    Ước tính số lượng token của chuỗi văn bản.
    
    TODO: [Thành viên 1]
    - Sử dụng thư viện tiktoken nếu có (encoding cl100k_base).
    - Hoặc giải thuật ước lượng xấp xỉ (~4 ký tự/token).
    """
    raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm estimate_tokens()")


class CoreAgent:
    """
    Vòng lặp Agent cơ sở (Agent Loop).
    Quản lý ngữ cảnh tin nhắn, gọi công cụ, và đo lường input_tokens.
    """

    def __init__(
        self,
        system_prompt: str = "You are a helpful software engineering assistant.",
        tools: Optional[Dict[str, Callable[..., str]]] = None,
        token_budget_limit: int = config.token_budget_limit,
    ) -> None:
        self.system_prompt: str = system_prompt
        self.messages: List[AgentMessage] = [
            AgentMessage(role="system", content=system_prompt)
        ]
        self.tools: Dict[str, Callable[..., str]] = tools or {}
        self.token_budget_limit: int = token_budget_limit
        self.total_usage = TokenUsage()
        self.history_usages: List[TokenUsage] = []

    def get_current_input_tokens(self) -> int:
        """
        Tính toán tổng số input_tokens của toàn bộ tin nhắn hiện có trong self.messages.
        
        TODO: [Thành viên 1]
        - Duyệt qua từng msg trong self.messages.
        - Gọi estimate_tokens(msg.content) và cộng dồn lại.
        """
        raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm get_current_input_tokens()")

    def add_message(self, role: str, content: str, name: Optional[str] = None) -> AgentMessage:
        """
        Thêm một tin nhắn mới vào danh sách self.messages.
        
        TODO: [Thành viên 1]
        - Khởi tạo AgentMessage.
        - Append vào self.messages và trả về message đó.
        """
        raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm add_message()")

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """
        Thực thi tool được chỉ định trong self.tools.
        
        TODO: [Thành viên 1]
        - Kiểm tra tool_name có trong self.tools không.
        - Gọi hàm tương ứng và trả về kết quả dạng str.
        - Xử lý exception nếu có lỗi phát sinh.
        """
        raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm execute_tool()")

    def step(self, user_input: str, simulate_llm_response: Optional[str] = None) -> str:
        """
        Thực hiện một lượt hội thoại (Turn):
        
        TODO: [Thành viên 1]
        1. Thêm tin nhắn user vào self.messages.
        2. Đo input_tokens trước khi gọi model bằng self.get_current_input_tokens().
        3. Lấy phản hồi từ LLM (hoặc dùng simulate_llm_response nếu đang chạy giả lập).
        4. Thêm tin nhắn assistant vào self.messages.
        5. Cập nhật TokenUsage vào self.history_usages và self.total_usage.
        6. Trả về nội dung phản hồi của assistant.
        """
        raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm step()")
