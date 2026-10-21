"""
Memory Injection and Context Assembly Module.
Phụ trách: Thành viên 3 - Huy Bình.

MỤC TIÊU CỦA HUY BÌNH:
1. Xây dựng lớp MemoryInjector:
   - Nhận vào đối tượng MemoryStore.
2. Hàm assemble_system_prompt(base_system_prompt, topic_filter):
   - Lấy toàn bộ active memories từ store.
   - Định dạng thành khối Markdown: [PROJECT ACTIVE MEMORIES & ARCHITECTURAL CONVENTIONS].
   - Nối vào cuối base_system_prompt để LLM Agent nhận diện quy ước ngay từ đầu session.
   - Trả về tuple (augmented_system_prompt, active_memories).
3. Hàm display_injected_memory_panel(active_memories, session_name):
   - In ra terminal bảng trực quan danh sách memory vừa được inject.
"""

from __future__ import annotations

from typing import List, Optional, Tuple
from src.memory_store import MemoryItem, MemoryStore


class MemoryInjector:
    """
    Chịu trách nhiệm trích xuất các quy ước đang hiệu lực và gắn vào System Prompt
    trước khi khởi động vòng lặp Agent.
    """

    def __init__(self, store: Optional[MemoryStore] = None) -> None:
        self.store: MemoryStore = store or MemoryStore()

    def assemble_system_prompt(
        self,
        base_system_prompt: str = "You are a Senior Fullstack Architect Assistant.",
        topic_filter: Optional[str] = None,
    ) -> Tuple[str, List[MemoryItem]]:
        """
        Lọc các active memory và ghép vào base system prompt.
        
        TODO: [Thành viên 3]
        - Lấy active memories từ self.store.get_active_memories(topic=topic_filter).
        - Nếu không có memory nào: trả về base_system_prompt và [].
        - Nếu có: format danh sách quy ước kèm topic, rule, source.
        - Ghép nối vào base_system_prompt và trả về (augmented_prompt, active_memories).
        """
        raise NotImplementedError("TODO: [Thành viên 3] Triển khai hàm assemble_system_prompt()")

    def display_injected_memory_panel(
        self,
        active_memories: List[MemoryItem],
        session_name: str = "New Session",
    ) -> None:
        """
        In bảng thông tin các Memory được inject vào Terminal một cách trực quan.
        
        TODO: [Thành viên 3]
        - Dùng thư viện rich (hoặc print thông thường) để hiển thị bảng gồm:
          Memory ID, Topic, Rule, Source, Status.
        """
        raise NotImplementedError("TODO: [Thành viên 3] Triển khai hàm display_injected_memory_panel()")
