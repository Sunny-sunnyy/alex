# `scripts` — orchestration script cho local/dev/deploy của Guide 7

`scripts` là bộ CLI Python hỗ trợ **Guide 7 - Frontend & API** trong repo Alex. Thư mục này không chứa business logic tài chính; nó đóng vai trò automation layer để chạy local đồng thời frontend + backend, deploy production lên AWS, và destroy hạ tầng Part 7 khi cần tiết kiệm chi phí. Theo code hiện tại, các script này bám trực tiếp vào `backend/api`, `frontend`, và `terraform/7_frontend`, đồng thời gián tiếp kế thừa remote state từ Part 5 và Part 6 qua Terraform.

## Cấu trúc thư mục

```text
scripts/
├── run_local.py         # Chạy backend/api và frontend song song trên máy local
├── deploy.py            # Package Lambda, apply Terraform, build frontend, upload S3, invalidate CloudFront
├── destroy.py           # Empty S3 bucket, terraform destroy, dọn artifact local
├── pyproject.toml       # Dependency tối thiểu cho các script
└── uv.lock              # Lock file của uv project
```

## Sơ đồ tổng quan

```mermaid
graph TD
    RL[run_local.py] --> API[backend/api]
    RL --> FE[frontend]

    DEP[deploy.py] --> PKG[backend/api/package_docker.py]
    DEP --> TF7[terraform/7_frontend]
    DEP --> BUILD[frontend npm build]
    DEP --> S3[S3 frontend bucket]
    DEP --> CF[CloudFront invalidation]

    DES[destroy.py] --> S3RM[Empty S3 bucket]
    DES --> TFD[terraform destroy]
    DES --> CLEAN[Delete api zip + frontend build artifacts]

    TF7 --> TF5[remote state Part 5]
    TF7 --> TF6[remote state Part 6]
```

## Bối cảnh phụ thuộc trực tiếp

- `run_local.py` phụ thuộc trực tiếp vào:
  - `backend/api/main.py`
  - `frontend` dev server
  - file môi trường `.env` và `frontend/.env.local`
- `deploy.py` phụ thuộc trực tiếp vào:
  - `backend/api/package_docker.py`
  - `terraform/7_frontend`
  - `frontend` production build
  - AWS CLI + Docker + Terraform
- `destroy.py` phụ thuộc trực tiếp vào:
  - `terraform/7_frontend`
  - output `s3_bucket_name`
  - artifact local từ `backend/api` và `frontend`

Chi tiết hạ tầng production nằm ở [terraform/7_frontend/README.md](/home/hieu0606sunny/AiProduction_t6_2026_wsl/projects/alex/terraform/7_frontend/README.md). Với môi trường hiện tại, hãy coi `ap-southeast-1` là region chính nếu không có override khác.

## Chi tiết từng file

### 1. `run_local.py` — chạy local full stack

**Vai trò:** Script dev tiện dụng để bật đồng thời FastAPI backend và Next.js frontend trên máy local.

**Nhiệm vụ chi tiết:**
- kiểm tra `node`, `npm`, `uv`
- kiểm tra tồn tại `.env` và `frontend/.env.local`
- tự cài `httpx` nếu thiếu
- khởi động `backend/api` bằng `uv run main.py`
- khởi động `frontend` bằng `npm run dev`
- health-check backend `http://localhost:8000/health`
- probe frontend `http://localhost:3000`
- theo dõi process và cleanup khi `Ctrl+C`

**Thông số runtime:**

| Thuộc tính | Giá trị |
|---|---|
| Backend local URL | `http://localhost:8000` |
| Frontend local URL | `http://localhost:3000` |
| Backend startup timeout | 30s |
| Frontend startup timeout | 30s |
| Windows special case | `shell=True` cho `npm` |

**Hàm then chốt:**

| Hàm | Chức năng |
|---|---|
| `check_requirements()` | check `node`, `npm`, `uv` |
| `check_env_files()` | bắt buộc `.env` và `.env.local` tồn tại |
| `start_backend()` | chạy `uv run main.py` trong `backend/api` |
| `start_frontend()` | chạy `npm run dev` trong `frontend` |
| `monitor_processes()` | theo dõi stdout và phát hiện process chết |
| `cleanup()` | terminate/kill toàn bộ subprocess |

### 2. `deploy.py` — deploy production cho Part 7

**Vai trò:** Script chính để deploy end-to-end frontend + API production.

**Nhiệm vụ chi tiết:**
- kiểm tra `docker`, `terraform`, `npm`, `aws`
- kiểm tra Docker đang chạy và AWS credentials hợp lệ
- package Lambda API bằng Docker
- `terraform apply` trong `terraform/7_frontend`
- lấy `api_gateway_url`, `cloudfront_url`, `s3_bucket_name`
- tạo `.env.production.local` cho frontend build
- `npm run build` để xuất static site
- upload frontend lên S3 theo nhóm content-type
- tạo CloudFront invalidation

**Workflow thực tế trong code:**

| Bước | Hàm |
|---|---|
| Check prerequisites | `check_prerequisites()` |
| Build `api_lambda.zip` | `package_lambda()` |
| Apply Part 7 Terraform | `deploy_terraform()` |
| Build frontend static export | `build_frontend()` |
| Upload và invalidate | `upload_frontend()` |
| In summary | `display_deployment_info()` |

**Toolchain bắt buộc:**

| Tool | Lý do |
|---|---|
| Docker | package Lambda tương thích AWS |
| Terraform | deploy Part 7 infrastructure |
| npm | build Next.js frontend |
| AWS CLI | upload S3 và invalidate CloudFront |

**Điểm implementation quan trọng:**
- script deploy hạ tầng trước để lấy `api_gateway_url`, rồi mới build frontend
- dùng `.env.production.local` để override `NEXT_PUBLIC_API_URL`, không sửa `.env.local`
- nếu không tìm được CloudFront distribution ID thì vẫn sync S3, chỉ bỏ qua invalidation tự động

### 3. `destroy.py` — teardown Part 7

**Vai trò:** Script dọn hạ tầng production của Guide 7.

**Nhiệm vụ chi tiết:**
- yêu cầu người dùng gõ `yes`
- lấy `s3_bucket_name` từ `terraform output`
- xóa object trong bucket trước khi destroy
- chạy `terraform destroy` trong `terraform/7_frontend`
- xóa artifact local:
  - `backend/api/api_lambda.zip`
  - `frontend/out`
  - `frontend/.next`

**Thông số quan trọng:**

| Thuộc tính | Giá trị |
|---|---|
| Terraform target folder | `terraform/7_frontend` |
| Bucket output name | `s3_bucket_name` |
| Prompt xác nhận | phải gõ `yes` |

**Lưu ý kỹ thuật:**
- script có một lệnh `aws s3api delete-objects` dùng cú pháp `$(...)` dạng shell nhưng lại truyền như list argv; path xóa versioned objects này hiện không thực sự portable
- kể cả khi bước xóa version lỗi, script vẫn tiếp tục teardown

### 4. `pyproject.toml` — dependency của script layer

**Vai trò:** uv project tối giản cho thư mục `scripts`.

**Dependencies:**

| Package | Mục đích |
|---|---|
| `httpx` | health-check localhost trong `run_local.py` |

### 5. `uv.lock` — lock file

**Vai trò:** khóa dependency cho `scripts` project để local run ổn định hơn giữa các máy.

## Workflow

### Workflow 1: Chạy local full stack

```mermaid
sequenceDiagram
    participant User as Developer
    participant Script as run_local.py
    participant API as backend/api
    participant FE as frontend
    participant Browser as Browser

    User->>Script: uv run run_local.py
    Script->>Script: check node/npm/uv
    Script->>Script: check .env + .env.local
    Script->>API: uv run main.py
    Script->>API: GET /health polling
    API-->>Script: 200 healthy
    Script->>FE: npm run dev
    Script->>Browser: probe http://localhost:3000
    FE-->>Script: ready
    User->>Browser: mở app local
    Script->>Script: monitor logs đến khi Ctrl+C
```

### Workflow 2: Deploy production Part 7

```mermaid
sequenceDiagram
    participant User as Developer
    participant Script as deploy.py
    participant Packager as backend/api/package_docker.py
    participant TF as terraform/7_frontend
    participant FE as frontend
    participant AWS as S3 + CloudFront + Lambda + API GW

    User->>Script: uv run deploy.py
    Script->>Script: check docker/terraform/npm/aws
    Script->>Packager: build api_lambda.zip
    Script->>TF: terraform apply
    TF-->>Script: api_url + cloudfront_url + bucket
    Script->>FE: write .env.production.local
    Script->>FE: npm run build
    Script->>AWS: aws s3 cp/sync upload static export
    Script->>AWS: create CloudFront invalidation
    Script-->>User: in deployment summary
```

### Workflow 3: Destroy Part 7

```mermaid
sequenceDiagram
    participant User as Developer
    participant Script as destroy.py
    participant TF as terraform/7_frontend
    participant S3 as frontend bucket
    participant FS as local filesystem

    User->>Script: uv run destroy.py
    Script->>User: ask "yes"
    User-->>Script: yes
    Script->>TF: terraform output -raw s3_bucket_name
    Script->>S3: aws s3 rm --recursive
    Script->>TF: terraform destroy
    Script->>FS: delete api_lambda.zip, frontend/out, frontend/.next
    Script-->>User: destruction summary
```

## Mối liên kết giữa các file

```mermaid
graph LR
    RL[run_local.py] --> API[backend/api/main.py]
    RL --> FE[frontend npm run dev]
    DEP[deploy.py] --> PKG[backend/api/package_docker.py]
    DEP --> TF[terraform/7_frontend]
    DEP --> FE
    DES[destroy.py] --> TF
    DES --> FEOUT[frontend/out .next]
    DES --> ZIP[backend/api/api_lambda.zip]
    PY[pyproject.toml] --> RL
```

## Mối liên hệ với folder khác

```mermaid
graph TD
    SCRIPTS[scripts] --> API[backend/api]
    SCRIPTS --> FE[frontend]
    SCRIPTS --> TF7[terraform/7_frontend]
    TF7 --> TF5[terraform/5_database]
    TF7 --> TF6[terraform/6_agents]
    API --> DB[backend/database]
    TF6 --> Planner[backend/planner]
```

| Folder | Cần gì | Dùng ở script nào |
|---|---|---|
| `backend/api` | local server, Lambda zip packaging | `run_local.py`, `deploy.py`, `destroy.py` |
| `frontend` | dev server, production build, static export | cả 3 script |
| `terraform/7_frontend` | API/S3/CloudFront infrastructure | `deploy.py`, `destroy.py` |
| `terraform/5_database` | remote state cho Part 7 | gián tiếp qua `deploy.py` |
| `terraform/6_agents` | remote state queue ARN/URL | gián tiếp qua `deploy.py` |

## Cách sử dụng nhanh

```bash
cd scripts

# Chạy local frontend + backend
uv run run_local.py
```

```bash
cd scripts

# Deploy production Guide 7
uv run deploy.py
```

```bash
cd scripts

# Destroy production Guide 7
uv run destroy.py
```

```bash
# Sau deploy, xem log API Lambda
aws logs tail /aws/lambda/alex-api --follow --region ap-southeast-1
```

## Tóm tắt

| File | Vai trò ngắn |
|---|---|
| `run_local.py` | chạy local full stack và giám sát subprocess |
| `deploy.py` | deploy end-to-end Part 7 lên AWS |
| `destroy.py` | teardown Part 7 và dọn artifact local |
| `pyproject.toml` | dependency tối thiểu cho script layer |
| `uv.lock` | lock dependency cho uv |

Checklist chức năng:

- Có script local dev cho frontend + backend
- Có script deploy package Lambda + Terraform + S3 + CloudFront
- Có script destroy có xác nhận
- Có phụ thuộc trực tiếp vào `backend/api`, `frontend`, `terraform/7_frontend`
