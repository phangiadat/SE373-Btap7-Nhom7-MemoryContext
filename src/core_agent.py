"""
Core Agent Loop and Token Tracking Module.
Phụ trách: Thành viên 1 - Phan Gia Đạt (Leader).

TÁC DỤNG VÀ Ý NGHĨA KIẾN TRÚC:
Module này là "Trái tim" của hệ thống Agentic AI (Core Execution Engine):
1. Quản lý trạng thái đàm thoại (Conversation State): Duy trì danh sách tin nhắn tuần tự (messages)
   tuân thủ kiến trúc Prompt Assembly theo chuẩn của các mô hình hiện đại.
2. Giám sát ngân sách Token (Token Budget Observability): Đo lường chính xác 'usage.input_tokens'
   sau mỗi lượt (Turn) để phát hiện sớm nguy cơ tràn ngữ cảnh (Context Rot & Bloat) trước khi gọi LLM.
3. Cơ chế kích hoạt công cụ (Tool Dispatcher): Kết nối linh hoạt giữa Agent Planner và môi trường
   thực thi bên ngoài (read_file, run_tests).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from src.config import config
from src.mock_env import mock_read_file, mock_run_tests


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
    Sử dụng tiktoken (cl100k_base) nếu đã cài đặt, hoặc giải thuật xấp xỉ (~4 ký tự/token).
    """
    if not text:
        return 0
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Heuristic chuẩn công nghiệp: 1 token ~= 4 ký tự tiếng Anh/code
        return max(1, len(text) // 4)


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
        # Đăng ký mặc định các mock tools để phục vụ bài B1 & B2
        self.tools: Dict[str, Callable[..., str]] = tools if tools is not None else {
            "read_file": mock_read_file,
            "run_tests": mock_run_tests,
        }
        self.token_budget_limit: int = token_budget_limit
        self.total_usage = TokenUsage()
        self.history_usages: List[TokenUsage] = []

    def get_current_input_tokens(self) -> int:
        """
        Tính toán tổng số input_tokens của toàn bộ tin nhắn hiện có trong self.messages.
        Phản ánh đúng khối lượng ngữ cảnh mà LLM sẽ phải nạp vào attention layer nếu gọi API.
        """
        return sum(estimate_tokens(msg.content) for msg in self.messages)

    def add_message(self, role: str, content: str, name: Optional[str] = None) -> AgentMessage:
        """Thêm một tin nhắn mới vào danh sách self.messages và trả về tin nhắn đó."""
        msg = AgentMessage(
            role=role,
            content=content,
            name=name,
            metadata={"estimated_tokens": estimate_tokens(content)},
        )
        self.messages.append(msg)
        return msg

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """
        Thực thi tool được chỉ định trong self.tools và trả về output kết quả.
        Bắt lỗi an toàn để tránh làm đổ vỡ vòng lặp Agent nếu tool ném Exception.
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' is not registered in agent toolset."
        try:
            tool_fn = self.tools[tool_name]
            result = tool_fn(**kwargs)
            return str(result)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {type(e).__name__} - {str(e)}"

    def step(self, user_input: str, simulate_llm_response: Optional[str] = None) -> str:
        """
        Thực hiện một lượt hội thoại (Turn):
        1. Thêm user message vào context.
        2. Đo lường chính xác input_tokens hiện thời trước khi gửi tới LLM.
        3. Sinh phản hồi của Assistant (hoặc dùng simulate_llm_response khi chạy test giả lập).
        4. Thêm assistant message vào context.
        5. Cập nhật và lưu vết thống kê TokenUsage.
        """
        # Bước 1: Ghi nhận tin nhắn người dùng
        self.add_message("user", user_input)

        # Bước 2: Đo lường input_tokens
        curr_input_tokens = self.get_current_input_tokens()

        # Bước 3: Xác định phản hồi của Assistant
        if simulate_llm_response is not None:
            assistant_reply = simulate_llm_response
        else:
            assistant_reply = (
                f"[CoreAgent] Acknowledged input: '{user_input[:60]}...'. "
                f"Current context contains {curr_input_tokens} input tokens across {len(self.messages)} messages."
            )

        # Bước 4: Ghi nhận phản hồi vào ngữ cảnh
        self.add_message("assistant", assistant_reply)
        output_tokens = estimate_tokens(assistant_reply)

        # Bước 5: Cập nhật chỉ số token tiêu thụ
        turn_usage = TokenUsage(
            input_tokens=curr_input_tokens,
            output_tokens=output_tokens,
            total_tokens=curr_input_tokens + output_tokens,
        )
        self.history_usages.append(turn_usage)
        self.total_usage.input_tokens += turn_usage.input_tokens
        self.total_usage.output_tokens += turn_usage.output_tokens
        self.total_usage.total_tokens += turn_usage.total_tokens

        return assistant_reply
