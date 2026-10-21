# ĐẶC TẢ KỸ THUẬT VÀ QUY TRÌNH LÀM VIỆC NHÓM 07
**Môn học:** Kỹ thuật xây dựng hệ thống Agentic AI (SE373) - Khoa Công nghệ Phần mềm, FIT - HCMUS  
**Chủ đề:** Buổi 07 - Persistent Memory, Context Compaction & Code Mode  
**GitHub Repository:** [https://github.com/phangiadat/SE373-Btap7-Nhom7-MemoryContext](https://github.com/phangiadat/SE373-Btap7-Nhom7-MemoryContext)  
**Nhóm thực hiện:** Nhóm 07 (5 thành viên)

---

## 1. TỔNG QUAN HỆ THỐNG VÀ CÁC THỬ THÁCH (CHALLENGES)

Dự án cung cấp bộ khung kiến trúc (Boilerplate Scaffolding) phân tách độc lập theo từng file để 5 thành viên trong Nhóm 07 code song song mà không bị xung đột mã nguồn:
1. **Challenge A (Bắt buộc) - Persistent Memory & Conflict Curation:** Lưu trữ bền vững các quy ước dự án qua nhiều session hội thoại độc lập; tự động giải quyết xung đột khi quy ước tiến hóa (đánh dấu quy ước cũ là `superseded`, áp dụng quy ước mới là `active`).
2. **Challenge B1 (Bắt buộc) - Context Compaction & Structured Checkpoint:** Kiểm soát ngân sách ngữ cảnh khi session hội thoại quá dài (>50.000 tokens). Áp dụng chiến lược **Selective Compaction** (KEEP / TRUNCATE / DROP) và đóng gói trạng thái suy luận thành **Structured Checkpoint** 7 trường thông tin cốt lõi.
3. **Challenge B2 (Điểm cộng) - Code Mode Runtime:** Khai thác năng lực viết và thực thi code trong sandbox runtime để xử lý các tác vụ phân tích dữ liệu lớn (quét 20 file log máy chủ) mà **không đưa raw log vào Context Window** của LLM, tối ưu hóa triệt để chi phí token và độ trễ.

---

## 2. BẢNG PHÂN CÔNG CÔNG VIỆC CHI TIẾT (NHÓM 07)

| Thành viên | Họ và Tên | Vai trò & Trách nhiệm chính | File mã nguồn phụ trách | Branch Git tương ứng |
| :---: | :--- | :--- | :--- | :--- |
| **TV 1** | **Phan Gia Đạt** *(Leader)* | **Core Agent Loop & Mock Data** | `src/core_agent.py`<br>`src/mock_env.py` | `feat/dat-core-agent` |
| **TV 2** | **Gia Bảo** | **Memory Storage & Conflict Curation** | `src/memory_store.py`<br>`data/project_memory.json` | `feat/bao-memory-store` |
| **TV 3** | **Huy Bình** | **Memory Injection & Demo Challenge A** | `src/memory_injector.py`<br>`demo_challenge_a.py` | `feat/binh-challenge-a` |
| **TV 4** | **Huy Phát** | **Compaction Pipeline & Demo Challenge B1** | `src/compactor.py`<br>`demo_challenge_b1.py` | `feat/phat-challenge-b1` |
| **TV 5** | **Thái Hưng** | **Code Mode Runtime & Demo Challenge B2** | `src/code_mode.py`<br>`demo_challenge_b2.py` | `feat/hung-challenge-b2` |

---

## 3. CHI TIẾT NHIỆM VỤ CỤ THỂ CỦA TỪNG THÀNH VIÊN

### 1. Thành viên 1 - Phan Gia Đạt (Leader)
- **File phụ trách:** `src/core_agent.py` và `src/mock_env.py`
- **Branch:** `feat/dat-core-agent`
- **Nhiệm vụ cần tự code:**
  1. Trong `src/mock_env.py`:
     - Viết hàm `generate_mock_server_logs(target_dir, num_files=20)`: tạo các file `server_01.log` -> `server_20.log` chứa timestamp, log level (INFO, WARN, ERROR), endpoint, status code (200, 401, 500, 502, 504), latency.
     - Viết hàm `generate_mock_test_logs(total_lines=7000)`: tạo 7.000 dòng log test pytest, phần lớn là test PASSED, chèn đoạn FAILURES ghi nhận lỗi `refresh-token race condition` và ghi chú cách `tăng TTL thất bại`.
     - Viết hàm `generate_mock_source_code(total_lines=2000)`: sinh mã nguồn Python giả lập có hàm `refresh_access_token` bị bug race condition.
     - Viết hai mock tool `mock_read_file` và `mock_run_tests`.
  2. Trong `src/core_agent.py`:
     - Viết hàm `estimate_tokens(text: str) -> int`.
     - Hoàn thiện các method của class `CoreAgent`: `get_current_input_tokens`, `add_message`, `execute_tool`, và `step`.
     - Quản lý mảng tin nhắn `messages` và đối tượng `TokenUsage` sau mỗi lượt.

### 2. Thành viên 2 - Gia Bảo
- **File phụ trách:** `src/memory_store.py` và `data/project_memory.json`
- **Branch:** `feat/bao-memory-store`
- **Nhiệm vụ cần tự code:**
  1. Trong `src/memory_store.py`:
     - Cài đặt đọc/ghi danh sách `MemoryItem` xuống file JSON: `load_all()` và `save_all()`.
     - Cài đặt hàm lọc `get_active_memories(topic)` và `get_superseded_memories(topic)`.
     - Cài đặt thuật toán giải quyết xung đột `update_rule_with_conflict_resolution(topic, new_rule, source)`:
       * Tìm tất cả memory đang `active` của cùng `topic`.
       * Đánh dấu chúng thành `superseded`, cập nhật timestamp `updated_at`, gán `superseded_by = new_memory.id`.
       * Tạo đối tượng `MemoryItem` mới với trạng thái `active`.
       * Ghi dữ liệu xuống file `data/project_memory.json`.

### 3. Thành viên 3 - Huy Bình
- **File phụ trách:** `src/memory_injector.py` và `demo_challenge_a.py`
- **Branch:** `feat/binh-challenge-a`
- **Nhiệm vụ cần tự code:**
  1. Trong `src/memory_injector.py`:
     - Viết hàm `assemble_system_prompt()`: lấy các active memory từ store, format thành block markdown `[PROJECT ACTIVE MEMORIES & ARCHITECTURAL CONVENTIONS]` và ghép vào System Prompt.
     - Viết hàm `display_injected_memory_panel()`: in thông tin memory ra terminal bằng thư viện `rich`.
  2. Trong `demo_challenge_a.py`:
     - Triển khai `run_session_1()`: chốt 3 quy ước (PostgreSQL, TypeScript, JWT) và lưu vào store.
     - Triển khai `run_session_2()`: mở session mới, nạp memory, kiểm tra Agent nhớ đúng quy ước (Chứng minh 1). Sau đó đổi quy ước sang Session Cookie, đánh dấu JWT thành `superseded`.
     - Triển khai `run_session_3()`: mở session mới, kiểm tra Agent tự động dùng Session Cookie và không nhắc lại JWT (Chứng minh 2).

### 4. Thành viên 4 - Huy Phát
- **File phụ trách:** `src/compactor.py` và `demo_challenge_b1.py`
- **Branch:** `feat/phat-challenge-b1`
- **Nhiệm vụ cần tự code:**
  1. Trong `src/compactor.py`:
     - Cài đặt Pipeline 5 bước:
       * `observe_token_budget()`: đo lường token và kiểm tra ngưỡng budget.
       * `prune_tool_output()`: áp dụng Selective Compaction (KEEP lỗi/ràng buộc, TRUNCATE log test, DROP test passed lặp lại).
       * `build_structured_checkpoint()`: trích xuất/đóng gói đủ 7 trường (`goal`, `current_state`, `constraints`, `findings`, `failed_attempts`, `files`, `next_action`).
       * `reinject_rules_and_plan()`: tạo mảng messages mới với checkpoint và active rules.
       * `run_pipeline()`: chạy toàn bộ pipeline và tính % token tiết kiệm.
  2. Trong `demo_challenge_b1.py`:
     - Mô phỏng session dài với 2.000 dòng code và 7.000 dòng log test (>50.000 tokens).
     - Chạy compactor và in bảng thống kê giảm token (>90%).
     - Đặt câu hỏi kiểm tra: chứng minh Agent nhớ lỗi race condition, không lặp lại cách tăng TTL đã thất bại, và thực hiện đúng Redis Redlock / DB lock.

### 5. Thành viên 5 - Thái Hưng
- **File phụ trách:** `src/code_mode.py` và `demo_challenge_b2.py`
- **Branch:** `feat/hung-challenge-b2`
- **Nhiệm vụ cần tự code:**
  1. Trong `src/code_mode.py`:
     - Xây dựng `CodeModeToolsProxy`: cài đặt `list_files()` và `read_file()` an toàn trong thư mục logs.
     - Xây dựng `CodeExecutionRuntime`: cài đặt `run_code(code: str)`: chuẩn bị namespace có biến `tools`, chuyển hướng stdout để bắt kết quả in, thiết lập timeout an toàn.
  2. Trong `demo_challenge_b2.py`:
     - Viết script Python mẫu mà Agent sẽ sinh để quét 20 file log trong runtime.
     - Chạy script qua runtime và hứng kết quả thống kê Top 5 lỗi 5xx.
     - In bảng so sánh số token tiêu thụ giữa Native Tool Calling (nạp raw logs) vs Code Mode.

---

## 4. HỢP ĐỒNG GIAO TIẾP GIỮA CÁC MODULE (INTERFACE CONTRACTS)

Cả 5 thành viên phải tuân thủ đúng chữ ký hàm (Function Signatures) sau để khi ghép lại hệ thống hoạt động khớp 100%:

### 1. `src/core_agent.py` (Gia Đạt)
```python
def estimate_tokens(text: str) -> int: ...

class CoreAgent:
    def __init__(self, system_prompt: str = "...", tools: Optional[Dict] = None, token_budget_limit: int = 8000): ...
    def get_current_input_tokens(self) -> int: ...
    def add_message(self, role: str, content: str, name: Optional[str] = None) -> AgentMessage: ...
    def execute_tool(self, tool_name: str, **kwargs) -> str: ...
    def step(self, user_input: str, simulate_llm_response: Optional[str] = None) -> str: ...
```

### 2. `src/memory_store.py` (Gia Bảo)
```python
class MemoryStore:
    def __init__(self, file_path: Path = MEMORY_FILE_PATH): ...
    def load_all(self) -> List[MemoryItem]: ...
    def save_all(self, items: List[MemoryItem]) -> None: ...
    def get_active_memories(self, topic: Optional[str] = None) -> List[MemoryItem]: ...
    def get_superseded_memories(self, topic: Optional[str] = None) -> List[MemoryItem]: ...
    def update_rule_with_conflict_resolution(
        self, topic: str, new_rule: str, source: str
    ) -> Tuple[MemoryItem, List[MemoryItem]]: ...
    def reset_memory(self) -> None: ...
```

### 3. `src/memory_injector.py` (Huy Bình)
```python
class MemoryInjector:
    def __init__(self, store: Optional[MemoryStore] = None): ...
    def assemble_system_prompt(
        self, base_system_prompt: str = "...", topic_filter: Optional[str] = None
    ) -> Tuple[str, List[MemoryItem]]: ...
    def display_injected_memory_panel(self, active_memories: List[MemoryItem], session_name: str = "New Session") -> None: ...
```

### 4. `src/compactor.py` (Huy Phát)
```python
class ContextCompactor:
    def __init__(self, token_budget_limit: int = 8000, warning_threshold: float = 0.75): ...
    def observe_token_budget(self, messages: List[AgentMessage]) -> TokenBudgetReport: ...
    def prune_tool_output(self, raw_output: str, max_lines_kept: int = 40) -> str: ...
    def build_structured_checkpoint(
        self, messages: List[AgentMessage], custom_checkpoint: Optional[StructuredCheckpoint] = None
    ) -> StructuredCheckpoint: ...
    def reinject_rules_and_plan(
        self, base_system_prompt: str, checkpoint: StructuredCheckpoint, active_rules: Optional[List[str]] = None
    ) -> List[AgentMessage]: ...
    def run_pipeline(
        self, messages: List[AgentMessage], base_system_prompt: str, active_rules: Optional[List[str]] = None
    ) -> Tuple[List[AgentMessage], StructuredCheckpoint, Dict[str, Any]]: ...
    def display_checkpoint_panel(self, checkpoint: StructuredCheckpoint, metrics: Dict[str, Any]) -> None: ...
```

### 5. `src/code_mode.py` (Thái Hưng)
```python
class CodeModeToolsProxy:
    def list_files(self, extension: str = ".log") -> List[str]: ...
    def read_file(self, filename: str) -> str: ...

class CodeExecutionRuntime:
    def __init__(self, timeout_seconds: int = 10): ...
    def run_code(self, code: str) -> CodeExecutionResult: ...
```

---

## 5. QUY TRÌNH PHỐI HỢP TRÊN GIT (TRÁNH MERGE CONFLICT)

1. **Khởi tạo repo và commit khung dự án (Leader Gia Đạt thực hiện):**
   ```bash
   git init
   git add .
   git commit -m "chore: scaffold boilerplate interfaces and task specs for team 07"
   git branch -M main
   git remote add origin https://github.com/phangiadat/SE373-Btap7-Nhom7-MemoryContext.git
   git push -u origin main
   ```
2. **Tạo 5 nhánh tính năng riêng biệt (Từng thành viên pull về và tạo branch):**
   - **Gia Đạt:** `git checkout -b feat/dat-core-agent`
   - **Gia Bảo:** `git checkout -b feat/bao-memory-store`
   - **Huy Bình:** `git checkout -b feat/binh-challenge-a`
   - **Huy Phát:** `git checkout -b feat/phat-challenge-b1`
   - **Thái Hưng:** `git checkout -b feat/hung-challenge-b2`
3. **Quy tắc làm việc:** Mỗi thành viên **chỉ chỉnh sửa đúng các file được phân công** trong bảng ở Mục 2. Tuyệt đối không thay đổi kiểu dữ liệu đầu vào/ra của Interface Contracts.
