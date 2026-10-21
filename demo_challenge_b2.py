"""
Demo Challenge B2: Code Mode vs Native Tool Calling on 20 Server Log Files.
Phụ trách: Thành viên 5 - Thái Hưng.

MỤC TIÊU KIỂM CHỨNG:
1. Đảm bảo dữ liệu 20 file log máy chủ đã có trong data/logs/.
2. So sánh 2 cách tiếp cận:
   - Cách 1 (Native Tool Calling): Đọc 20 file log và đẩy toàn bộ nội dung thô vào tin nhắn của LLM.
   - Cách 2 (Code Mode): Cho LLM sinh mã Python, chạy script trong sandbox runtime để scan 20 files,
     và chỉ trả về bảng kết quả Top 5 endpoint lỗi HTTP 5xx nhiều nhất.
3. In bảng so sánh số lượng input_tokens và chi phí giữa 2 cách làm.
"""

from __future__ import annotations

from src.config import LOGS_DIR
from src.code_mode import CodeExecutionRuntime


def run_challenge_b2_demo() -> None:
    """
    Kịch bản kiểm chứng Challenge B2.
    
    TODO: [Thành viên 5]
    - Bước 1: Khởi tạo runtime = CodeExecutionRuntime().
    - Bước 2: Chuẩn bị đoạn code Python mẫu để duyệt 20 file log qua biến 'tools'.
    - Bước 3: Chạy runtime.run_code(code) và in kết quả stdout.
    - Bước 4: So sánh input_tokens giữa việc nạp raw log (~100k tokens) vs Code Mode (~100 tokens).
    """
    print("=== BẮT ĐẦU CHẠY DEMO CHALLENGE B2 (CODE MODE) ===")
    runtime = CodeExecutionRuntime()

    # TODO: [Thành viên 5] Triển khai kịch bản kiểm chứng theo hướng dẫn trong docs/TEAM_WORKFLOW_AND_SPEC.md
    raise NotImplementedError("TODO: [Thành viên 5] Triển khai hàm run_challenge_b2_demo()")


if __name__ == "__main__":
    run_challenge_b2_demo()
