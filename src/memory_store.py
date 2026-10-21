"""
Persistent Memory Storage and Conflict Curation Module.
Phụ trách: Thành viên 2 - Gia Bảo.

MỤC TIÊU CỦA GIA BẢO:
1. Thiết kế Pydantic Schema cho Memory Item:
   - id: str (mã định danh quy ước)
   - topic: str (chủ đề: 'database', 'auth', 'language'...)
   - rule: str (nội dung quy ước)
   - status: Literal['active', 'superseded', 'wontfix']
   - source: str (nguồn gốc quy ước)
   - updated_at: str (thời gian cập nhật ISO-8601)
   - superseded_by: Optional[str] (id quy ước mới thay thế nếu bị superseded)
2. Quản lý đọc/ghi file data/project_memory.json:
   - load_all() -> List[MemoryItem]
   - save_all(items: List[MemoryItem]) -> None
   - get_active_memories(topic: Optional[str]) -> List[MemoryItem]
   - get_superseded_memories(topic: Optional[str]) -> List[MemoryItem]
3. Thuật toán giải quyết xung đột (Conflict Resolution):
   - update_rule_with_conflict_resolution(topic, new_rule, source) -> (new_item, superseded_items)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Literal, Optional, Tuple
from pydantic import BaseModel, Field

from src.config import MEMORY_FILE_PATH

MemoryStatus = Literal["active", "superseded", "wontfix"]


class MemoryItem(BaseModel):
    """Mô hình dữ liệu cho một quy ước kiến trúc trong persistent memory."""
    id: str = Field(..., description="Định danh duy nhất của memory (ví dụ: mem_001)")
    topic: str = Field(..., description="Chủ đề của quy ước (ví dụ: 'database', 'auth')")
    rule: str = Field(..., description="Nội dung quy ước chi tiết")
    status: MemoryStatus = Field(default="active", description="Trạng thái: active | superseded | wontfix")
    source: str = Field(default="human_instruction", description="Nguồn gốc quy ước")
    updated_at: str = Field(..., description="Thời gian cập nhật ISO-8601")
    superseded_by: Optional[str] = Field(default=None, description="ID của memory mới thay thế memory này")


class MemoryStore:
    """
    Quản lý lưu trữ và xử lý xung đột quy ước trên file JSON.
    """

    def __init__(self, file_path: Path = MEMORY_FILE_PATH) -> None:
        self.file_path: Path = file_path

    def load_all(self) -> List[MemoryItem]:
        """
        Đọc toàn bộ danh sách MemoryItem từ file JSON.
        
        TODO: [Thành viên 2]
        - Kiểm tra file tồn tại chưa, nếu chưa thì tạo file với mảng rỗng [].
        - Đọc nội dung JSON và parse thành danh sách MemoryItem.
        """
        raise NotImplementedError("TODO: [Thành viên 2] Triển khai hàm load_all()")

    def save_all(self, items: List[MemoryItem]) -> None:
        """
        Ghi danh sách MemoryItem xuống file JSON.
        
        TODO: [Thành viên 2]
        - Ghi đè danh sách items dưới dạng JSON có format thụt lề (indent=2).
        """
        raise NotImplementedError("TODO: [Thành viên 2] Triển khai hàm save_all()")

    def get_active_memories(self, topic: Optional[str] = None) -> List[MemoryItem]:
        """
        Lọc danh sách các memory đang có status == 'active'.
        
        TODO: [Thành viên 2]
        - Lấy toàn bộ items từ load_all().
        - Lọc các items có status == 'active'.
        - Nếu có truyền topic thì lọc thêm theo topic tương ứng.
        """
        raise NotImplementedError("TODO: [Thành viên 2] Triển khai hàm get_active_memories()")

    def get_superseded_memories(self, topic: Optional[str] = None) -> List[MemoryItem]:
        """
        Lọc danh sách các memory đã bị thay thế (status == 'superseded').
        
        TODO: [Thành viên 2]
        - Lọc các items có status == 'superseded'.
        """
        raise NotImplementedError("TODO: [Thành viên 2] Triển khai hàm get_superseded_memories()")

    def update_rule_with_conflict_resolution(
        self,
        topic: str,
        new_rule: str,
        source: str,
    ) -> Tuple[MemoryItem, List[MemoryItem]]:
        """
        Cập nhật quy ước mới với cơ chế Conflict Resolution:
        
        TODO: [Thành viên 2]
        1. Tìm tất cả memory đang 'active' có cùng topic.
        2. Đánh dấu các memory cũ đó thành 'superseded', cập nhật thời gian và gán superseded_by.
        3. Tạo MemoryItem mới có status='active'.
        4. Ghi toàn bộ thay đổi xuống file JSON.
        5. Trả về tuple: (new_memory, list_of_superseded_memories).
        """
        raise NotImplementedError("TODO: [Thành viên 2] Triển khai hàm update_rule_with_conflict_resolution()")

    def reset_memory(self) -> None:
        """
        Xóa trắng dữ liệu trong kho memory về [] để phục vụ chạy lại test/demo.
        
        TODO: [Thành viên 2] Ghi mảng rỗng [] xuống self.file_path.
        """
        raise NotImplementedError("TODO: [Thành viên 2] Triển khai hàm reset_memory()")
