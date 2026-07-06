# `terraform/4_researcher` - Hạ tầng AWS cho Researcher trong Part 4

Thư mục này chứa toàn bộ **Infrastructure as Code** cho thành phần **Researcher** của Part 4.

Vai trò của thư mục này là biến code trong `backend/researcher` thành một service AWS có thể dùng thật.

Trong implementation hiện tại của repo, thư mục này triển khai:

- ECR repository cho researcher image;
- Lambda function chạy container image;
- Lambda Function URL public;
- IAM roles và policies;
- scheduler tùy chọn chạy mỗi 2 giờ.

Nói ngắn gọn:

- `backend/researcher` là **application code**
- `terraform/4_researcher` là **lớp hạ tầng AWS** chạy application code đó

## Thành phần này làm gì?

Sau khi hoàn thành Parts 2 và 3, bạn đã có:

- SageMaker endpoint để tạo embedding;
- ingest pipeline để lưu tài liệu vào vector knowledge base.

Part 4 cần bổ sung:

1. một AI service có thể nghiên cứu chủ đề đầu tư;
2. một public URL để gọi service đó;
3. một nơi lưu Docker image;
4. một scheduler tùy chọn để chạy research tự động.

Thư mục này giải quyết toàn bộ các yêu cầu đó.

## Lưu ý rất quan trọng về implementation hiện tại

Guide 4 trong một số đoạn vẫn mô tả:

- App Runner

Nhưng implementation thực tế trong repo hiện tại là:

- **AWS Lambda container image**
- **Lambda Function URL**
- **ECR**

Ngoài ra, runtime thực tế hiện tại còn có các đặc điểm quan trọng:

- model researcher mặc định: `openai/gpt-5.4-nano`
- policy ingest hiện tại là `verified-web-only`
  - chỉ ingest khi có `source_url` sạch
  - fallback note không còn được phép đi vào S3 Vectors

Vì vậy khi đọc folder này, hãy coi đây là source of truth cho hạ tầng hiện tại của Researcher.

## Trạng thái behavior hiện tại của service

Hạ tầng trong folder này đang chạy một version Researcher với behavior đã được siết qua nhieu pass:

- `/research` khong con la best-effort ingest service
- verified-web-only gate: nếu browser khong chung minh duoc noi dung web thật → `500`, khong ingest
- immediate-snapshot constraint: agent phai snapshot ngay sau navigate, khong co hanh dong trung gian
- 3-source limit: Investopedia → AP News → CNN Business, dung sau 3 source neu tat ca fail
- drift detection: `_detect_drifted_snapshot()` phat hien about:blank/about:srcdoc/client-storage
- snapshot URL logging: `snapshot_page_url` trong CloudWatch de truy vet
- `browser_run` status: `article_captured` / `page_drifted` / `ok` / `max_turns` / `error`

Điều này là chủ ý để giữ knowledge base sạch hơn va co evidence ro rang ve browser behavior.

## Các file trong thư mục

### File Terraform chính

#### `main.tf`

Đây là file quan trọng nhất của thư mục.

Nó định nghĩa các resource chính:

- provider AWS;
- data source lấy account hiện tại;
- ECR repository;
- ECR repository policy;
- IAM role cho researcher Lambda;
- policy log cơ bản cho Lambda;
- policy Bedrock access;
- researcher Lambda function;
- Lambda Function URL;
- public invoke permission;
- scheduler role;
- scheduler Lambda;
- EventBridge Scheduler;
- permission để schedule invoke Lambda.

Nếu bạn chỉ đọc một file để hiểu hạ tầng Researcher hoạt động thế nào, hãy đọc `main.tf`.

### File biến đầu vào

#### `variables.tf`

File này khai báo toàn bộ input variable cho Part 4.

Các biến quan trọng:

- `aws_region`
- `openai_api_key`
- `openrouter_api_key`
- `alex_api_endpoint`
- `alex_api_key`
- `scheduler_enabled`
- `researcher_image_uri`
- `bedrock_region`
- `researcher_model`
- `mcp_logging`

Đây là nơi định nghĩa:

- Terraform cần nhận cấu hình gì;
- biến nào nhạy cảm;
- biến nào có default.

### File output

#### `outputs.tf`

File này xuất các giá trị quan trọng sau deploy.

Các output chính:

- `ecr_repository_url`
- `researcher_url`
- `researcher_function_name`
- `scheduler_status`
- `setup_instructions`

Những output này phục vụ cho:

- script deploy;
- test script;
- người dùng cần copy/paste URL hoặc xác nhận trạng thái scheduler.

### File biến mẫu

#### `terraform.tfvars.example`

Đây là file mẫu để tạo `terraform.tfvars`.

Mục tiêu:

- cho người học biết cần điền biến gì;
- tách cấu hình cá nhân khỏi logic hạ tầng.

Thông thường sẽ làm:

```bash
cp terraform.tfvars.example terraform.tfvars
```

rồi điền:

- region;
- OpenAI API key;
- ingest endpoint;
- ingest API key;
- scheduler flag.

### File cấu hình runtime thực tế

#### `terraform.tfvars`

Đây là file cấu hình thật của môi trường hiện tại.

Nó thường chứa:

- region thật;
- API key thật;
- ingest endpoint thật;
- các cờ cấu hình đang dùng.

Không nên commit nội dung nhạy cảm của file này.

#### `researcher.auto.tfvars.json`

File này thường được script `backend/researcher/deploy.py` ghi tự động.

Nhiệm vụ:

- truyền `researcher_image_uri` mới nhất vào Terraform;
- giúp Terraform biết image nào cần deploy/update.

Lưu ý:

- file này được commit trong repo hiện tại để phản ánh image đang chạy thật trên Lambda
- trước khi sửa code mới, nên kiểm tra diff của file này để tránh hiểu nhầm image production đang active

### File lock provider

#### `.terraform.lock.hcl`

File do Terraform sinh ra để khóa version provider.

Vai trò:

- giữ môi trường Terraform ổn định;
- tránh thay đổi provider bất ngờ.

Thông thường không sửa tay.

### File state

#### `terraform.tfstate`

Local state chính của Part 4.

Nhiệm vụ:

- ghi nhớ resource nào đã tạo;
- lưu ID, ARN, URL, dependency thực tế;
- giúp `terraform apply` và `terraform destroy` hoạt động đúng.

#### `terraform.tfstate.backup`

Bản backup của local state.

## Các thành phần AWS mà thư mục này tạo ra

### 1. ECR Repository

Resource:

- `aws_ecr_repository.researcher`

Vai trò:

- lưu Docker image của Researcher;
- là nơi `deploy.py` push image lên trước khi Terraform deploy Lambda.

Tên repository:

- `alex-researcher`

### 2. ECR Repository Policy

Resource:

- `aws_ecr_repository_policy.researcher_lambda_access`

Vai trò:

- cho phép Lambda pull image layers từ ECR.

### 3. IAM Role cho Researcher Lambda

Resource:

- `aws_iam_role.researcher_lambda_role`

Vai trò:

- là danh tính AWS của researcher Lambda.

Nó được gắn thêm:

- policy log cơ bản;
- policy Bedrock access.

### 4. Researcher Lambda Function

Resource:

- `aws_lambda_function.researcher`

Đây là compute chính của Part 4.

Nó:

- dùng `package_type = "Image"`
- chạy image từ ECR
- inject biến môi trường cho runtime
- chạy FastAPI app trong container
- đang chạy một runtime đã được sửa để enforce verified-web-only behavior + immediate-snapshot constraint + drift detection

Lưu ý:

resource này chỉ được tạo khi:

- `researcher_image_uri` không rỗng

Điều đó có nghĩa là Terraform có thể được apply một phần trước để tạo ECR/role, rồi sau đó mới deploy Lambda sau khi image đã được build.

### 5. Lambda Function URL

Resource:

- `aws_lambda_function_url.researcher`

Vai trò:

- tạo public HTTPS URL cho Researcher service.

Đây là URL mà:

- `test_research.py` gọi `/health` và `/research`
- người dùng có thể test trực tiếp bằng `curl`

### 6. Public Invoke Permission

Resource:

- `aws_lambda_permission.allow_public_function_url_invoke`

Vai trò:

- cho phép public access qua Function URL.

### 7. Scheduler Lambda

Resource:

- `aws_lambda_function.scheduler_lambda`

Vai trò:

- gọi Researcher service theo lịch;
- là lớp trung gian giữa EventBridge Scheduler và Researcher URL.

Nó chỉ được tạo khi:

- `scheduler_enabled = true`
- và researcher đã deploy xong.

### 8. EventBridge Scheduler

Resource:

- `aws_scheduler_schedule.research_schedule`

Vai trò:

- chạy automated research theo lịch `rate(2 hours)`.

## Trạng thái deploy gần đây

`uv run deploy.py` hiện đang deploy được lại.

Flow hiện tại:

1. Terraform tạo/refresh ECR + IAM prerequisites
2. `deploy.py` build image mới
3. image được push lên ECR
4. `researcher.auto.tfvars.json` được cập nhật
5. Terraform update Lambda image (neu Terraform crash: fallback `aws lambda update-function-code --image-uri ...`)
6. script chờ Lambda active rồi in Function URL

Các image tag live gần đây đã được dùng trong quá trình verify gồm:

- `deploy-1783267083` — verified-web-only enforcement
- `deploy-1783267341` — anti-fabrication prompt pass
- `deploy-1783267702` — runtime experiment bỏ `--single-process` (inconclusive)
- `deploy-1783329777` — immediate-snapshot strategy + drift detection (active, 2026-07-06)

## Điều đã được chứng minh và chưa được chứng minh

Đã được chứng minh:

- deploy path bằng `uv run deploy.py` hiện hoạt động (thinh thoang Terraform AWS provider crash "Plugin did not respond" — fallback: `aws lambda update-function-code`)
- Function URL, ECR, và Lambda update flow hoạt động
- service có thể fail đúng theo verified-web-only contract (4/5 topic)
- **browser-based `success_verified` đã có bằng chứng reproducible** (NVIDIA AI datacenter demand, Investopedia, 2/2 lan pass 2026-07-06)
- immediate-snapshot strategy giúp capture article content trước khi JavaScript redirects gây drift
- `browser_run` status `article_captured` + `snapshot_page_url` log hoat dong trong CloudWatch

Chưa được chứng minh:

- `success_verified` ổn định trên toan bo 5-topic benchmark (chi 1/5)
- clean article extraction ổn định từ source AP News hoặc CNN Business (chi Investopedia pass)
- browser path ổn định cho cac topic khac ngoai NVIDIA
