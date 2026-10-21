"""
Demo Challenge B1: Context Compaction Pipeline & Structured Checkpoint.
Phụ trách: Thành viên 4 - Huy Phát.

MỤC TIÊU KIỂM CHỨNG:
1. Tạo một session dài dẫn đến Context Bloat (>50.000 tokens):
   - Đọc source code auth_service.py (~2.000 dòng).
   - Chạy test suite (~7.000 dòng log test).
2. Kích hoạt Compaction Pipeline 5 bước (Observe -> Prune -> Build Checkpoint -> Reinject -> Resume).
3. Chứng minh sau khi nén:
   - Số token giảm sâu (>90%).
   - Agent vẫn nhớ lỗi 'refresh-token race condition'.
   - Agent KHÔNG lặp lại phương án 'tăng token TTL' đã thất bại.
   - Agent thực thi đúng bước 'next_action'.
"""

from __future__ import annotations

from src.config import config
from src.core_agent import CoreAgent
from src.compactor import ContextCompactor, StructuredCheckpoint
from src.mock_env import generate_mock_source_code, generate_mock_test_logs


def run_challenge_b1_demo() -> None:
    """
    Kịch bản kiểm chứng Challenge B1.
    
    TODO: [Thành viên 4]
    - Bước 1: Khởi tạo CoreAgent và nạp dữ liệu lớn (code 2.000 dòng, log 7.000 dòng).
    - Bước 2: Gọi compactor.run_pipeline() để nén ngữ cảnh.
    - Bước 3: In bảng so sánh token trước và sau khi nén.
    - Bước 4: Kiểm tra phản hồi của Agent sau nén dựa trên Checkpoint 7 trường.
    """
    print("=== BẮT ĐẦU CHẠY DEMO CHALLENGE B1 ===")
    compactor = ContextCompactor()
    agent = CoreAgent()

    # TODO: [Thành viên 4] Triển khai kịch bản kiểm chứng theo hướng dẫn trong docs/TEAM_WORKFLOW_AND_SPEC.md
    raise NotImplementedError("TODO: [Thành viên 4] Triển khai hàm run_challenge_b1_demo()")


if __name__ == "__main__":
    run_challenge_b1_demo()
