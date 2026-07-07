# `terraform/3_ingestion` — Hạ tầng AWS cho Part 3 (Ingestion Pipeline)

Thư mục này chứa toàn bộ **Infrastructure as Code** cho **Part 3 - Ingestion Pipeline** của dự án Alex.

Vai trò: biến code trong `backend/ingest` thành một dịch vụ AWS hoàn chỉnh — nhận văn bản, gọi SageMaker để tạo embedding, lưu vector vào S3 Vectors, và public endpoint có bảo vệ API key.

---

## Mục tiêu

Sau Part 2 (SageMaker endpoint), Part 3 cần bổ sung:

1. Một backend nhận văn bản đầu vào
2. Một Lambda gọi sang SageMaker để tạo embedding
3. Một API Gateway public để client gọi được
4. Cơ chế xác thực bằng API key + Usage Plan
5. Xuất thông tin cấu hình để dùng cho Part 4

---

## Sơ đồ tài nguyên AWS được tạo

```
S3 Bucket (alex-vectors-<account_id>)
  ├─ Versioning (Enabled)
  ├─ SSE-S3 AES256 Encryption
  └─ Public Access Block (4 flags = true)

IAM Role (alex-ingest-lambda-role)
  └─ Inline Policy (alex-ingest-lambda-policy)
       ├─ CloudWatch Logs
       ├─ S3 CRUD (bucket + objects)
       ├─ SageMaker InvokeEndpoint
       └─ S3 Vectors (Put/Query/Get/Delete)

Lambda Function (alex-ingest)
  │  runtime: python3.12, memory: 512MB, timeout: 60s
  │  handler: ingest_s3vectors.lambda_handler
  │  env: VECTOR_BUCKET, SAGEMAKER_ENDPOINT
  │  code: ../../backend/ingest/lambda_function.zip
  │
  ▼
CloudWatch Log Group (/aws/lambda/alex-ingest)
  │  retention: 7 days

API Gateway REST API (alex-api)
  ├─ Resource: /ingest
  │    └─ Method: POST (api_key_required = true)
  │         └─ Integration: AWS_PROXY → Lambda alex-ingest
  ├─ Deployment (sha1 trigger, create_before_destroy)
  ├─ Stage: prod
  ├─ API Key (alex-api-key)
  └─ Usage Plan (alex-usage-plan)
       ├─ Quota: 10,000 req/month
       ├─ Throttle: 100 rate / 200 burst
       └─ Key Binding: alex-api-key
```

---

## Chi tiết từng tài nguyên AWS

### 1. S3 Bucket — `alex-vectors-<account_id>`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-vectors-<account_id>` (account_id lấy từ `data.aws_caller_identity`) |
| Versioning | **Enabled** |
| Encryption (SSE) | **AES256** (SSE-S3) |
| Block Public ACLs | **true** |
| Block Public Policy | **true** |
| Ignore Public ACLs | **true** |
| Restrict Public Buckets | **true** |
| Tags | `Project=alex`, `Part=3` |

Bucket này lưu dữ liệu vector. Toàn bộ public access bị chặn ở cấp bucket.

### 2. IAM Role — `alex-ingest-lambda-role`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-ingest-lambda-role` |
| Trust Policy | Cho phép `lambda.amazonaws.com` assume role (`sts:AssumeRole`) |
| Tags | `Project=alex`, `Part=3` |

### 3. IAM Inline Policy — `alex-ingest-lambda-policy`

Gắn trực tiếp vào role `alex-ingest-lambda-role`. Đây là policy tổng hợp các quyền tối thiểu:

| Nhóm quyền | Actions | Resource |
|-----------|---------|----------|
| CloudWatch Logs | `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` | `arn:aws:logs:<region>:<account>:*` |
| S3 Bucket | `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` | `alex-vectors-<account_id>` và `alex-vectors-<account_id>/*` |
| SageMaker | `sagemaker:InvokeEndpoint` | `arn:aws:sagemaker:<region>:<account>:endpoint/<sagemaker_endpoint_name>` |
| S3 Vectors | `s3vectors:PutVectors`, `s3vectors:QueryVectors`, `s3vectors:GetVectors`, `s3vectors:DeleteVectors` | `arn:aws:s3vectors:<region>:<account>:bucket/alex-vectors-<account_id>/index/*` |

### 4. Lambda Function — `alex-ingest`

| Thuộc tính | Giá trị |
|-----------|---------|
| Function Name | **`alex-ingest`** |
| Runtime | **python3.12** |
| Handler | `ingest_s3vectors.lambda_handler` |
| Memory | **512 MB** |
| Timeout | **60 giây** |
| IAM Role | `alex-ingest-lambda-role` |
| Code Source | `../../backend/ingest/lambda_function.zip` |
| Source Code Hash | `filebase64sha256` của zip (để tự động redeploy khi code đổi) |
| Tags | `Project=alex`, `Part=3` |

**Environment Variables của Lambda:**

| Biến | Giá trị | Mô tả |
|------|--------|-------|
| `VECTOR_BUCKET` | `alex-vectors-<account_id>` | Tên bucket nơi lưu dữ liệu vector |
| `SAGEMAKER_ENDPOINT` | Từ biến `var.sagemaker_endpoint_name` | Tên endpoint embedding (từ Part 2) |

### 5. CloudWatch Log Group — `/aws/lambda/alex-ingest`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `/aws/lambda/alex-ingest` |
| Retention | **7 ngày** |
| Tags | `Project=alex`, `Part=3` |

### 6. API Gateway REST API — `alex-api`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-api` |
| Description | `Alex Financial Planner API` |
| Endpoint Type | **REGIONAL** |
| Tags | `Project=alex`, `Part=3` |

### 7. API Resource & Method — `POST /ingest`

| Thuộc tính | Giá trị |
|-----------|---------|
| Path | `/ingest` |
| HTTP Method | **POST** |
| Authorization | `NONE` |
| API Key Required | **true** |
| Integration Type | `AWS_PROXY` |
| Integration Target | Lambda `alex-ingest` |

API Gateway chuyển gần như nguyên bản HTTP request thành event cho Lambda handler xử lý.

### 8. Lambda Permission cho API Gateway

| Thuộc tính | Giá trị |
|-----------|---------|
| Statement ID | `AllowAPIGatewayInvoke` |
| Action | `lambda:InvokeFunction` |
| Principal | `apigateway.amazonaws.com` |
| Source ARN | `<api-execution-arn>/*/*` |

### 9. API Deployment

| Thuộc tính | Giá trị |
|-----------|---------|
| Trigger | `sha1(jsonencode([resource.ingest.id, method.ingest_post.id, integration.lambda.id]))` |
| Lifecycle | `create_before_destroy = true` |

Terraform tự động tạo deployment mới khi bất kỳ thành phần nào trong trigger thay đổi.

### 10. API Stage — `prod`

| Thuộc tính | Giá trị |
|-----------|---------|
| Stage Name | **`prod`** |
| Deployment | Deployment snapshot mới nhất |
| Tags | `Project=alex`, `Part=3` |

### 11. API Key — `alex-api-key`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-api-key` |
| Tags | `Project=alex`, `Part=3` |

### 12. Usage Plan — `alex-usage-plan`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-usage-plan` |
| Associated Stage | `alex-api` / `prod` |
| Quota Limit | **10,000** requests |
| Quota Period | **MONTH** |
| Throttle Rate | **100** requests/second |
| Throttle Burst | **200** requests |

Usage Plan gắn với API key `alex-api-key` qua resource `aws_api_gateway_usage_plan_key`.

---

## IAM Roles và Policies — tổng hợp

| Resource | Name | Policy |
|----------|------|--------|
| `aws_iam_role` | `alex-ingest-lambda-role` | Trust: `lambda.amazonaws.com` |
| `aws_iam_role_policy` | `alex-ingest-lambda-policy` | Inline: CloudWatch Logs + S3 CRUD + SageMaker InvokeEndpoint + S3 Vectors CRUD |

---

## Environment Variables của Lambda

| Biến | Nguồn | Mô tả |
|------|-------|-------|
| `VECTOR_BUCKET` | `aws_s3_bucket.vectors.id` | Tên bucket lưu vector |
| `SAGEMAKER_ENDPOINT` | `var.sagemaker_endpoint_name` | Tên endpoint embedding từ Part 2 |

---

## Outputs sau khi triển khai

| Output | Giá trị | Sensitive | Mô tả |
|--------|--------|-----------|-------|
| `vector_bucket_name` | `alex-vectors-<account_id>` | No | Tên bucket S3 Vectors |
| `api_endpoint` | `https://<api-id>.execute-api.<region>.amazonaws.com/prod/ingest` | No | URL endpoint ingest |
| `api_key_id` | `<key-id>` | No | ID của API key |
| `api_key_value` | `<key-value>` | **Yes** | Giá trị API key thật |
| `setup_instructions` | (text hướng dẫn) | No | Hướng dẫn copy vào `.env` và test |

---

## Các biến cần điền trong `terraform.tfvars`

Copy từ `terraform.tfvars.example` và điền giá trị thực tế:

| Biến | Mô tả | Ví dụ | Bắt buộc |
|------|-------|-------|----------|
| `aws_region` | AWS region để deploy resource | `"ap-southeast-1"` | Có |
| `sagemaker_endpoint_name` | Tên endpoint embedding từ Part 2 | `"alex-embedding-endpoint"` | Có |

---

## Version Constraints

| Thành phần | Version |
|-----------|---------|
| Terraform CLI | `>= 1.5` |
| AWS Provider (`hashicorp/aws`) | `~> 5.0` |
| Backend | Local (`terraform.tfstate` trong thư mục này) |

---

## Quan hệ với các phần khác của project

```
terraform/2_sagemaker (embedding endpoint)
       │
       │  sagemaker_endpoint_name
       ▼
backend/ingest (code Python: ingest_s3vectors.py, package.py → lambda_function.zip)
       │
       │  lambda_function.zip
       ▼
terraform/3_ingestion (thư mục này — hạ tầng AWS)
       │
       │  api_endpoint, api_key_value
       ▼
terraform/4_researcher (researcher gọi ingest API để lưu kết quả)
       │
       │  ALEX_API_ENDPOINT, ALEX_API_KEY
       ▼
.env (cấu hình local cho các script test)
```

### Phụ thuộc vào

- `terraform/2_sagemaker` — cần tên endpoint embedding (`sagemaker_endpoint_name`)
- `backend/ingest/lambda_function.zip` — phải build trước khi `terraform apply`

### Được dùng bởi

- `terraform/4_researcher` — cần `api_endpoint` và API key để researcher lưu kết quả
- `.env` root project — cần `VECTOR_BUCKET`, `ALEX_API_ENDPOINT`, `ALEX_API_KEY`

---

## Luồng hoạt động end-to-end

### Luồng build & deploy

1. Vào `backend/ingest`, chạy `uv run package.py` để tạo `lambda_function.zip`
2. Vào `terraform/3_ingestion`, copy `terraform.tfvars.example` thành `terraform.tfvars`
3. Điền `aws_region` và `sagemaker_endpoint_name`
4. Chạy `terraform init` → `terraform apply`
5. Copy output vào `.env`

### Luồng request runtime

```
Client (curl/Researcher)
  │  POST /ingest + x-api-key header
  ▼
API Gateway (alex-api / prod)
  │  kiểm tra API key + usage plan
  ▼
Lambda (alex-ingest)
  │  ingest_s3vectors.lambda_handler
  │  → gọi SageMaker InvokeEndpoint (tạo embedding)
  │  → gọi S3 Vectors PutVectors (lưu vector + metadata)
  │  → trả document_id
  ▼
Client nhận response
```

---

## Cách sử dụng nhanh

### Bước 1: Build package

```bash
cd backend/ingest
uv run package.py
```

### Bước 2: Cấu hình Terraform

```bash
cd ../../terraform/3_ingestion
cp terraform.tfvars.example terraform.tfvars
```

Chỉnh `terraform.tfvars`:

```hcl
aws_region              = "ap-southeast-1"
sagemaker_endpoint_name = "alex-embedding-endpoint"
```

### Bước 3: Deploy

```bash
terraform init
terraform apply
```

### Bước 4: Lấy output và lưu vào `.env`

```bash
terraform output
```

Copy vào `.env` ở root project:

```env
VECTOR_BUCKET=<vector_bucket_name>
ALEX_API_ENDPOINT=<api_endpoint>
ALEX_API_KEY=<api_key_value>
```

### Bước 5: Test endpoint

```bash
curl -X POST <ALEX_API_ENDPOINT> \
  -H "x-api-key: <ALEX_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test document", "metadata": {"source": "test"}}'
```

---

## Các file trong thư mục

| File | Vai trò |
|------|--------|
| `main.tf` | Định nghĩa toàn bộ resource AWS (S3, IAM, Lambda, API Gateway, API key, usage plan) |
| `variables.tf` | Khai báo 2 biến đầu vào: `aws_region`, `sagemaker_endpoint_name` |
| `outputs.tf` | Xuất `vector_bucket_name`, `api_endpoint`, `api_key_id`, `api_key_value`, `setup_instructions` |
| `terraform.tfvars.example` | File mẫu để copy thành `terraform.tfvars` |
| `terraform.tfvars` | File cấu hình thật của môi trường bạn *(không commit)* |
| `.terraform.lock.hcl` | Khóa version provider, do Terraform tự sinh |
| `terraform.tfstate` | Local state chính — ghi nhớ resource đã tạo *(không sửa tay)* |

---

## Những điều quan trọng cần nhớ

1. **Đây là local-state Terraform** — state nằm ngay trong thư mục, không dùng remote backend. Giữ file state cẩn thận.
2. **Terraform không tự build code** — phải chạy `uv run package.py` trong `backend/ingest` trước khi `terraform apply`.
3. **API key và Usage Plan rất quan trọng** — nếu bỏ, endpoint public có thể bị spam, chi phí SageMaker/Lambda tăng nhanh.
4. **API Gateway và Lambda là hai lớp khác nhau** — API Gateway là cổng HTTP, Lambda là compute chạy logic Python.

---

## Tóm tắt

`terraform/3_ingestion` tạo ra **hạ tầng ingest pipeline** hoàn chỉnh:

- **1 S3 Bucket** (`alex-vectors-<account_id>`) — versioning, encrypted, private
- **1 IAM Role** (`alex-ingest-lambda-role`) + **1 Inline Policy** — CloudWatch + S3 + SageMaker + S3 Vectors
- **1 Lambda Function** (`alex-ingest`) — python3.12, 512MB, 60s
- **1 CloudWatch Log Group** (`/aws/lambda/alex-ingest`) — retention 7 ngày
- **1 API Gateway REST API** (`alex-api`) — REGIONAL
- **1 Endpoint** (`POST /ingest`) — API key required, AWS_PROXY integration
- **1 API Key** (`alex-api-key`) + **1 Usage Plan** (`alex-usage-plan`) — 10k req/month, 100 rate/200 burst
- **1 Deployment** + **1 Stage** (`prod`)
- **5 Outputs** — bucket name, endpoint URL, key ID, key value (sensitive), hướng dẫn
