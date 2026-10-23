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
        
        Triển khai bởi Thành viên 3 - Huy Bình:
        - Lấy active memories từ self.store.get_active_memories(topic=topic_filter).
        - Nếu không có memory nào: trả về base_system_prompt và [].
        - Nếu có: format danh sách quy ước kèm topic, rule, source theo khối Markdown
          [PROJECT ACTIVE MEMORIES & ARCHITECTURAL CONVENTIONS].
        - Ghép nối vào base_system_prompt và trả về (augmented_prompt, active_memories).
        """
        try:
            active_memories = self.store.get_active_memories(topic=topic_filter)
        except NotImplementedError:
            active_memories = []

        if not active_memories:
            return base_system_prompt, []

        convention_lines = [
            base_system_prompt.strip(),
            "",
            "### [PROJECT ACTIVE MEMORIES & ARCHITECTURAL CONVENTIONS]",
            "The following architectural conventions are currently active and MUST be strictly enforced across all interactions:",
        ]
        for item in active_memories:
            convention_lines.append(
                f"- **{item.topic}**: {item.rule} *(ID: {item.id}, Source: {item.source})*"
            )
        convention_lines.append("### [END OF ACTIVE CONVENTIONS]")

        augmented_prompt = "\n".join(convention_lines)
        return augmented_prompt, active_memories

    def display_injected_memory_panel(
        self,
        active_memories: List[MemoryItem],
        session_name: str = "New Session",
    ) -> None:
        """
        In bảng thông tin các Memory được inject vào Terminal một cách trực quan bằng thư viện rich.
        
        Triển khai bởi Thành viên 3 - Huy Bình:
        - Sử dụng Table và Panel của rich để hiển thị:
          Memory ID, Topic, Rule, Source, Status, Updated At.
        """
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table

            console = Console()
            if not active_memories:
                console.print(
                    Panel(
                        f"[yellow]No active persistent memories injected for '{session_name}'.[/yellow]\n"
                        f"[dim]Agent is operating strictly with base system prompt.[/dim]",
                        title=f"[bold cyan]Context Injection: {session_name}[/bold cyan]",
                        border_style="yellow",
                    )
                )
                return

            table = Table(
                title=f"Injected Persistent Memories ({len(active_memories)} active conventions)",
                border_style="bright_blue",
                header_style="bold cyan",
            )
            table.add_column("Memory ID", style="bold yellow", justify="center")
            table.add_column("Topic", style="bold magenta")
            table.add_column("Rule (Active Convention)", style="green")
            table.add_column("Source", style="blue")
            table.add_column("Status", style="bold bright_green", justify="center")
            table.add_column("Updated At", style="dim", justify="center")

            for mem in active_memories:
                table.add_row(
                    mem.id,
                    mem.topic,
                    mem.rule,
                    mem.source,
                    mem.status.upper(),
                    mem.updated_at,
                )

            console.print(
                Panel(
                    table,
                    title=f"[bold green] Injected System Prompt Context - [{session_name}][/bold green]",
                    subtitle="[italic cyan]Preserved via Persistent Memory across sessions[/italic cyan]",
                    border_style="green",
                )
            )
        except ImportError:
            # Fallback in trường hợp rich chưa được cài đặt
            print(f"\n--- Injected System Prompt Context: {session_name} ---")
            if not active_memories:
                print("No active persistent memories.")
                return
            for mem in active_memories:
                print(f"[{mem.id}] [{mem.status.upper()}] Topic: {mem.topic} | Rule: {mem.rule} (Source: {mem.source})")
            print("-------------------------------------------------------\n")

