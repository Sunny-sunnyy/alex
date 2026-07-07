# Prompt: Tạo README cho folder `terraform/*/`

Copy toàn bộ nội dung bên dưới vào Agent Code. Thay `<FOLDER_PATH>` bằng đường dẫn thực tế (ví dụ: `terraform/5_database`).

---

## Nhiệm vụ

Tạo file `README.md` chi tiết cho folder `<FOLDER_PATH>`. File phải bằng **tiếng Việt có dấu**, mặc định **dưới 600 dòng**, đầy đủ nhưng súc tích.

Nếu sau khi khám phá folder và các part liên quan, bạn thấy folder chứa quá nhiều tài nguyên, dependency hoặc bối cảnh cần thiết và việc ép dưới 600 dòng sẽ làm README mất giá trị học tập hoặc tra cứu, bạn **được phép chủ động hỏi người dùng** để xin viết dài hơn 600 dòng. Nếu người dùng đồng ý, ưu tiên viết **vừa đủ để hiểu đúng** thay vì cắt ngắn máy móc.

## Quy trình

### Bước 1 — Khám phá folder terraform

Đọc tất cả file trong `<FOLDER_PATH>` (bỏ qua `.terraform/`, `terraform.tfstate`, `terraform.tfstate.backup`).

Phải đọc:
- `main.tf` — toàn bộ resource AWS
- `variables.tf` — tất cả input variables
- `outputs.tf` — tất cả outputs
- `terraform.tfvars.example` hoặc `terraform.tfvars` — giá trị thực tế đang dùng
- Các file `.auto.tfvars.json` nếu có
- `.terraform.lock.hcl` — version provider

### Bước 1.5 — Nắm bối cảnh từ các bài học trước có liên quan trực tiếp

Trước khi viết README, bạn phải đọc các **guide** và **folder code/terraform trước đó mà `<FOLDER_PATH>` phụ thuộc thực sự**.

Nguyên tắc:
- Không cần đọc máy móc tất cả các part trước nếu chúng không liên quan kỹ thuật trực tiếp
- Phải đọc đủ để hiểu folder Terraform hiện tại đang kế thừa resource, output, hoặc workflow nào từ các part trước
- Ví dụ: nếu đang viết cho `terraform/5_database`, bạn phải nắm được ít nhất các phần trước liên quan trực tiếp như `terraform/3_ingestion`, `terraform/4_researcher`, cùng các guide tương ứng nếu chúng tạo ra ngữ cảnh kỹ thuật mà Part 5 đang tiếp nối

Bạn có thể tự khám phá các file, folder chứa code khác để hiểu rõ thêm về bài học nếu thấy cần thiết hoặc nếu tôi cung cấp thiếu ngữ cảnh.

### Bước 2 — Tìm folder backend tương ứng

Tự động tìm folder backend được deploy bởi terraform này:

- Tìm trong `main.tf` các tham chiếu: `filename`, `image_uri`, `source_code_hash`, `handler`, đường dẫn `../../backend/...`
- Dùng `path.module` để xác định đúng đường dẫn tương đối
- Nếu tìm thấy folder backend → đọc tất cả file code trong đó để hiểu application code
- Nếu **không** tìm thấy → bỏ qua phần application code

### Bước 3 — Trích xuất cấu hình AWS

Từ `main.tf`, trích xuất:

**Từng resource một:**
- Resource type (`aws_lambda_function`, `aws_iam_role`, ...)
- Resource name (logical name trong Terraform)
- Tên thực tế trên AWS (`function_name`, `role name`, `bucket name`...)
- Các attribute quan trọng: `timeout`, `memory_size`, `runtime`, `handler`, `schedule_expression`, `authorization_type`...
- `depends_on` — thể hiện dependency giữa các resource

**IAM Roles & Policies:**
- Tổng hợp tất cả IAM roles, policies (managed + inline)
- Mỗi policy: actions + resources
- Trust relationships (principal + action)

**Environment Variables:**
- Tất cả biến môi trường inject vào Lambda/container
- Nguồn của từng biến (từ variable hay từ resource khác)
- Giá trị mặc định nếu có

**Locals & Conditions:**
- `locals {}` block — logic điều kiện
- `count` / `for_each` — resource nào được tạo có điều kiện

### Bước 4 — Viết README

#### Cấu trúc bắt buộc

**1. Tiêu đề + Mục tiêu (3-5 câu)**
- Folder này tạo ra những gì trên AWS
- Tương ứng với Guide nào
- Nếu implementation khác với guide gốc → ghi rõ

**2. Sơ đồ tài nguyên AWS (mermaid graph)**
- Thể hiện tất cả resource + dependency (depends_on, count condition)
- Gom nhóm theo chức năng (Compute, IAM, Storage, API, Scheduler...)

**3. Chi tiết từng tài nguyên**

Với mỗi resource quan trọng, dùng định dạng:

```markdown
### <số>. <Resource Type> — `<tên AWS>`

| Thuộc tính | Giá trị |
|-----------|---------|
| ... | ... |

| Condition | <nếu có> |
```

Gom các resource nhỏ/phụ thành 1 bảng tổng hợp nếu có quá nhiều.

**4. IAM Roles & Policies — tổng hợp**

```markdown
| Resource | Name | Type | Policies |
|----------|------|------|----------|
| ... | ... | Role/Policy | ... |
```

**5. Environment Variables tổng hợp** (nếu có Lambda/container)

```markdown
| Biến | Nguồn | Mặc định | Mô tả |
|------|-------|----------|-------|
| ... | ... | ... | ... |
```

**6. Outputs sau khi triển khai**

```markdown
| Output | Giá trị | Sensitive | Mô tả |
|--------|--------|-----------|-------|
| ... | ... | Yes/No | ... |
```

**7. Các biến cần điền trong `terraform.tfvars`**

```markdown
| Biến | Mô tả | Mặc định | Bắt buộc |
|------|-------|----------|----------|
| ... | ... | ... | Có/Không |
```

**8. Version Constraints**

```markdown
| Thành phần | Version |
|-----------|---------|
| Terraform CLI | >= ... |
| AWS Provider | ... |
| Backend | Local |
```

**9. Quan hệ với các phần khác (mermaid graph)**

- Thể hiện: folder này phụ thuộc vào Part nào, được Part nào dùng
- Kèm bảng chi tiết: folder nào, cần gì, mục đích

**10. Cách sử dụng nhanh**

```bash
# Từng bước một
cd <FOLDER_PATH>
cp terraform.tfvars.example terraform.tfvars
# ... chỉnh biến ...
terraform init
terraform apply
```

**11. Tóm tắt (checklist)**

Liệt kê tất cả resource được tạo + số lượng. Định dạng:

```markdown
- **X <Resource Type>** (`<tên>`) — mô tả ngắn
```

#### Nguyên tắc viết

- **Súc tích.** Mỗi resource mô tả 5-15 dòng. Gom các resource tương tự vào chung 1 bảng nếu có >12 resource.
- **Tiếng Việt có dấu.** Giữ nguyên thuật ngữ kỹ thuật bằng tiếng Anh (Lambda, endpoint, IAM role, policy...).
- **Dùng bảng.** Hầu hết thông số kỹ thuật nên ở dạng bảng để dễ đọc.
- **Diagram bắt buộc.** Tối thiểu 2 diagram mermaid: (1) sơ đồ tài nguyên AWS, (2) quan hệ cross-service.
- **Không lặp lại** thông tin từ `CLAUDE.md` hoặc `gameplan.md` trừ khi cần cho ngữ cảnh.
- **Không in secret values.** Đánh dấu `sensitive = true` trong output table, không hiển thị giá trị thật.
- **Phải có bối cảnh theo chuỗi bài học.** README không được mô tả folder Terraform hiện tại như một khối cô lập; phải chỉ ra nó kế thừa gì từ các part trước có liên quan trực tiếp.

#### Ràng buộc kỹ thuật

- Tổng file **mặc định dưới 600 dòng**
- Nếu folder nhiều nội dung và việc giới hạn 600 dòng làm giảm chất lượng README, bạn phải **xin phép người dùng** trước khi viết dài hơn 600 dòng
- Nếu folder backend tương ứng tồn tại → giới hạn mô tả application code trong **1 section ngắn** (dưới 30 dòng), dẫn link đến `backend/*/README.md` để biết chi tiết
- Nếu có >15 resource → chỉ mô tả chi tiết top 12 resource quan trọng nhất, còn lại gom vào bảng tổng hợp
- Nếu có locals phức tạp → giải thích ngắn gọn logic điều kiện

### Bước 5 — Tự kiểm tra trước khi ghi file

Trước khi ghi, kiểm tra:
1. Tất cả section bắt buộc đã có mặt?
2. Tên resource, biến, output có khớp chính xác với `main.tf` / `variables.tf` / `outputs.tf` không?
3. Các giá trị số (memory, timeout, rate limit...) có đúng không?
4. README đã thể hiện đúng bối cảnh từ các guide/folder trước có liên quan trực tiếp chưa?
5. Đếm dòng — có vượt 600 không? → Nếu vượt mà chưa được người dùng cho phép, phải hỏi trước khi ghi file
6. Không có TBD, TODO, placeholder nào chưa được thay thế?
7. Nếu implementation khác guide gốc → đã ghi rõ sự khác biệt chưa?
