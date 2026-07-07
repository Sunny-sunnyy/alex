# `terraform/4_researcher` — Hạ tầng AWS cho Researcher trong Part 4

Thư mục này chứa toàn bộ **Infrastructure as Code** cho thành phần **Researcher** của Part 4.

Vai trò: biến code trong `backend/researcher` thành một AI service chạy trên AWS — nhận chủ đề nghiên cứu, dùng LLM + trình duyệt để thu thập thông tin web đã xác minh, và lưu kết quả vào S3 Vectors qua ingest API của Part 3.

---

## Lưu ý quan trọng về implementation hiện tại

Guide 4 trong một số đoạn vẫn mô tả **App Runner + Bedrock (Nova Pro)**. Tuy nhiên, implementation thực tế trong repo hiện tại là:

| Mô tả cũ (guide) | Thực tế hiện tại |
|-----------------|-----------------|
| App Runner | **AWS Lambda container image** |
| AWS Bedrock (Nova Pro) | **OpenAI API (`openai/gpt-5.4-nano`)** qua LiteLLM |
| App Runner URL | **Lambda Function URL** (public HTTPS) |
| Scheduler 2 giờ | **Scheduler 12 giờ** (`rate(12 hours)`) |

Hãy coi file này và `main.tf` là source of truth cho hạ tầng hiện tại của Researcher.

---

## Mục tiêu

Sau Part 3 (Ingestion Pipeline), Part 4 cần bổ sung:

1. Một AI service có thể nghiên cứu chủ đề đầu tư qua web browser
2. Một public URL để gọi service đó (`/health`, `/research`)
3. Một nơi lưu Docker image (ECR)
4. Một scheduler tùy chọn để chạy research tự động

---

## Sơ đồ tài nguyên AWS được tạo

```
ECR Repository (alex-researcher)
  │  MUTABLE tags, force_delete=true
  └─ ECR Repository Policy (Lambda ECR access)

IAM Role (alex-researcher-lambda-role)
  ├─ Policy Attachment: AWSLambdaBasicExecutionRole
  └─ Inline Policy: alex-researcher-lambda-bedrock-policy
       └─ bedrock:InvokeModel, InvokeModelWithResponseStream, ListFoundationModels

Lambda Function (alex-researcher)           [chỉ tạo khi researcher_image_uri != ""]
  │  package_type: Image
  │  timeout: 300s, memory: 2048MB, ephemeral_storage: 2048MB
  │  arch: x86_64
  │  env: OPENAI_API_KEY, OPENROUTER_API_KEY, ALEX_API_ENDPOINT,
  │       ALEX_API_KEY, BEDROCK_REGION, RESEARCHER_MODEL, MCP_LOGGING
  │
  ├─ Lambda Function URL (public, NONE auth)
  └─ Lambda Permission (public invoke)

── [Scheduler - chỉ tạo khi scheduler_enabled && researcher_deployed] ──

IAM Role (alex-scheduler-lambda-role)
  └─ Policy Attachment: AWSLambdaBasicExecutionRole

Lambda Function (alex-researcher-scheduler)
  │  runtime: python3.12, memory: 256MB, timeout: 180s
  │  handler: lambda_function.handler
  │  code: ../../backend/scheduler/lambda_function.zip
  │  env: APP_RUNNER_URL = <researcher function URL>

IAM Role (alex-eventbridge-scheduler-role)
  └─ Inline Policy: InvokeLambdaPolicy → scheduler Lambda

EventBridge Scheduler (alex-research-schedule)
  │  schedule: rate(12 hours)
  │  flexible_time_window: OFF

Lambda Permission (AllowExecutionFromEventBridge)
```

---

## Điều kiện kích hoạt (locals)

| Local | Công thức | Ý nghĩa |
|-------|----------|---------|
| `researcher_deployed` | `var.researcher_image_uri != ""` | Researcher Lambda chỉ được tạo khi đã có image URI |
| `scheduler_active` | `var.scheduler_enabled && local.researcher_deployed` | Scheduler chỉ được tạo khi cả 2 điều kiện đều đúng |

Điều này cho phép Terraform được apply một phần trước (tạo ECR + IAM role) rồi deploy Lambda sau khi image đã build và push.

---

## Chi tiết từng tài nguyên AWS

### 1. ECR Repository — `alex-researcher`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | **`alex-researcher`** |
| Image Tag Mutability | **MUTABLE** |
| Force Delete | **true** |
| Scan On Push | **false** |
| Tags | `Project=alex`, `Part=4` |

### 2. ECR Repository Policy — Lambda Access

| Thuộc tính | Giá trị |
|-----------|---------|
| Principal | `lambda.amazonaws.com` |
| Actions | `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer` |
| Condition | `ArnLike.aws:sourceArn` = Lambda functions trong account |

Cho phép Lambda pull image layers từ ECR.

### 3. IAM Role — `alex-researcher-lambda-role`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-researcher-lambda-role` |
| Trust Policy | Cho phép `lambda.amazonaws.com` assume role (`sts:AssumeRole`) |
| Tags | `Project=alex`, `Part=4` |

**Policies gắn vào role này:**

#### a) `AWSLambdaBasicExecutionRole` (managed)

Policy managed của AWS, cấp quyền ghi log CloudWatch cơ bản.

#### b) `alex-researcher-lambda-bedrock-policy` (inline)

| Action | Resource |
|--------|----------|
| `bedrock:InvokeModel` | `*` |
| `bedrock:InvokeModelWithResponseStream` | `*` |
| `bedrock:ListFoundationModels` | `*` |

Policy này giữ quyền Bedrock cho runtime cũ hoặc khi cần debug AWS model access.

### 4. Lambda Function — `alex-researcher`

| Thuộc tính | Giá trị |
|-----------|---------|
| Function Name | **`alex-researcher`** |
| Package Type | **Image** (container) |
| Image URI | Từ `var.researcher_image_uri` |
| IAM Role | `alex-researcher-lambda-role` |
| Timeout | **300 giây** (5 phút) |
| Memory | **2048 MB** |
| Architecture | **x86_64** |
| Ephemeral Storage | **2048 MB** |
| Tags | `Project=alex`, `Part=4` |

| Condition | Chỉ tạo khi `researcher_image_uri != ""` |

**Environment Variables của Researcher Lambda:**

| Biến | Nguồn | Mô tả |
|------|-------|-------|
| `OPENAI_API_KEY` | `var.openai_api_key` | API key cho model OpenAI (GPT) |
| `OPENROUTER_API_KEY` | `var.openrouter_api_key` | API key cho OpenRouter (dùng model thay thế) |
| `ALEX_API_ENDPOINT` | `var.alex_api_endpoint` | URL endpoint ingest từ Part 3 |
| `ALEX_API_KEY` | `var.alex_api_key` | API key ingest từ Part 3 |
| `BEDROCK_REGION` | `var.bedrock_region` | Region cho Bedrock inference (mặc định: `ap-southeast-1`) |
| `RESEARCHER_MODEL` | `var.researcher_model` | Model identifier (mặc định: `openai/gpt-5.4-nano`) |
| `MCP_LOGGING` | `var.mcp_logging` | Bật/tắt logging MCP Playwright (mặc định: `"False"`) |

### 5. Lambda Function URL

| Thuộc tính | Giá trị |
|-----------|---------|
| Function | `alex-researcher` |
| Authorization Type | **NONE** (public) |

Đây là URL HTTPS công khai dùng để gọi `/health` và `/research`.

### 6. Lambda Permission — Public Invoke

| Thuộc tính | Giá trị |
|-----------|---------|
| Statement ID | `AllowPublicFunctionInvokeViaUrl` |
| Action | `lambda:InvokeFunction` |
| Principal | `*` |
| Invoked Via Function URL | `true` |

---

### 7-12. Scheduler Resources (chỉ tạo khi `scheduler_active = true`)

#### 7. IAM Role — `alex-scheduler-lambda-role`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-scheduler-lambda-role` |
| Trust Policy | `lambda.amazonaws.com` |
| Policy Attached | `AWSLambdaBasicExecutionRole` |
| Tags | `Project=alex`, `Part=4` |

#### 8. Lambda Function — `alex-researcher-scheduler`

| Thuộc tính | Giá trị |
|-----------|---------|
| Function Name | **`alex-researcher-scheduler`** |
| Runtime | **python3.12** |
| Handler | `lambda_function.handler` |
| Memory | **256 MB** |
| Timeout | **180 giây** |
| Code Source | `../../backend/scheduler/lambda_function.zip` |
| Tags | `Project=alex`, `Part=4` |

| Environment Variable | Giá trị |
|---------------------|--------|
| `APP_RUNNER_URL` | Researcher Function URL (đã strip trailing `/`) |

Scheduler Lambda là lớp trung gian gọi Researcher theo lịch, cần thiết vì research có thể chạy lâu hơn timeout của một số integration trực tiếp.

#### 9. IAM Role — `alex-eventbridge-scheduler-role`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | `alex-eventbridge-scheduler-role` |
| Trust Policy | `scheduler.amazonaws.com` |
| Tags | `Project=alex`, `Part=4` |

#### 10. Inline Policy — `InvokeLambdaPolicy` (gắn vào eventbridge role)

| Action | Resource |
|--------|----------|
| `lambda:InvokeFunction` | ARN của `alex-researcher-scheduler` |

#### 11. EventBridge Scheduler — `alex-research-schedule`

| Thuộc tính | Giá trị |
|-----------|---------|
| Name | **`alex-research-schedule`** |
| Schedule Expression | **`rate(12 hours)`** |
| Flexible Time Window | **OFF** |
| Target ARN | `alex-researcher-scheduler` Lambda |
| Target Role | `alex-eventbridge-scheduler-role` |

#### 12. Lambda Permission — `AllowExecutionFromEventBridge`

| Thuộc tính | Giá trị |
|-----------|---------|
| Statement ID | `AllowExecutionFromEventBridge` |
| Action | `lambda:InvokeFunction` |
| Principal | `scheduler.amazonaws.com` |
| Source ARN | `alex-research-schedule` |

---

## IAM Roles và Policies — tổng hợp

| Resource | Name | Type | Policies |
|----------|------|------|----------|
| `aws_iam_role` | `alex-researcher-lambda-role` | Lambda execution | `AWSLambdaBasicExecutionRole` (managed) + `alex-researcher-lambda-bedrock-policy` (inline) |
| `aws_iam_role` | `alex-scheduler-lambda-role` | Lambda execution | `AWSLambdaBasicExecutionRole` (managed) |
| `aws_iam_role` | `alex-eventbridge-scheduler-role` | Scheduler execution | `InvokeLambdaPolicy` (inline) |

---

## Environment Variables tổng hợp

### Researcher Lambda (`alex-researcher`)

| Biến | Nguồn | Mặc định |
|------|-------|----------|
| `OPENAI_API_KEY` | `var.openai_api_key` | *(bắt buộc)* |
| `OPENROUTER_API_KEY` | `var.openrouter_api_key` | *(bắt buộc)* |
| `ALEX_API_ENDPOINT` | `var.alex_api_endpoint` | *(bắt buộc)* |
| `ALEX_API_KEY` | `var.alex_api_key` | *(bắt buộc)* |
| `BEDROCK_REGION` | `var.bedrock_region` | `"ap-southeast-1"` |
| `RESEARCHER_MODEL` | `var.researcher_model` | `"openai/gpt-5.4-nano"` |
| `MCP_LOGGING` | `var.mcp_logging` | `"False"` |

### Scheduler Lambda (`alex-researcher-scheduler`)

| Biến | Nguồn | Mô tả |
|------|-------|-------|
| `APP_RUNNER_URL` | `trimsuffix(function_url, "/")` | Researcher Function URL (để gọi `/research`) |

---

## Outputs sau khi triển khai

| Output | Giá trị | Mô tả |
|--------|--------|-------|
| `ecr_repository_url` | `<account>.dkr.ecr.<region>.amazonaws.com/alex-researcher` | ECR repository URL |
| `researcher_url` | `https://<lambda-id>.lambda-url.<region>.on.aws/` | Public HTTPS URL của researcher |
| `researcher_function_name` | `alex-researcher` | Tên Lambda function |
| `scheduler_status` | `"Enabled - Running every 12 hours"` / `"Disabled"` / `"Disabled - deploy the researcher image first"` | Trạng thái scheduler |
| `setup_instructions` | (text hướng dẫn) | Hướng dẫn test `/health` và trạng thái scheduler |

---

## Các biến cần điền trong `terraform.tfvars`

Copy từ `terraform.tfvars.example` và điền giá trị thực tế:

| Biến | Mô tả | Mặc định | Sensitive |
|------|-------|----------|-----------|
| `aws_region` | AWS region để deploy resource | *(bắt buộc)* | No |
| `openai_api_key` | OpenAI API key cho researcher agent | *(bắt buộc)* | **Yes** |
| `openrouter_api_key` | OpenRouter API key | *(bắt buộc)* | **Yes** |
| `alex_api_endpoint` | URL endpoint ingest từ Part 3 | *(bắt buộc)* | No |
| `alex_api_key` | API key ingest từ Part 3 | *(bắt buộc)* | **Yes** |
| `scheduler_enabled` | Bật/tắt automated research | `false` | No |
| `researcher_image_uri` | Full ECR image URI (để trống nếu chưa build) | `""` | No |
| `bedrock_region` | Region cho Bedrock inference | `"ap-southeast-1"` | No |
| `researcher_model` | Model identifier cho researcher | `"openai/gpt-5.4-nano"` | No |
| `mcp_logging` | Bật/tắt MCP Playwright logging (`"True"` / `"False"`) | `"False"` | No |

### File `researcher.auto.tfvars.json`

File này được script `backend/researcher/deploy.py` tự động ghi sau khi build và push image. Ví dụ nội dung hiện tại:

```json
{
  "researcher_image_uri": "487592470523.dkr.ecr.ap-southeast-1.amazonaws.com/alex-researcher:deploy-1783346445"
}
```

Lưu ý: file này được commit trong repo để phản ánh image đang chạy thật. Trước khi sửa code, nên kiểm tra diff của file này.

---

## Version Constraints

| Thành phần | Version |
|-----------|---------|
| Terraform CLI | `>= 1.5` |
| AWS Provider (`hashicorp/aws`) | `>= 6.28.0` |
| Backend | Local (`terraform.tfstate` trong thư mục này) |

---

## Quan hệ với các phần khác của project

```
terraform/3_ingestion (ingest API + API key)
       │
       │  ALEX_API_ENDPOINT, ALEX_API_KEY
       ▼
backend/researcher (code Python: server.py, context.py, tools.py, mcp_servers.py)
       │
       │  Dockerfile → ECR image
       ▼
terraform/4_researcher (thư mục này — hạ tầng AWS)
       │
       │  researcher_url (Function URL)
       ▼
Người dùng / Scheduler
       │
       │  gọi /health, /research
       ▼
Researcher → gọi ingest API → S3 Vectors (knowledge base)
```

### Phụ thuộc vào

- `terraform/3_ingestion` — cần `api_endpoint` và `api_key_value` để researcher lưu kết quả
- `backend/researcher` — Docker image phải được build và push lên ECR trước khi deploy Lambda
- `backend/scheduler/lambda_function.zip` — phải tồn tại nếu bật scheduler

### Được dùng bởi

- `terraform/6_agents` — Planner agent sẽ query S3 Vectors (nơi researcher lưu kết quả)
- Người dùng — gọi trực tiếp `/research` để test
- EventBridge Scheduler — tự động gọi research mỗi 12 giờ

---

## Behavior runtime hiện tại của Researcher

Hạ tầng này đang chạy một phiên bản Researcher với behavior đã được siết qua nhiều pass:

### Verified-Web-Only Contract

`/research` trả về **200** chỉ khi:
- Agent thu được nội dung từ trang bài viết thực
- Ghi chú cuối cùng có dòng `Source URL: https://...` sạch sẽ
- `ingest_financial_document()` ghi nhận ingest thành công
- Nội dung không phải fallback/kiến thức chung

`/research` trả về **500** khi:
- Không thu được nội dung web đã xác minh
- Trang không khả dụng, bị chặn, hoặc đã thay đổi
- Agent không thể ghi nhận source URL sạch sẽ
- Ghi chú trông giống kiến thức dự phòng
- Ingest từ chối tài liệu

### Immediate-Snapshot Strategy

1. Khám phá URL bài viết thực qua kết quả tìm kiếm/điều hướng
2. Điều hướng đến URL bài viết
3. Gọi ngay `browser_snapshot` (không click, scroll, type)
4. Nếu trang là `about:blank`, `about:srcdoc`, client-storage, ad-tech → chuyển nguồn
5. Thử tối đa 3 loại nguồn: Investopedia → AP News → CNN Business
6. Dừng nếu cả 3 thất bại

### Browser Phase Statuses

| Status | Ý nghĩa |
|--------|---------|
| `article_captured` | Response có source URL sạch, browser phase hoàn thành |
| `page_drifted` | Response chứa drift markers (`about:blank`, `about:srcdoc`, `client-storage`, `optimizely`, `doubleclick`, `googlesyndication`) |
| `ok` | Browser phase hoàn thành nhưng không chứng minh được article capture |
| `max_turns` | OpenAI Agents SDK đạt giới hạn lượt |
| `error` | Ngoại lệ không mong đợi |

### Request Outcomes

| Outcome | Ý nghĩa |
|---------|---------|
| `success_verified` | Nội dung web đã xác minh đã được ingest |
| `failed_browser` | Browser hoặc cổng xác minh thất bại |
| `failed_ingest` | Công cụ ingest trả về thất bại |
| `failed_unknown` | Không thể phân loại |

---

## Trạng thái đã chứng minh và chưa chứng minh

### Đã chứng minh

- Deploy path bằng `uv run deploy.py` hoạt động
- Function URL, ECR, Lambda update flow hoạt động
- Service fail đúng theo verified-web-only contract (4/5 topic)
- **Browser-based `success_verified` đã có bằng chứng reproducible**: NVIDIA AI datacenter demand, Investopedia, 2/2 lần pass (2026-07-06)
- Immediate-snapshot strategy giúp capture article content trước khi JavaScript redirects
- `browser_run` status `article_captured` + `snapshot_page_url` log hoạt động trong CloudWatch

### Chưa chứng minh

- `success_verified` ổn định trên toàn bộ 5-topic benchmark (chỉ 1/5)
- Clean article extraction ổn định từ AP News hoặc CNN Business (chỉ Investopedia pass)
- Browser path ổn định cho các topic khác ngoài NVIDIA

---

## Cách sử dụng nhanh

### Bước 1: Cấu hình Terraform

```bash
cd terraform/4_researcher
cp terraform.tfvars.example terraform.tfvars
```

Chỉnh `terraform.tfvars`:

```hcl
aws_region        = "ap-southeast-1"
openai_api_key    = "<your-openai-key>"
openrouter_api_key = "<your-openrouter-key>"
alex_api_endpoint = "<ingest-endpoint-from-part-3>"
alex_api_key      = "<ingest-api-key-from-part-3>"
scheduler_enabled = false
bedrock_region    = "ap-southeast-1"
researcher_model  = "openai/gpt-5.4-nano"
```

### Bước 2: Tạo ECR + IAM role (chưa có Lambda)

```bash
terraform init
terraform apply
```

(Lúc này `researcher_image_uri` còn rỗng nên Lambda chưa được tạo.)

### Bước 3: Build, push và deploy toàn bộ

```bash
cd ../../backend/researcher
uv run deploy.py
```

Script này sẽ:
1. Build Docker image
2. Push lên ECR
3. Ghi `researcher.auto.tfvars.json`
4. Chạy `terraform apply` để tạo/update Lambda
5. In ra Function URL

### Bước 4: Kiểm tra health

```bash
curl <researcher_url>/health
```

### Bước 5: Test research

```bash
uv run test_research.py "NVIDIA AI datacenter demand"
```

### Bước 6: Kiểm tra log

```bash
aws logs tail /aws/lambda/alex-researcher --since 15m --region ap-southeast-1
```

Lọc log benchmark:

```bash
aws logs tail /aws/lambda/alex-researcher --since 15m --region ap-southeast-1 | rg "research_run|research_ingest|snapshot_page_url"
```

---

## Các file trong thư mục

| File | Vai trò |
|------|--------|
| `main.tf` | Định nghĩa toàn bộ resource AWS (ECR, Lambda, Function URL, IAM, Scheduler, EventBridge) |
| `variables.tf` | Khai báo 9 biến đầu vào (region, keys, endpoint, model, scheduler flag, etc.) |
| `outputs.tf` | Xuất `ecr_repository_url`, `researcher_url`, `researcher_function_name`, `scheduler_status`, `setup_instructions` |
| `terraform.tfvars.example` | File mẫu để copy thành `terraform.tfvars` |
| `terraform.tfvars` | File cấu hình thật của môi trường bạn *(không commit)* |
| `researcher.auto.tfvars.json` | File tự động ghi bởi `deploy.py`, chứa image URI hiện tại *(có commit)* |
| `.terraform.lock.hcl` | Khóa version provider, do Terraform tự sinh |
| `terraform.tfstate` | Local state chính — ghi nhớ resource đã tạo *(không sửa tay)* |
| `terraform.tfstate.backup` | Backup của state |

---

## Các file code backend tương ứng

| File trong `backend/researcher/` | Vai trò |
|----------------------------------|--------|
| `server.py` | FastAPI app, model setup, agent run orchestration, verified-web gate, phase logs |
| `context.py` | Agent instructions, source preference, immediate-snapshot rule |
| `tools.py` | Ingest tool, source URL validation, degraded-content rejection, ingest telemetry |
| `mcp_servers.py` | Playwright MCP setup và Chromium/container args |
| `test_research.py` | Deployed end-to-end test script và terminal summary |
| `deploy.py` | Docker build, ECR push, Terraform apply, Lambda deployment |
| `Dockerfile` | Lambda container image với Playwright MCP, Chromium, uv, FastAPI, Lambda Web Adapter |
| `pyproject.toml` | uv project dependencies |

---

## Deploy flow chi tiết

```
1. terraform apply (khởi tạo)
   └─ Tạo ECR repo + IAM roles
   └─ Lambda CHƯA được tạo (researcher_image_uri = "")

2. uv run deploy.py (trong backend/researcher)
   ├─ docker build -t alex-researcher:deploy-<timestamp> .
   ├─ docker tag + push lên ECR
   ├─ Ghi researcher.auto.tfvars.json với image URI mới
   ├─ terraform apply (cập nhật Lambda image)
   └─ In Function URL

3. Nếu Terraform crash ("Plugin did not respond"):
   └─ Fallback: aws lambda update-function-code --image-uri <uri>
```

---

## Lưu ý quan trọng

1. **Đây là local-state Terraform** — state nằm ngay trong thư mục, không dùng remote backend.
2. **Terraform không tự build Docker image** — phải dùng `uv run deploy.py` trong `backend/researcher`.
3. **Docker phải đang chạy** để build và push image.
4. **Lambda chỉ được tạo khi có `researcher_image_uri`** — nếu image URI rỗng, Terraform chỉ tạo ECR + role.
5. **Schedule interval hiện tại là 12 giờ** (`rate(12 hours)`), không phải 2 giờ như mô tả trong một số tài liệu cũ.
6. **`researcher.auto.tfvars.json` được commit** — phản ánh image production đang active.
7. **Không in secret values** từ `.env`, `terraform.tfvars`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `ALEX_API_KEY`.
8. **Repo có thể chứa local dirty Terraform changes** — không ghi đè trừ khi được yêu cầu rõ ràng.

---

## An toàn Secrets

Không in hoặc tóm tắt giá trị từ:
- `.env`
- `terraform.tfvars`
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `ALEX_API_KEY`

Có thể xác minh an toàn các trường không nhạy cảm:

```bash
aws lambda get-function-configuration \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Environment.Variables.RESEARCHER_MODEL' \
  --output text
```

Tránh dump toàn bộ biến môi trường Lambda vì có thể làm lộ khóa.

---

## Tóm tắt

`terraform/4_researcher` tạo ra **hạ tầng AI Research Agent** hoàn chỉnh:

**Luôn được tạo:**
- **1 ECR Repository** (`alex-researcher`) — MUTABLE tags, force delete, có policy cho Lambda access
- **1 IAM Role** (`alex-researcher-lambda-role`) — `AWSLambdaBasicExecutionRole` + Bedrock inline policy

**Tạo khi có image URI (`researcher_image_uri != ""`):**
- **1 Lambda Function** (`alex-researcher`) — container image, 300s timeout, 2048MB memory, 2048MB ephemeral storage
- **1 Function URL** — public HTTPS, NONE auth
- **1 Lambda Permission** — public invoke qua Function URL

**Tạo khi scheduler được bật (`scheduler_enabled && researcher_deployed`):**
- **1 IAM Role** (`alex-scheduler-lambda-role`) — `AWSLambdaBasicExecutionRole`
- **1 Lambda Function** (`alex-researcher-scheduler`) — python3.12, 256MB, 180s
- **1 IAM Role** (`alex-eventbridge-scheduler-role`) — cho phép scheduler invoke Lambda
- **1 EventBridge Scheduler** (`alex-research-schedule`) — `rate(12 hours)`
- **1 Lambda Permission** — cho phép EventBridge invoke scheduler Lambda

**Cấu hình runtime:**
- Model mặc định: `openai/gpt-5.4-nano`
- Behavior: verified-web-only, immediate-snapshot, 3-source limit, drift detection
- 7 biến môi trường cho researcher Lambda, 1 biến cho scheduler Lambda
- 5 outputs
- 9 biến đầu vào (4 sensitive)
