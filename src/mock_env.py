"""
Mock Environment and Data Generation Module.
Phụ trách: Thành viên 1 - Phan Gia Đạt (Leader).

TÁC DỤNG VÀ Ý NGHĨA KIẾN TRÚC:
Module này đóng vai trò là "Thao trường giả lập" (Mock Harness Environment) nhằm:
1. Tái hiện hiện tượng 'Context Bloat' và 'Lost-in-the-Middle' bằng cách sinh ra các khối dữ liệu
   rất lớn (2.000 dòng mã nguồn và 7.000 dòng log test), đẩy Context Window của LLM vượt ngưỡng an toàn.
2. Cung cấp 20 file log máy chủ với các mã lỗi HTTP phân tán chuẩn để thử nghiệm Code Mode (Challenge B2).
3. Đảm bảo tính tất định (Deterministic): Cùng seed ngẫu nhiên sẽ luôn cho ra cùng kết quả kiểm thử.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import List
from src.config import LOGS_DIR


def generate_mock_server_logs(target_dir: Path = LOGS_DIR, num_files: int = 20, lines_per_file: int = 150) -> List[Path]:
    """
    Sinh 20 file log giả lập (server_01.log -> server_20.log) vào thư mục target_dir.
    
    Định dạng mỗi dòng log:
    [TIMESTAMP] [LEVEL] [ENDPOINT] status=[CODE] latency=[LATENCY]ms - [MESSAGE]
    
    Phân bổ lỗi có chủ đích:
    - Các lỗi 500, 502, 504 tập trung chủ yếu vào các endpoint thanh toán và làm mới token
      để Thành viên 5 (Thái Hưng) có thể dùng Code Mode thống kê Top 5 endpoint lỗi nhiều nhất.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    generated_files: List[Path] = []

    endpoints = [
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v2/payments/charge",
        "/api/v2/orders/create",
        "/api/v1/users/profile",
        "/api/v2/inventory/check",
        "/api/v1/notifications/push",
        "/api/v2/analytics/track",
        "/api/v1/reports/export",
        "/api/v2/webhooks/stripe",
    ]

    status_weights = {
        200: 0.65,
        201: 0.10,
        400: 0.05,
        401: 0.05,
        404: 0.03,
        429: 0.02,
        500: 0.07,
        502: 0.02,
        504: 0.01,
    }
    status_codes = list(status_weights.keys())
    weights = list(status_weights.values())

    # Cố định seed ngẫu nhiên để 5 thành viên luôn sinh ra bộ dữ liệu giống nhau
    random.seed(42)

    for i in range(1, num_files + 1):
        file_name = f"server_{i:02d}.log"
        file_path = target_dir / file_name
        lines = []

        for line_idx in range(1, lines_per_file + 1):
            timestamp = f"2026-10-21T10:{i:02d}:{line_idx % 60:02d}.{random.randint(100, 999)}Z"
            endpoint = random.choice(endpoints)
            code = random.choices(status_codes, weights=weights)[0]
            latency = random.randint(15, 1200)

            if code >= 500:
                level = "ERROR"
                msg = f"Internal server exception during processing endpoint={endpoint} trace_id=tx-{i}-{line_idx}"
            elif code in (401, 429):
                level = "WARN"
                msg = f"Client rate limit or auth challenge at endpoint={endpoint}"
            else:
                level = "INFO"
                msg = f"Request handled successfully endpoint={endpoint}"

            lines.append(f"[{timestamp}] [{level}] {endpoint} status={code} latency={latency}ms - {msg}")

        file_path.write_text("\n".join(lines), encoding="utf-8")
        generated_files.append(file_path)

    return generated_files


def generate_mock_test_logs(total_lines: int = 7000) -> str:
    """
    Sinh 7.000 dòng log test suite phục vụ bài toán Context Compaction (Challenge B1).
    
    Cấu trúc:
    - 6.900+ dòng PASSED rườm rà (cần loại bỏ bằng chiến lược DROP trong quá trình nén).
    - Khối FAILURES trọng tâm: chứa chi tiết lỗi 'refresh-token race condition',
      ghi nhận phương án tăng TTL thất bại và chỉ dẫn bước đi kế tiếp (cần KEEP trong Checkpoint).
    """
    lines: List[str] = [
        "============================= test session starts ==============================",
        "platform win32 -- Python 3.14.7, pytest-8.3.0, pluggy-1.5.0",
        "rootdir: C:\\workspace\\payment_service",
        "collected 650 items",
        "",
    ]

    # Sinh các dòng test pass đều đặn
    for suite in range(1, 130):
        for case in range(1, 50):
            if len(lines) >= total_lines - 100:
                break
            lines.append(f"tests/unit/suite_{suite:03d}.py::test_case_{case:03d} PASSED [ {(len(lines)*100)//total_lines}%]")

    # Chèn khối lỗi cốt lõi (Root cause & Failed Attempts)
    critical_failure_block = [
        "",
        "=================================== FAILURES ===================================",
        "_____________________ test_concurrent_token_refresh ___________________________",
        "tests/integration/test_auth_flow.py:342: in test_concurrent_token_refresh",
        "    response = await client.post('/api/v2/auth/refresh', headers=dup_headers)",
        ">   assert response.status_code == 200, f'Expected 200 OK, got {response.status_code}: {response.text}'",
        "E   AssertionError: Expected 200 OK, got 409 Conflict: {\"error\": \"refresh-token race condition detected\"}",
        "E   FINDING: Two concurrent requests with the same refresh token caused race condition in token rotation.",
        "E   FAILED_ATTEMPT_1: Increasing token TTL from 15m to 60m failed. Race condition still occurs under concurrent bursts.",
        "E   CONSTRAINT: Token rotation must remain atomic. No long-lived refresh tokens allowed.",
        "E   NEXT_ACTION: Implement Redis distributed lock (Redlock) or DB row-level locking on user token record.",
        "=========================== short test summary info ===========================",
        "FAILED tests/integration/test_auth_flow.py::test_concurrent_token_refresh - AssertionError: refresh-token race condition",
        f"= 1 failed, 649 passed in 14.82s (simulated {total_lines} lines output) =",
    ]
    lines.extend(critical_failure_block)

    # Đảm bảo đủ total_lines
    while len(lines) < total_lines:
        lines.append(f"[DEBUG LOG VERBOSE #{len(lines)}] ThreadPoolExecutor pool-worker active")

    return "\n".join(lines[:total_lines])


def generate_mock_source_code(total_lines: int = 2000) -> str:
    """
    Sinh 2.000 dòng mã nguồn giả lập của auth_service.py phục vụ Challenge B1.
    Chứa hàm refresh_access_token bị lỗi race condition khi xoay token đồng thời.
    """
    header = [
        '"""Authentication & Token Management Service."""',
        "from __future__ import annotations",
        "import time",
        "import hashlib",
        "from typing import Optional, Dict, Any",
        "",
        "class AuthService:",
        "    def __init__(self, db_client: Any, cache_client: Any) -> None:",
        "        self.db = db_client",
        "        self.cache = cache_client",
        "",
    ]
    lines = list(header)

    for i in range(1, 180):
        lines.extend([
            f"    def helper_method_{i:03d}(self, param_a: str, param_b: int) -> Dict[str, Any]:",
            f'        """Internal validation routine {i}."""',
            f"        token_hash = hashlib.sha256(f'{{param_a}}_{{param_b}}'.encode()).hexdigest()",
            f"        timestamp = time.time()",
            f"        return {{'index': {i}, 'hash': token_hash, 'ts': timestamp}}",
            "",
        ])
        if len(lines) >= total_lines - 40:
            break

    # Đoạn mã nguồn trọng tâm chứa lỗi Race Condition
    buggy_method = [
        "    async def refresh_access_token(self, refresh_token: str) -> dict[str, str]:",
        '        """Vulnerable method: refresh-token race condition under concurrency."""',
        "        token_data = await self.db.find_one({'token': refresh_token})",
        "        if not token_data:",
        "            raise ValueError('Invalid refresh token')",
        "        # BUG: Check-then-act without distributed lock allows double token issuance",
        "        new_token = self._issue_new_token(token_data['user_id'])",
        "        await self.db.update_token(refresh_token, revoked=True)",
        "        return {'access_token': new_token}",
    ]
    lines.extend(buggy_method)

    while len(lines) < total_lines:
        lines.append(f"# Padding source line {len(lines)}")

    return "\n".join(lines[:total_lines])


def mock_read_file(file_path: str = "src/auth_service.py") -> str:
    """Tool giả lập đọc file dung lượng lớn (~2.000 dòng mã nguồn)."""
    return generate_mock_source_code(2000)


def mock_run_tests(command: str = "pytest tests/") -> str:
    """Tool giả lập chạy test suite xuất log khổng lồ (~7.000 dòng)."""
    return generate_mock_test_logs(7000)
