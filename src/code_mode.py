"""
Code Mode Runtime Module.
Phụ trách: Thành viên 5 - Thái Hưng.

MỤC TIÊU CỦA THÁI HƯNG:
1. Xây dựng SDK Proxy 'tools' (CodeModeToolsProxy):
   - tools.list_files(extension: str) -> List[str]: Liệt kê các file log trong data/logs/.
   - tools.read_file(filename: str) -> str: Đọc an toàn nội dung 1 file log.
2. Xây dựng môi trường thực thi code an toàn (CodeExecutionRuntime):
   - Hàm run_code(code: str) -> CodeExecutionResult:
     * Cung cấp biến 'tools' vào môi trường thực thi.
     * Chuyển hướng stdout để bắt toàn bộ kết quả print().
     * Thiết lập timeout và bắt các exception.
3. Bản chất Code Mode:
   - LLM chỉ sinh đoạn code Python để xử lý 20 file log trong runtime cục bộ.
   - LLM chỉ nhận lại bảng kết quả tóm tắt (Top 5 lỗi) thay vì nuốt toàn bộ raw log vào Context Window.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from src.config import config, LOGS_DIR


class CodeModeToolsProxy:
    """
    Tập hợp các hàm tiện ích được nạp vào namespace của môi trường runtime.
    """

    def __init__(self, logs_dir: Path = LOGS_DIR) -> None:
        self.logs_dir: Path = logs_dir

    def list_files(self, extension: str = ".log") -> List[str]:
        """
        Liệt kê danh sách tên file trong thư mục logs.
        
        TODO: [Thành viên 5]
        - Quét self.logs_dir và trả về danh sách tên file có đuôi extension.
        """
        raise NotImplementedError("TODO: [Thành viên 5] Triển khai hàm list_files()")

    def read_file(self, filename: str) -> str:
        """
        Đọc nội dung một file log trong thư mục logs.
        
        TODO: [Thành viên 5]
        - Đọc file an toàn (kiểm tra file tồn tại) và trả về chuỗi nội dung.
        """
        raise NotImplementedError("TODO: [Thành viên 5] Triển khai hàm read_file()")


class CodeExecutionResult(BaseModel):
    """Kết quả sau khi thực thi code trong sandbox runtime."""
    success: bool = Field(..., description="Trạng thái thực thi có thành công hay không")
    output: str = Field(..., description="Toàn bộ chuỗi stdout in ra hoặc traceback lỗi")
    execution_time_ms: float = Field(default=0.0, description="Thời gian thực thi tính bằng ms")
    error: Optional[str] = Field(default=None, description="Chi tiết ngoại lệ nếu có lỗi")


class CodeExecutionRuntime:
    """
    Môi trường thực thi code Python có kiểm soát (Sandbox Runtime).
    """

    def __init__(self, timeout_seconds: int = config.code_exec_timeout_seconds) -> None:
        self.timeout_seconds: int = timeout_seconds
        self.tools_proxy = CodeModeToolsProxy()

    def run_code(self, code: str) -> CodeExecutionResult:
        """
        Thực thi đoạn mã python được cung cấp bởi Agent.
        
        TODO: [Thành viên 5]
        - Khởi tạo namespace chứa {'tools': self.tools_proxy}.
        - Bắt stdout bằng io.StringIO() và contextlib.redirect_stdout.
        - Xử lý timeout và bắt lỗi ngoại lệ nếu mã code bị lỗi.
        - Trả về đối tượng CodeExecutionResult.
        """
        raise NotImplementedError("TODO: [Thành viên 5] Triển khai hàm run_code()")
