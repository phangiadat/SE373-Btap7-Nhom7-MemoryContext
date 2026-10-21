# BÀI TẬP THỰC HÀNH BUỔI 07: PERSISTENT MEMORY, CONTEXT COMPACTION & CODE MODE
**Môn học:** Kỹ thuật xây dựng hệ thống Agentic AI (SE373) - Khoa Công nghệ Phần mềm, FIT - HCMUS  
**Nhóm thực hiện:** Nhóm 07  
**GitHub Repository:** [https://github.com/phangiadat/SE373-Btap7-Nhom7-MemoryContext](https://github.com/phangiadat/SE373-Btap7-Nhom7-MemoryContext)  

---

##  GIỚI THIỆU DỰ ÁN

Dự án cung cấp bộ khung kiến trúc (Boilerplate / Starter Scaffolding) gồm các interface, type hints và mô tả đặc tả chi tiết để **5 thành viên trong Nhóm 07 code song song độc lập**, giải quyết 3 thử thách kiến trúc của hệ thống AI Agent:
1. **Challenge A (Bắt buộc):** Persistent Memory (Lưu trữ quy ước dự án qua các session và giải quyết xung đột khi quy ước thay đổi).
2. **Challenge B1 (Bắt buộc):** Context Compaction (Nén session dài thành Structured Checkpoint 7 trường thông tin cốt lõi mà vẫn giữ trọn vẹn ngữ cảnh suy luận).
3. **Challenge B2 (Điểm cộng):** Code Mode (Thống kê lỗi trên 20 file log máy chủ bằng script runtime mà không nạp raw log vào LLM Context).

---

##  CẤU TRÚC THƯ MỤC DỰ ÁN

```text
bt_buoi07_memory_context/
├── docs/
│   └── TEAM_WORKFLOW_AND_SPEC.md   # Đặc tả kỹ thuật chi tiết & Bảng phân công Nhóm 07
├── data/
│   ├── project_memory.json         # Kho lưu trữ Persistent Memory (JSON)
│   └── logs/                       # Thư mục chứa 20 file log giả lập (server_01.log -> server_20.log)
├── src/
│   ├── __init__.py
│   ├── config.py                   # Cấu hình tập trung (Token limits, file paths, model)
│   ├── core_agent.py               # [Gia Đạt] Khung Core Agent Loop & đo lường input_tokens
│   ├── mock_env.py                 # [Gia Đạt] Khung Mock Data: 20 file log & test log 7.000 dòng
│   ├── memory_store.py             # [Gia Bảo] Khung MemoryItem & thuật toán Conflict Resolution
│   ├── memory_injector.py          # [Huy Bình] Khung lọc active memory & inject System Prompt
│   ├── compactor.py                # [Huy Phát] Khung Selective Compactor & Structured Checkpoint
│   └── code_mode.py                # [Thái Hưng] Khung Sandbox runtime run_code() + SDK tools proxy
├── demo_challenge_a.py             # [Huy Bình] Khung kịch bản kiểm chứng Challenge A qua 3 Session
├── demo_challenge_b1.py            # [Huy Phát] Khung kịch bản kiểm chứng Challenge B1 nén session dài
├── demo_challenge_b2.py            # [Thái Hưng] Khung kịch bản kiểm chứng Challenge B2 Code Mode
├── requirements.txt                # Danh sách thư viện phụ thuộc
├── .env.example                    # Mẫu cấu hình biến môi trường
├── .gitignore                      # Bỏ qua venv, __pycache__, .env
└── README.md                       # Hướng dẫn cài đặt và phân công
```

---

##  BẢNG PHÂN CÔNG THÀNH VIÊN NHÓM 07

Chi tiết xem tại tài liệu [docs/TEAM_WORKFLOW_AND_SPEC.md](docs/TEAM_WORKFLOW_AND_SPEC.md).

| Thành viên | Họ và Tên | Vai trò | File phụ trách | Nhánh Git |
| :---: | :--- | :--- | :--- | :--- |
| **TV 1** | **Gia Đạt** | Leader, Core Agent & Mock Data | `src/core_agent.py`, `src/mock_env.py` | `feat/dat-core-agent` |
| **TV 2** | **Gia Bảo** | Memory Storage & Conflict Curation | `src/memory_store.py`, `data/project_memory.json` | `feat/bao-memory-store` |
| **TV 3** | **Huy Bình** | Memory Injection & Challenge A Demo | `src/memory_injector.py`, `demo_challenge_a.py` | `feat/binh-challenge-a` |
| **TV 4** | **Huy Phát** | Compaction Pipeline & Challenge B1 Demo | `src/compactor.py`, `demo_challenge_b1.py` | `feat/phat-challenge-b1` |
| **TV 5** | **Thái Hưng** | Code Mode Runtime & Challenge B2 Demo | `src/code_mode.py`, `demo_challenge_b2.py` | `feat/hung-challenge-b2` |

---

##  HƯỚNG DẪN CÀI ĐẶT MÔI TRƯỜNG

### 1. Khởi tạo Virtual Environment
Mở terminal tại thư mục dự án:

**Trên Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Trên Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Cài đặt các gói phụ thuộc
```bash
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường
```bash
cp .env.example .env
```

---

##  LỆNH CHẠY KIỂM THỬ KHI HOÀN THÀNH

Khi từng thành viên hoàn thiện phần code của mình, chạy kiểm chứng bằng các lệnh sau:
- **Kiểm chứng Thử thách A (Huy Bình & Gia Bảo):** `python demo_challenge_a.py`
- **Kiểm chứng Thử thách B1 (Huy Phát & Gia Đạt):** `python demo_challenge_b1.py`
- **Kiểm chứng Thử thách B2 (Thái Hưng):** `python demo_challenge_b2.py`

---

##  QUY ƯỚC LÀM VIỆC TRÊN GIT

1. Đạt khởi tạo repository trên nhánh `main`.
2. Mỗi thành viên checkout nhánh riêng tương ứng (`feat/dat-core-agent`, `feat/bao-memory-store`, v.v.).
3. **Chỉ chỉnh sửa các file thuộc phân công của mình** để tránh Merge Conflict.
4. Đọc kỹ Hợp đồng giao tiếp (Interface Contracts) trong [docs/TEAM_WORKFLOW_AND_SPEC.md](docs/TEAM_WORKFLOW_AND_SPEC.md) trước khi code.
