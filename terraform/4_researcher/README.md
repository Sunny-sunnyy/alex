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

Vì vậy khi đọc folder này, hãy coi đây là source of truth cho hạ tầng hiện tại của Researcher.

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

### File override image URI

#### `researcher.auto.tfvars.json`

File này thường được script `backend/researcher/deploy.py` ghi tự động.

Nhiệm vụ:

- truyền `researcher_image_uri` mới nhất vào Terraform;
- giúp Terraform biết image nào cần deploy/update.

Đây là một phần quan trọng trong deploy flow hiện tại.

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

Không có policy này:

- Lambda có thể không lấy được image để khởi chạy function.

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

Điều này giúp knowledge base có thể được làm giàu dần theo thời gian.

## Cách các file trong thư mục liên kết với nhau

### Luồng logic nội bộ

1. `variables.tf` định nghĩa Terraform cần input gì.
2. `terraform.tfvars` và `researcher.auto.tfvars.json` cung cấp giá trị thật.
3. `main.tf` dùng các giá trị đó để tạo resource AWS.
4. `outputs.tf` xuất ra URL, function name, status để người dùng và script dùng tiếp.
5. `terraform.tfstate` lưu trạng thái thực tế của deployment.

### Quan hệ giữa `terraform.tfvars` và `researcher.auto.tfvars.json`

Đây là điểm quan trọng của flow hiện tại.

- `terraform.tfvars` thường do người dùng tự điền:
  - region
  - keys
  - endpoint ingest
  - scheduler flag

- `researcher.auto.tfvars.json` thường do `backend/researcher/deploy.py` tự ghi:
  - `researcher_image_uri`

Vì vậy deploy flow thực tế là:

1. người dùng cấu hình `terraform.tfvars`
2. `deploy.py` build/push image
3. `deploy.py` ghi `researcher.auto.tfvars.json`
4. `terraform apply` dùng cả hai nguồn input

## Luồng hoạt động deploy end-to-end

### Bước 1: Tạo hạ tầng nền

Có thể apply Terraform sớm để tạo:

- ECR repository
- IAM roles

Điều này cho phép bước build/push image có nơi để đẩy image lên.

### Bước 2: Build và push image

`backend/researcher/deploy.py` sẽ:

1. build Docker image từ `backend/researcher/Dockerfile`
2. tag image bằng timestamp
3. push image lên ECR

### Bước 3: Ghi image URI cho Terraform

`deploy.py` ghi:

- `terraform/4_researcher/researcher.auto.tfvars.json`

để truyền image URI vào Terraform.

### Bước 4: Terraform deploy Lambda

Khi `researcher_image_uri` đã có:

- `aws_lambda_function.researcher` được tạo hoặc update
- `aws_lambda_function_url.researcher` được tạo

### Bước 5: Test service

Sau deploy:

- `outputs.tf` cung cấp `researcher_url`
- `backend/researcher/test_research.py` dùng URL này để test

## Luồng hoạt động của service sau khi hạ tầng đã deploy

1. Client gọi Lambda Function URL
2. Request vào container Researcher
3. FastAPI trong `backend/researcher/server.py` xử lý request
4. Agent tạo research note
5. Agent gọi ingest API từ Part 3
6. Ingest pipeline tạo embedding và lưu vào vector store
7. Response trả lại cho client

## Thư mục này liên kết với các phần trước như thế nào?

### Liên kết với `backend/researcher`

Đây là liên kết trực tiếp nhất.

`terraform/4_researcher` không chứa logic research.

Nó chỉ:

- tạo nơi chứa image;
- deploy image đó lên AWS;
- cấp URL và permission để image chạy thành service.

Code được deploy thực sự nằm ở:

- `backend/researcher`

### Liên kết với `backend/ingest`

Researcher phụ thuộc vào ingest pipeline để lưu knowledge.

Terraform Part 4 không deploy ingest, nhưng nó inject:

- `ALEX_API_ENDPOINT`
- `ALEX_API_KEY`

vào runtime của Researcher Lambda.

Hai biến này là cầu nối để code trong `backend/researcher/tools.py` gọi sang Part 3.

### Liên kết với `terraform/3_ingestion`

Part 4 cần output từ Part 3.

Cụ thể:

- ingest endpoint URL
- ingest API key

Nếu Part 3 chưa có hoặc sai cấu hình:

- Researcher Lambda vẫn có thể chạy,
- nhưng bước lưu research vào knowledge base sẽ fail.

### Liên kết với `terraform/2_sagemaker`

Part 4 không gọi SageMaker trực tiếp trong Terraform.

Nhưng chuỗi phụ thuộc thực tế là:

- Researcher -> Ingest API -> Lambda ingest -> SageMaker endpoint

Nghĩa là nếu Part 2 hỏng:

- Part 4 có thể bị ảnh hưởng gián tiếp ở bước ingest.

## Ý nghĩa của các biến quan trọng

### `researcher_image_uri`

Biến quan trọng nhất để quyết định Lambda researcher có được tạo hay không.

Nếu biến này rỗng:

- Terraform chỉ tạo hạ tầng nền
- chưa tạo Lambda researcher thật

### `researcher_model`

Model runtime mà Researcher sẽ dùng.

Trong repo hiện tại, default đang là:

- `openai/gpt-5.4-nano`

### `scheduler_enabled`

Quyết định có bật automated research hay không.

Khuyến nghị:

- để `false` trong lúc debug ban đầu
- chỉ bật khi manual flow đã chạy ổn

## Cách hiểu thư mục này theo vai trò

Nếu tóm tắt ngắn:

- `main.tf` là blueprint hạ tầng
- `variables.tf` là hợp đồng đầu vào
- `outputs.tf` là nơi trả dữ liệu ra ngoài
- `terraform.tfvars.example` là mẫu cấu hình
- `researcher.auto.tfvars.json` là cầu nối giữa `deploy.py` và Terraform

## Tóm tắt

`terraform/4_researcher` là phần **hạ tầng AWS** cho Researcher ở Part 4.

Nó chịu trách nhiệm:

- tạo ECR repository;
- deploy Researcher dưới dạng Lambda container image;
- public service qua Function URL;
- cấp biến môi trường để Researcher gọi ingest pipeline;
- và bật scheduler tự động nếu cần.

Nếu `backend/researcher` là phần **logic ứng dụng**, thì `terraform/4_researcher` là phần **đưa logic đó lên AWS và biến nó thành service dùng thật**.
