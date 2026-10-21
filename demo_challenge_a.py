"""
Demo Challenge A: Persistent Memory & Convention Evolution Across Sessions.
Phụ trách: Thành viên 3 - Huy Bình.

MỤC TIÊU KIỂM CHỨNG:
1. Chứng minh 1: Session 2 nhớ đúng quy ước (PostgreSQL + TypeScript + JWT) đã chốt ở Session 1.
2. Chứng minh 2: Session 2 đổi quy ước sang Session Cookie -> Session 3 tự động dùng Session Cookie
   và ghi nhận JWT đã bị superseded.
3. In rõ phần memory được inject vào context của từng session trên terminal.

HƯỚNG DẪN DÀNH CHO HUY BÌNH:
- Kết nối MemoryStore (do Gia Bảo viết) và MemoryInjector (do Huy Bình viết).
- Triển khai 3 hàm session tương ứng bên dưới.
"""

from __future__ import annotations

from src.core_agent import CoreAgent
from src.memory_injector import MemoryInjector
from src.memory_store import MemoryStore


def run_session_1(store: MemoryStore) -> None:
    """
    Session 1: Thảo luận và lưu 3 quy ước ban đầu vào store:
    - database: PostgreSQL with Prisma ORM
    - language: TypeScript strict mode
    - auth: JWT tokens with 15m expiration
    
    TODO: [Thành viên 3] Viết logic Session 1 tại đây.
    """
    raise NotImplementedError("TODO: [Thành viên 3] Triển khai hàm run_session_1()")


def run_session_2(store: MemoryStore, injector: MemoryInjector) -> None:
    """
    Session 2:
    - Inject memory vào System Prompt -> Kiểm tra Agent nhớ PostgreSQL + TypeScript + JWT (Chứng minh 1).
    - Đổi quy ước: Nhóm quyết định chuyển từ JWT sang Session Cookie.
    - Cập nhật store: JWT đổi trạng thái thành superseded, Cookie thành active.
    
    TODO: [Thành viên 3] Viết logic Session 2 tại đây.
    """
    raise NotImplementedError("TODO: [Thành viên 3] Triển khai hàm run_session_2()")


def run_session_3(store: MemoryStore, injector: MemoryInjector) -> None:
    """
    Session 3:
    - Khởi động session mới hoàn toàn, nạp active memory.
    - Kiểm tra Agent tự động áp dụng Session Cookie và không dùng JWT (Chứng minh 2).
    
    TODO: [Thành viên 3] Viết logic Session 3 tại đây.
    """
    raise NotImplementedError("TODO: [Thành viên 3] Triển khai hàm run_session_3()")


def main() -> None:
    print("=== BẮT ĐẦU CHẠY DEMO CHALLENGE A ===")
    store = MemoryStore()
    injector = MemoryInjector(store=store)

    run_session_1(store)
    run_session_2(store, injector)
    run_session_3(store, injector)
    print("=== KẾT THÚC DEMO CHALLENGE A ===")


if __name__ == "__main__":
    main()
