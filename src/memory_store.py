# LUỒNG HOẠT ĐỘNG CỦA FILE:
# 1. MemoryItem giữ nguyên schema của hợp đồng giao tiếp cho từng quy ước.
# 2. MemoryStore đọc mảng JSON từ file; nếu file chưa có thì tạo file chứa [].
# 3. Khi ghi, store lưu toàn bộ MemoryItem vào file tạm cùng thư mục rồi thay
#    file chính để tránh file JSON bị ghi dở khi chương trình dừng đột ngột.
# 4. Các hàm truy vấn chỉ trả về quy ước active hoặc superseded, có thể lọc topic.
# 5. Khi có quy ước mới, store tạo ID UUID mới, chuyển mọi bản active cùng topic
#    sang superseded, trỏ superseded_by tới ID mới, rồi thêm bản active mới.
# 6. Tất cả thay đổi được ghi xuống JSON; MemoryStore ở phiên sau đọc lại file.
# 7. reset_memory() ghi [] để có thể chạy lại demo từ đầu.

"""Lưu quy ước dự án bằng JSON và giữ lịch sử khi quy ước thay đổi."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Literal, Optional, Tuple
from uuid import uuid4

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
    """Đọc, ghi và cập nhật quy ước trong một file JSON."""

    def __init__(self, file_path: Path = MEMORY_FILE_PATH) -> None:
        self.file_path: Path = file_path

    def load_all(self) -> List[MemoryItem]:
        """Đọc JSON thành MemoryItem; tạo kho rỗng nếu file chưa tồn tại."""
        if not self.file_path.exists():
            self.save_all([])
            return []

        # utf-8-sig đọc được cả file UTF-8 thường lẫn file mẫu có BOM của repo.
        with self.file_path.open("r", encoding="utf-8-sig") as memory_file:
            data = json.load(memory_file)
        return [MemoryItem.model_validate(item) for item in data]

    def save_all(self, items: List[MemoryItem]) -> None:
        """Ghi toàn bộ danh sách bằng cách thay file JSON sau khi ghi xong."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Optional[Path] = None

        try:
            # File tạm cùng thư mục để os.replace thay file đích trong một bước.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                prefix=f".{self.file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(
                    [item.model_dump() for item in items],
                    temporary_file,
                    ensure_ascii=False,
                    indent=2,
                )
                temporary_file.flush()
                os.fsync(temporary_file.fileno())

            os.replace(temporary_path, self.file_path)
        finally:
            # Nếu ghi/thay file lỗi, không để lại file tạm chứa dữ liệu dở.
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def get_active_memories(self, topic: Optional[str] = None) -> List[MemoryItem]:
        """Lấy các quy ước đang dùng, hoặc chỉ các quy ước thuộc topic."""
        return [
            item
            for item in self.load_all()
            if item.status == "active" and (topic is None or item.topic == topic)
        ]

    def get_superseded_memories(self, topic: Optional[str] = None) -> List[MemoryItem]:
        """Lấy lịch sử quy ước đã bị thay thế, có thể lọc theo topic."""
        return [
            item
            for item in self.load_all()
            if item.status == "superseded" and (topic is None or item.topic == topic)
        ]

    def update_rule_with_conflict_resolution(
        self,
        topic: str,
        new_rule: str,
        source: str,
    ) -> Tuple[MemoryItem, List[MemoryItem]]:
        """Lưu quy ước mới và chuyển mọi bản active cùng topic vào lịch sử."""
        items = self.load_all()
        updated_at = datetime.now(timezone.utc).isoformat()
        new_item = MemoryItem(
            id=str(uuid4()),
            topic=topic,
            rule=new_rule,
            status="active",
            source=source,
            updated_at=updated_at,
        )

        superseded_items: List[MemoryItem] = []
        for item in items:
            if item.topic == topic and item.status == "active":
                item.status = "superseded"
                item.updated_at = updated_at
                item.superseded_by = new_item.id
                superseded_items.append(item)

        items.append(new_item)
        self.save_all(items)
        return new_item, superseded_items

    def reset_memory(self) -> None:
        """Xóa dữ liệu của lần chạy trước để bắt đầu demo lại."""
        self.save_all([])
