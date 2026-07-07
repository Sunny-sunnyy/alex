# `terraform/2_sagemaker` — Hạ tầng SageMaker Embedding cho Part 2

Thư mục này chứa toàn bộ **Infrastructure as Code** cho **Part 2 - SageMaker Serverless Deployment** của dự án Alex.

Vai trò: tạo một **SageMaker Serverless Endpoint** nhận văn bản đầu vào, tải model embedding từ Hugging Face và sinh ra vector embedding 384 chiều, phục vụ semantic search / RAG ở các phần sau.

---

## Mục tiêu

Sau Guide 1 (Permissions), Guide 2 cần tạo ra:

1. IAM role cho SageMaker
2. SageMaker model sử dụng Hugging Face inference container
3. Endpoint configuration kiểu serverless
4. Endpoint thực tế để backend/CLI gọi

---

## Sơ đồ tài nguyên AWS được tạo

```
IAM Role (alex-sagemaker-role)
  └─ Policy Attachment (AmazonSageMakerFullAccess)
       │
       ▼
SageMaker Model (alex-embedding-model)
  │  image: HuggingFace inference container
  │  env:   HF_MODEL_ID, HF_TASK
  │
  ▼
Endpoint Configuration (alex-embedding-serverless-config)
  │  serverless: memory=3072MB, max_concurrency=2
  │
  ▼
time_sleep (15s) — chờ IAM propagate
  │
  ▼
SageMaker Endpoint (alex-embedding-endpoint)
  └─ InService → có thể gọi từ backend/CLI
```

---

## Chi tiết từng tài nguyên AWS

### 1. IAM Role — `alex-sagemaker-role`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-sagemaker-role` |
| Trust Policy | Cho phép `sagemaker.amazonaws.com` assume role (Action: `sts:AssumeRole`) |
| Policy Attached | `arn:aws:iam::aws:policy/AmazonSageMakerFullAccess` |

Đây là danh tính AWS của SageMaker. Nếu không có role hợp lệ, bước tạo model hoặc endpoint sẽ thất bại.

### 2. SageMaker Model — `alex-embedding-model`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-embedding-model` |
| Execution Role | `alex-sagemaker-role` |
| Container Image | `763104351884.dkr.ecr.<region>.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04` |
| `HF_MODEL_ID` | `sentence-transformers/all-MiniLM-L6-v2` |
| `HF_TASK` | `feature-extraction` |
| Depends On | `aws_iam_role_policy_attachment.sagemaker_full_access` |

**Quan trọng:** `image` URI phải cùng region với `aws_region`. Nếu khác region, SageMaker báo lỗi: `Cross region ECR image pulls are not allowed`.

### 3. Endpoint Configuration — `alex-embedding-serverless-config`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-embedding-serverless-config` |
| Model | `alex-embedding-model` |
| Serverless Memory | **3072 MB** |
| Max Concurrency | **2** |

Memory 3072 MB giúp container có đủ RAM/CPU để khởi động và inference ổn định. Max concurrency đặt thấp để tránh vượt quota tài khoản học viên.

### 4. time_sleep — `wait_for_iam_propagation`

| Thuộc tính | Giá trị |
|-----------|---------|
| Duration | **15 giây** |
| Depends On | `aws_iam_role_policy_attachment.sagemaker_full_access` |

Workaround cho vấn đề IAM propagation. AWS IAM cần vài giây để đồng bộ quyền sau khi tạo/gắn policy. Nếu tạo endpoint quá sớm, SageMaker có thể báo role chưa hợp lệ.

### 5. SageMaker Endpoint — `alex-embedding-endpoint`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | **`alex-embedding-endpoint`** |
| Endpoint Config | `alex-embedding-serverless-config` |
| Depends On | `time_sleep.wait_for_iam_propagation` |

Đây là endpoint thực tế. Sau khi trạng thái là `InService`, bạn có thể dùng AWS CLI hoặc code backend để gửi text và nhận embedding.

---

## IAM Roles và Policies — tổng hợp

| Resource | Name | Policy |
|----------|------|--------|
| `aws_iam_role` | `alex-sagemaker-role` | Trust: `sagemaker.amazonaws.com` |
| `aws_iam_role_policy_attachment` | — | `AmazonSageMakerFullAccess` (managed) |

---

## Environment Variables của SageMaker Model

Đây là biến môi trường được inject vào container inference, không phải biến của Lambda:

| Biến | Giá trị | Mô tả |
|------|--------|-------|
| `HF_MODEL_ID` | `sentence-transformers/all-MiniLM-L6-v2` | Model embedding sẽ được tải từ Hugging Face Hub |
| `HF_TASK` | `feature-extraction` | Loại tác vụ — trả về vector embedding |

---

## Outputs sau khi triển khai

| Output | Giá trị | Mô tả |
|--------|--------|-------|
| `sagemaker_endpoint_name` | `alex-embedding-endpoint` | Tên endpoint — copy vào `.env` cho Part 3 |
| `sagemaker_endpoint_arn` | `arn:aws:sagemaker:<region>:<account>:endpoint/alex-embedding-endpoint` | ARN đầy đủ, dùng khi debug/audit |
| `setup_instructions` | (text hướng dẫn) | Nhắc các bước tiếp theo sau deploy |

---

## Các biến cần điền trong `terraform.tfvars`

Copy từ `terraform.tfvars.example` và điền giá trị thực tế:

| Biến | Mô tả | Ví dụ | Default |
|------|-------|-------|---------|
| `aws_region` | AWS region để deploy resource | `"ap-southeast-1"` | *(bắt buộc)* |
| `sagemaker_image_uri` | URI HuggingFace inference container trên ECR | `"763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"` | *(có default theo ap-southeast-1)* |
| `embedding_model_name` | Tên model trên Hugging Face Hub | `"sentence-transformers/all-MiniLM-L6-v2"` | `"sentence-transformers/all-MiniLM-L6-v2"` |

### Quy tắc quan trọng

- `aws_region` là region nào thì `sagemaker_image_uri` cũng phải là ECR image ở đúng region đó.
- Ví dụ nếu dùng `us-east-1`:
  ```hcl
  aws_region          = "us-east-1"
  sagemaker_image_uri = "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
  ```

---

## Version Constraints

| Thành phần | Version |
|-----------|---------|
| Terraform CLI | `>= 1.5` |
| AWS Provider (`hashicorp/aws`) | `~> 5.70` |
| Backend | Local (`terraform.tfstate` trong thư mục này) |

---

## Quan hệ với các phần khác của project

```
terraform/2_sagemaker (tạo embedding service)
       │
       │  endpoint name: alex-embedding-endpoint
       ▼
terraform/3_ingestion (Lambda ingest gọi endpoint này)
       │
       │  biến sagemaker_endpoint_name
       ▼
backend/ingest (code Python gọi SageMaker để tạo embedding)
```

- **Guide 3** cần tên endpoint từ thư mục này để điền vào biến `sagemaker_endpoint_name`.
- **`.env`** root project sẽ cần: `SAGEMAKER_ENDPOINT=alex-embedding-endpoint`

---

## Model và Container — phân biệt quan trọng

| Khái niệm | Giá trị | Vai trò |
|-----------|--------|---------|
| `embedding_model_name` | `sentence-transformers/all-MiniLM-L6-v2` | **Model** trên Hugging Face Hub — quyết định chất lượng embedding, số chiều (384) |
| `sagemaker_image_uri` | ECR HuggingFace container | **Container** — bộ máy chạy model, biết cách tải model từ Hub và chạy inference |

---

## Cách sử dụng nhanh

### Bước 1: Tạo file biến thật

```bash
cd terraform/2_sagemaker
cp terraform.tfvars.example terraform.tfvars
```

### Bước 2: Chỉnh region trong `terraform.tfvars`

```hcl
aws_region = "ap-southeast-1"
```

### Bước 3: Khởi tạo và deploy

```bash
terraform init
terraform plan
terraform apply
```

### Bước 4: Xem output

```bash
terraform output
```

### Bước 5: Kiểm tra endpoint

```bash
aws sagemaker describe-endpoint --endpoint-name alex-embedding-endpoint
```

### Bước 6: Test invoke embedding

```bash
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name alex-embedding-endpoint \
  --content-type application/json \
  --body fileb://vectorize_me.json \
  --output json /dev/stdout
```

---

## Các file trong thư mục

| File | Vai trò |
|------|--------|
| `main.tf` | Định nghĩa toàn bộ resource AWS (role, model, endpoint config, endpoint, time_sleep) |
| `variables.tf` | Khai báo 3 biến đầu vào: `aws_region`, `sagemaker_image_uri`, `embedding_model_name` |
| `outputs.tf` | Xuất `sagemaker_endpoint_name`, `sagemaker_endpoint_arn`, `setup_instructions` |
| `terraform.tfvars.example` | File mẫu để copy thành `terraform.tfvars` |
| `terraform.tfvars` | File cấu hình thật của môi trường bạn *(không commit)* |
| `.terraform.lock.hcl` | Khóa version provider, do Terraform tự sinh |
| `terraform.tfstate` | Local state chính — ghi nhớ resource đã tạo *(không sửa tay)* |
| `terraform.tfstate.backup` | Backup của state |

---

## Xử lý lỗi thường gặp

### Lỗi 1: Cross region ECR image

**Kiểm tra:** `aws_region` và `sagemaker_image_uri` phải cùng region.

### Lỗi 2: Role invalid / cannot be assumed

**Kiểm tra:** Role đã attach policy chưa? Có `time_sleep` không? Thử apply lại sau một lúc.

### Lỗi 3: Endpoint tạo lâu

Đây là bình thường với serverless endpoint. Có thể mất vài phút.

### Lỗi 4: Invoke không thấy endpoint

Thường do AWS CLI đang dùng region mặc định khác với region deploy. Thêm `--region <your-region>` vào lệnh test.

---

## Tóm tắt

`terraform/2_sagemaker` tạo ra **dịch vụ embedding** nền tảng cho toàn bộ project Alex:

- **1 IAM Role** (`alex-sagemaker-role`) + **1 Managed Policy** (`AmazonSageMakerFullAccess`)
- **1 SageMaker Model** (`alex-embedding-model`) chạy container HuggingFace, tự tải `all-MiniLM-L6-v2`
- **1 Endpoint Configuration** (`alex-embedding-serverless-config`) — serverless, 3072MB, max 2 concurrent
- **1 Endpoint** (`alex-embedding-endpoint`) — endpoint thực tế, tên này được dùng xuyên suốt Part 3
- **1 time_sleep** (15s) — workaround IAM propagation
- **3 Outputs** — endpoint name, ARN, hướng dẫn

Vector đầu ra: **384 chiều**. Model: **sentence-transformers/all-MiniLM-L6-v2**. Chi phí: serverless scale-to-zero, trả tiền theo request.
