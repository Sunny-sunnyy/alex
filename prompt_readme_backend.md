# Prompt: Tạo README cho folder `backend/*/`

Copy toàn bộ nội dung bên dưới vào Claude Code. Thay `<FOLDER_PATH>` bằng đường dẫn thực tế (ví dụ: `backend/planner`).

---

## Nhiệm vụ

Tạo file `README.md` chi tiết cho folder `<FOLDER_PATH>`. File phải bằng **tiếng Việt có dấu**, độ dài **dưới 500 dòng**, đầy đủ nhưng súc tích.

## Quy trình

### Bước 1 — Khám phá folder được chỉ định

Đọc **tất cả** file code trong `<FOLDER_PATH>` (bỏ qua `.venv`, `__pycache__`, `__init__.py`, file lock, file zip).

Xác định:
- File nào là **core logic** (handler, agent, server, main)
- File nào là **test** (test_*.py)
- File nào là **config** (pyproject.toml, .env.example)
- File nào là **deploy/build** (Dockerfile, package.py, deploy.py)

### Bước 2 — Tìm folder terraform tương ứng

Tự động tìm folder terraform quản lý hạ tầng cho folder backend này:

- Tìm trong `terraform/*/main.tf` xem file nào tham chiếu đến `<FOLDER_PATH>` (qua `filename`, `image_uri`, `source_code_hash`, hoặc comment)
- Nếu tìm thấy → đọc `main.tf`, `variables.tf`, `outputs.tf` của folder terraform đó
- Nếu **không** tìm thấy → bỏ qua phần hạ tầng, chỉ document code

### Bước 3 — Phân tích code

Trích xuất từ code:
- **Entry points**: endpoint HTTP, Lambda handler, CLI script
- **Mối liên kết import**: file nào import file nào
- **Biến môi trường**: tất cả `os.getenv()` / `os.environ.get()`
- **Dependencies**: từ `pyproject.toml`
- **Cấu trúc request/response**: từ Pydantic models, type hints, docstring
- **Constants quan trọng**: timeout, memory, model name, region

### Bước 4 — Viết README

#### Cấu trúc bắt buộc

**1. Tiêu đề + Nhiệm vụ chính (3-5 câu)**
- Folder này làm gì, vai trò trong hệ thống Alex
- Tương ứng với Guide nào trong khóa học

**2. Cấu trúc thư mục (tree ASCII)**
```
backend/<name>/
├── file_chinh.py        # Mô tả 1 dòng
├── file_phu.py          # Mô tả 1 dòng
└── ...
```

**3. Sơ đồ tổng quan (mermaid graph)**
- Thể hiện các thành phần trong folder + kết nối đến service AWS

**4. Chi tiết từng file**
Với mỗi file code, dùng định dạng sau:

```markdown
### <số>. `<tên file>` — <Vai trò ngắn>

**Vai trò:** 1 câu mô tả chính.

**Nhiệm vụ chi tiết:** (chỉ liệt kê nếu quan trọng)
- điểm 1
- điểm 2

**<Bảng thông số nếu có:>**
| Thuộc tính | Giá trị |
|-----------|---------|
| ... | ... |

**<Hàm/Class then chốt nếu có:>**
| Hàm/Class | Chức năng |
|-----------|-----------|
| ... | ... |
```

**5. Workflow (mermaid sequence diagram)**
- Ít nhất 1 sequence diagram thể hiện luồng chính
- Có thêm 1-2 diagram phụ nếu cần (build, deploy, retry...)

**6. Mối liên kết giữa các file (mermaid graph)**
- File nào import/ gọi/ phụ thuộc file nào

**7. Mối liên hệ với folder khác (mermaid graph + bảng)**
- Bảng: folder nào, cần gì, dùng ở đâu
- Graph: thể hiện data flow xuyên suốt các Part

**8. Cách sử dụng nhanh**
- Lệnh test local, build, deploy, check log

**9. Tóm tắt (checklist/bảng)**
- Liệt kê tất cả file + 1 câu mô tả

#### Nguyên tắc viết

- **Súc tích.** Mỗi file mô tả 5-15 dòng. Không lan man.
- **Tiếng Việt có dấu.** Giữ nguyên thuật ngữ kỹ thuật bằng tiếng Anh (Lambda, handler, endpoint, embedding, agent...).
- **Dùng bảng.** Ưu tiên bảng cho thông số kỹ thuật, biến môi trường, dependencies, constants.
- **Diagram vừa đủ.** 2-4 diagram mermaid, mỗi diagram 10-25 nodes.
- **Không lặp lại** thông tin đã có trong `CLAUDE.md` hoặc `gameplan.md` trừ khi cần thiết cho ngữ cảnh.
- **Tập trung vào "code làm gì" và "code liên kết với code nào"** — không sao chép nguyên văn code vào README.

#### Ràng buộc kỹ thuật

- Tổng file **dưới 500 dòng**
- Nếu folder terraform tương ứng tồn tại → giới hạn mô tả hạ tầng trong **1 section ngắn** (dưới 30 dòng), dẫn link đến `terraform/*/README.md` để biết chi tiết
- Nếu folder có >10 file code → chỉ mô tả chi tiết top 8 file quan trọng nhất, các file còn lại gom vào bảng tóm tắt

### Bước 5 — Tự kiểm tra trước khi ghi file

Trước khi ghi, kiểm tra:
1. Tất cả section bắt buộc đã có mặt?
2. Có chỗ nào TBD/TODO không? → Nếu có, sửa ngay
3. Có chỗ nào mâu thuẫn không? (vd: mô tả file này import file kia nhưng diagram không thể hiện)
4. Đếm dòng — có vượt 500 không? → Nếu vượt, cắt bớt phần ít quan trọng
5. Tên file, đường dẫn, biến môi trường có khớp với code thực tế không?
