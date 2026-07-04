# `terraform/3_ingestion` - Hạ tầng AWS cho Part 3

Thư mục này chứa toàn bộ **Infrastructure as Code** cho **Part 3 - Ingestion Pipeline** của Alex.

Vai trò của thư mục này là biến code trong `backend/ingest` thành một dịch vụ AWS có thể dùng thật.

Cụ thể, thư mục này triển khai:

- Lambda function `alex-ingest`;
- IAM role và IAM policy cho Lambda;
- API Gateway REST API với endpoint `/ingest`;
- API key và usage plan;
- các output cần lưu lại vào `.env`.

Nói ngắn gọn: nếu `backend/ingest` là **application code**, thì `terraform/3_ingestion` là **lớp hạ tầng chạy application code đó trên AWS**.

## Mục tiêu của thư mục này

Sau khi hoàn thành Part 2, bạn đã có:

- một **SageMaker Endpoint** để tạo embedding.

Part 3 cần bổ sung:

1. một backend nhận văn bản đầu vào;
2. một Lambda gọi sang SageMaker;
3. một API Gateway public để client gọi được;
4. một cơ chế xác thực đơn giản bằng API key;
5. một cách xuất thông tin cấu hình ra để dùng tiếp.

Thư mục này giải quyết toàn bộ các yêu cầu đó.

## Các file trong thư mục

### File Terraform chính

#### `main.tf`

Đây là file quan trọng nhất của thư mục.

Nó định nghĩa toàn bộ resource AWS cho Part 3.

Các nhóm resource chính trong file:

- provider AWS;
- data source lấy `account_id`;
- bucket dữ liệu;
- IAM role/policy cho Lambda;
- Lambda function `alex-ingest`;
- CloudWatch log group;
- REST API Gateway;
- resource `/ingest`;
- method `POST`;
- Lambda proxy integration;
- permission cho API Gateway invoke Lambda;
- deployment và stage `prod`;
- API key;
- usage plan;
- usage plan key binding.

Nếu bạn muốn hiểu thư mục này làm gì trên AWS, hãy đọc `main.tf` trước tiên.

### File biến đầu vào

#### `variables.tf`

File này khai báo các input variable mà module cần.

Hiện tại có 2 biến chính:

- `aws_region`
- `sagemaker_endpoint_name`

Ý nghĩa:

- `aws_region` xác định vùng AWS deploy resource;
- `sagemaker_endpoint_name` là tên endpoint embedding từ Part 2 mà Lambda sẽ gọi.

File này **không tạo resource**. Nó chỉ định nghĩa module cần nhận thông tin gì từ bên ngoài.

### File output

#### `outputs.tf`

File này xuất các giá trị quan trọng sau khi `terraform apply`.

Các output đáng chú ý:

- `vector_bucket_name`
- `api_endpoint`
- `api_key_id`
- `api_key_value`
- `setup_instructions`

Vai trò của các output:

- giúp bạn không phải vào console để copy thủ công;
- cho biết chính xác endpoint và API key cần lưu vào `.env`;
- giúp test ngay sau deploy.

### File biến mẫu

#### `terraform.tfvars.example`

Đây là file mẫu để bạn copy thành `terraform.tfvars`.

Mục tiêu:

- cho biết những biến nào bạn cần điền;
- tách cấu hình người dùng ra khỏi logic hạ tầng.

Bạn thường sẽ làm:

```bash
cp terraform.tfvars.example terraform.tfvars
```

rồi chỉnh giá trị thực tế.

### File cấu hình runtime thực tế

#### `terraform.tfvars`

Đây là file bạn tự tạo từ file example.

Nó chứa giá trị thật cho môi trường của bạn, ví dụ:

- region thật đang dùng;
- tên endpoint SageMaker thật.

Không nên commit file này nếu nó chứa dữ liệu nhạy cảm hoặc giá trị đặc thù môi trường.

### File lock provider

#### `.terraform.lock.hcl`

File này do Terraform sinh ra để khóa version provider.

Vai trò:

- giữ môi trường Terraform ổn định;
- tránh thay đổi provider bất ngờ làm lệch kết quả.

Thông thường không sửa tay.

### File state

#### `terraform.tfstate`

Đây là local state của riêng Part 3.

Nhiệm vụ:

- ghi nhớ Terraform đã tạo resource nào;
- lưu id/arn/tham chiếu thực tế;
- cho phép `terraform apply` và `terraform destroy` làm việc đúng.

Đây là file rất quan trọng nhưng không phải file để chỉnh tay.

## Các thành phần AWS mà thư mục này tạo ra

### 1. Bucket dữ liệu

File `main.tf` hiện tạo một bucket tên:

```text
alex-vectors-<account_id>
```

Bucket này được cấu hình thêm:

- versioning;
- server-side encryption AES256;
- block public access.

### 2. Lambda `alex-ingest`

Đây là compute chính của Part 3.

Lambda này:

- chạy runtime `python3.12`;
- dùng file zip từ `backend/ingest/lambda_function.zip`;
- gọi handler `ingest_s3vectors.lambda_handler`;
- được truyền biến môi trường:
  - `VECTOR_BUCKET`
  - `SAGEMAKER_ENDPOINT`

### 3. IAM role và policy

Lambda cần quyền để:

- ghi log vào CloudWatch;
- thao tác dữ liệu bucket;
- gọi `sagemaker:InvokeEndpoint`;
- thao tác `s3vectors:*` cần thiết trên index.

IAM trong Part 3 chính là lớp quyền nối Lambda với các dịch vụ AWS khác.

### 4. API Gateway

API Gateway tạo public endpoint:

```text
/ingest
```

Method:

- `POST`

Kiểu integration:

- `AWS_PROXY`

Điều này có nghĩa:

- toàn bộ request gần như được chuyển nguyên sang Lambda;
- Lambda tự parse `event`.

### 5. API Key và Usage Plan

Đây là lớp bảo vệ quan trọng của endpoint ingest.

API key giúp:

- hạn chế người lạ spam endpoint;
- giảm nguy cơ phát sinh chi phí AWS vô kiểm soát.

Usage plan giúp:

- đặt quota theo tháng;
- đặt throttle theo giây;
- bảo vệ Lambda/SageMaker khỏi quá tải.

## Cách các file trong thư mục liên kết với nhau

### Luồng logic nội bộ

1. `variables.tf` định nghĩa module cần đầu vào gì.
2. `terraform.tfvars` cung cấp giá trị thật cho đầu vào đó.
3. `main.tf` dùng các giá trị này để tạo resource AWS.
4. `outputs.tf` in ra các giá trị cần dùng sau deploy.
5. `.terraform.lock.hcl` giữ provider ổn định.
6. `terraform.tfstate` lưu trạng thái thực tế của deployment.

### Quan hệ với `backend/ingest`

Thư mục này phụ thuộc trực tiếp vào `backend/ingest`.

Cụ thể:

- `main.tf` dùng file:

```text
../../backend/ingest/lambda_function.zip
```

Điều này có nghĩa:

1. bạn phải chạy `uv run package.py` trong `backend/ingest` trước;
2. file zip phải tồn tại;
3. sau đó `terraform apply` mới deploy được Lambda code đúng.

### Quan hệ với `terraform/2_sagemaker`

Part 3 cũng phụ thuộc vào Part 2.

Lý do:

- Lambda ingest phải gọi endpoint embedding đã tạo ở `terraform/2_sagemaker`.

Giá trị kết nối giữa hai part là:

- `sagemaker_endpoint_name`

Thông thường giá trị này là:

```text
alex-embedding-endpoint
```

## Luồng hoạt động end-to-end

### Luồng build và deploy

1. Bạn vào `backend/ingest`.
2. Chạy:

```bash
uv run package.py
```

3. Script tạo `lambda_function.zip`.
4. Bạn vào `terraform/3_ingestion`.
5. Copy file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

6. Chỉnh region và `sagemaker_endpoint_name`.
7. Chạy:

```bash
terraform init
terraform apply
```

8. Terraform tạo resource AWS.
9. `outputs.tf` in ra endpoint và API key info.

### Luồng request runtime

Khi hệ thống đang chạy:

1. Client gọi API Gateway `POST /ingest`.
2. API Gateway kiểm tra `x-api-key`.
3. Nếu hợp lệ, API Gateway invoke Lambda `alex-ingest`.
4. Lambda chạy code trong `ingest_s3vectors.py`.
5. Lambda gọi SageMaker endpoint để tạo embedding.
6. Lambda ghi dữ liệu vector vào S3 Vectors.
7. Lambda trả `document_id`.
8. API Gateway trả response về client.

## Vì sao cần tách thư mục này độc lập

Thiết kế của khóa học dùng **mỗi part một thư mục Terraform độc lập**.

Điều này có lợi vì:

- dễ học từng phần;
- dễ deploy theo từng guide;
- dễ destroy độc lập;
- state file nhỏ và đơn giản hơn;
- ít phụ thuộc chéo hơn trong giai đoạn học tập.

`terraform/3_ingestion` vì thế chỉ quản lý những gì liên quan đến ingest pipeline.

## Những điều quan trọng cần nhớ

### 1. Đây là local-state Terraform

State nằm ngay trong thư mục này, không dùng remote backend.

Điều đó có nghĩa:

- bạn cần giữ file state cẩn thận;
- nếu mất state nhưng resource vẫn còn trên AWS, Terraform có thể "quên" chúng.

### 2. Thư mục này không tự build code

Terraform chỉ deploy file zip có sẵn.

Nó **không** tự chạy `package.py`.

Bạn phải build zip trước.

### 3. API Gateway và Lambda là hai lớp khác nhau

- API Gateway nhận HTTP request từ bên ngoài;
- Lambda chạy logic Python bên trong;
- API Gateway chỉ là lớp cổng vào.

### 4. Usage Plan rất quan trọng

Nếu bỏ API key và usage plan:

- endpoint public có thể bị spam;
- số lần gọi SageMaker tăng;
- chi phí tăng rất nhanh.

## Cách dùng nhanh

### Bước 1: build package ở thư mục code

```bash
cd backend/ingest
uv run package.py
```

### Bước 2: cấu hình Terraform

```bash
cd ../../terraform/3_ingestion
cp terraform.tfvars.example terraform.tfvars
```

### Bước 3: deploy

```bash
terraform init
terraform apply
```

### Bước 4: lấy output

```bash
terraform output
```

### Bước 5: lưu vào `.env`

Thông tin thường cần copy:

- `VECTOR_BUCKET`
- `ALEX_API_ENDPOINT`
- `ALEX_API_KEY`

## Tóm tắt

Thư mục `terraform/3_ingestion` là phần **hạ tầng AWS** cho Part 3.

Nó chịu trách nhiệm:

- tạo Lambda ingest;
- tạo IAM role/policy;
- tạo API Gateway `/ingest`;
- tạo API key và usage plan;
- xuất thông tin để bạn cấu hình local và test tiếp.

Nếu `backend/ingest` là phần **code xử lý**, thì `terraform/3_ingestion` là phần **đưa code đó lên AWS và làm cho nó truy cập được từ bên ngoài**.
