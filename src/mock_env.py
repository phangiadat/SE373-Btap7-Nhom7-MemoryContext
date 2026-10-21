"""
Mock Environment and Data Generation Module.
Phụ trách: Thành viên 1 - Phan Gia Đạt (Leader).

MỤC TIÊU CỦA PHAN GIA ĐẠT:
1. Viết hàm generate_mock_server_logs():
   - Tạo 20 file log trong data/logs/ (server_01.log -> server_20.log).
   - Chứa các định dạng: [TIMESTAMP] [LEVEL] [ENDPOINT] status=[CODE] latency=[MS] - [MSG].
   - Phân bổ các lỗi 500, 502, 504 và cảnh báo 401, 429 để phục vụ bài thống kê B2.
2. Viết hàm generate_mock_test_logs():
   - Sinh chuỗi kết quả log chạy test gồm ~7.000 dòng.
   - Phần lớn là các dòng test PASSED rườm rà.
   - Có đoạn FAILURES: ghi nhận lỗi 'refresh-token race condition' và 'tăng TTL token thất bại'.
3. Viết hàm generate_mock_source_code():
   - Sinh chuỗi mã nguồn ~2.000 dòng mô phỏng auth_service.py.
4. Cung cấp mock tools: mock_read_file và mock_run_tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import List
from src.config import LOGS_DIR


def generate_mock_server_logs(target_dir: Path = LOGS_DIR, num_files: int = 20) -> List[Path]:
    """
    Sinh 20 file log giả lập (server_01.log -> server_20.log) vào thư mục target_dir.
    
    TODO: [Thành viên 1]
    - Duyệt qua từ 1 đến num_files.
    - Sinh nội dung log ngẫu nhiên có chủ đích (khoảng 100-200 dòng mỗi file).
    - Ghi ra các file server_01.log -> server_20.log.
    - Trả về danh sách Path các file đã sinh.
    """
    raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm generate_mock_server_logs()")


def generate_mock_test_logs(total_lines: int = 7000) -> str:
    """
    Sinh 7.000 dòng log test suite phục vụ bài toán Context Compaction (Challenge B1).
    
    TODO: [Thành viên 1]
    - Sinh khoảng 6.950 dòng PASSED rườm rà.
    - Chèn đoạn lỗi FAILURES với thông điệp AssertionError: refresh-token race condition.
    - Ghi chú giải pháp thất bại: tăng TTL token không giải quyết được vấn đề.
    """
    raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm generate_mock_test_logs()")


def generate_mock_source_code(total_lines: int = 2000) -> str:
    """
    Sinh 2.000 dòng mã nguồn giả lập của service auth_service.py phục vụ Challenge B1.
    
    TODO: [Thành viên 1]
    - Sinh mã nguồn Python giả lập có header, class AuthService, các helper method.
    - Chứa đoạn hàm refresh_access_token bị lỗi race condition.
    """
    raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm generate_mock_source_code()")


def mock_read_file(file_path: str) -> str:
    """
    Tool giả lập đọc file dung lượng lớn (~2.000 dòng).
    
    TODO: [Thành viên 1] Gọi hàm generate_mock_source_code() để trả về nội dung.
    """
    raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm mock_read_file()")


def mock_run_tests(command: str = "pytest tests/") -> str:
    """
    Tool giả lập chạy test suite xuất log khổng lồ (~7.000 dòng).
    
    TODO: [Thành viên 1] Gọi hàm generate_mock_test_logs() để trả về nội dung.
    """
    raise NotImplementedError("TODO: [Thành viên 1] Triển khai hàm mock_run_tests()")
