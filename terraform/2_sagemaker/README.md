# `terraform/2_sagemaker` - Hạ tầng SageMaker Embedding cho Part 2

Thư mục này chứa toàn bộ **Infrastructure as Code** cho **Part 2 - SageMaker Serverless Deployment** của dự án Alex.

Vai trò của thư mục này là tạo ra một **SageMaker Serverless Endpoint** có thể:

- nhận văn bản đầu vào;
- tải model embedding từ Hugging Face;
- sinh ra vector embedding 384 chiều;
- phục vụ cho các bước semantic search / RAG ở các phần sau.

Nói ngắn gọn: nếu Part 3 cần một nơi để biến `text -> vector`, thì `terraform/2_sagemaker` chính là phần hạ tầng tạo ra "nhà máy vector" đó.

## Mục tiêu của thư mục này

Sau Guide 1, bạn đã có:

- AWS account;
- IAM permissions;
- CLI và Terraform sẵn sàng.

Guide 2 cần tạo ra:

1. một IAM role để SageMaker được phép chạy model;
2. một SageMaker model sử dụng Hugging Face inference container;
3. một endpoint configuration theo kiểu serverless;
4. một endpoint thực tế để backend hoặc CLI có thể gọi.

Thư mục này thực hiện toàn bộ các bước đó.

## Thư mục này tạo gì trên AWS?

Khi chạy `terraform apply`, thư mục này sẽ tạo các thành phần chính sau:

### 1. IAM Role cho SageMaker

SageMaker không thể tự chạy trong tài khoản AWS của bạn nếu không có role phù hợp.

Role này cho phép dịch vụ:

- assume role;
- dùng quyền cần thiết để tạo và chạy model.

### 2. SageMaker Model

Đây là phần khai báo model inference.

Nó không chứa model file ngay trong repo.
Thay vào đó, nó mô tả cho SageMaker biết:

- dùng container nào;
- khi container khởi động thì tải model nào từ Hugging Face;
- task inference là gì.

### 3. SageMaker Endpoint Configuration

Đây là cấu hình cách endpoint sẽ chạy.

Trong project này, endpoint được cấu hình:

- theo kiểu **serverless**;
- có `memory_size_in_mb = 3072`;
- có `max_concurrency = 2`.

### 4. SageMaker Endpoint

Đây là endpoint thực tế mà các thành phần khác sẽ gọi.

Sau khi deploy xong, endpoint này thường có tên:

```text
alex-embedding-endpoint
```

Chính endpoint này sẽ được:

- CLI test ở Guide 2 gọi trực tiếp;
- `backend/ingest` trong Guide 3 gọi để tạo embedding;
- lưu tên vào `.env` dưới biến `SAGEMAKER_ENDPOINT`.

### 5. `time_sleep` workaround

Đây không phải tài nguyên nghiệp vụ.

Nó chỉ là một resource hỗ trợ nhằm giải quyết vấn đề:

- IAM role vừa tạo xong;
- policy vừa attach xong;
- nhưng SageMaker gọi quá sớm nên AWS chưa kịp propagate quyền.

## Các file trong thư mục

### File Terraform chính

#### `main.tf`

Đây là file quan trọng nhất của thư mục.

File này định nghĩa:

- provider AWS;
- IAM role cho SageMaker;
- policy attachment;
- SageMaker model;
- endpoint configuration;
- `time_sleep`;
- endpoint thực tế.

Nếu bạn chỉ đọc một file để hiểu thư mục này làm gì, hãy đọc `main.tf`.

### File biến đầu vào

#### `variables.tf`

File này khai báo các input variables mà module cần.

Các biến chính:

- `aws_region`
- `sagemaker_image_uri`
- `embedding_model_name`

Ý nghĩa:

- `aws_region`: region deploy resource;
- `sagemaker_image_uri`: URI của Hugging Face inference container trên ECR;
- `embedding_model_name`: model embedding cụ thể trên Hugging Face Hub.

File này không deploy gì cả.
Nó chỉ định nghĩa module cần nhận thông tin gì từ bên ngoài.

### File output

#### `outputs.tf`

File này in ra các giá trị quan trọng sau khi deploy xong.

Các output chính:

- `sagemaker_endpoint_name`
- `sagemaker_endpoint_arn`
- `setup_instructions`

Vai trò của outputs:

- giúp bạn biết chính xác endpoint tên gì;
- cho phép copy nhanh vào `.env`;
- giúp kiểm tra deployment mà không cần mở console.

### File biến mẫu

#### `terraform.tfvars.example`

Đây là file mẫu để bạn copy thành `terraform.tfvars`.

Mục tiêu:

- cho biết các biến nào cần điền;
- tách cấu hình người dùng ra khỏi logic hạ tầng.

Thông thường bạn sẽ làm:

```bash
cp terraform.tfvars.example terraform.tfvars
```

rồi chỉnh:

- region;
- nếu cần thì chỉnh `sagemaker_image_uri`.

### File cấu hình runtime thực tế

#### `terraform.tfvars`

Đây là file cấu hình thật của riêng môi trường bạn.

Ví dụ nó có thể chứa:

```hcl
aws_region = "ap-southeast-1"
sagemaker_image_uri = "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
```

Không nên commit file này nếu nó chứa giá trị đặc thù môi trường của bạn.

### File lock provider

#### `.terraform.lock.hcl`

File này do Terraform tạo ra để khóa version provider.

Vai trò:

- giữ môi trường Terraform ổn định;
- tránh thay đổi provider bất ngờ;
- giúp các lần `terraform init` sau ít khác biệt hơn.

Thông thường không sửa tay file này.

### File state

#### `terraform.tfstate`

Đây là local state chính của riêng Part 2.

Nhiệm vụ:

- ghi nhớ Terraform đã tạo resource nào;
- lưu id, arn, và tham chiếu thực tế;
- cho phép `terraform apply` và `terraform destroy` hoạt động đúng.

Đây là file rất quan trọng nhưng không phải file để chỉnh tay.

#### `terraform.tfstate.backup`

Đây là bản backup của state.

Vai trò:

- hỗ trợ khôi phục nếu state chính bị hỏng hoặc cần tham chiếu lại.

Bạn cũng không nên sửa tay file này.

## Cách các file trong thư mục liên kết với nhau

### Luồng logic nội bộ

1. `variables.tf` định nghĩa module cần đầu vào gì.
2. `terraform.tfvars` cung cấp giá trị thật cho các biến đó.
3. `main.tf` dùng các giá trị này để tạo resource AWS.
4. `outputs.tf` xuất ra các thông tin cần dùng sau deploy.
5. `.terraform.lock.hcl` giữ version provider ổn định.
6. `terraform.tfstate` lưu trạng thái thực tế của deployment.

### Quan hệ với các phần khác của project

Thư mục này là nền tảng cho các phần sau, đặc biệt là:

- `backend/ingest`
- `terraform/3_ingestion`

Cụ thể:

- Guide 3 cần tên endpoint embedding từ thư mục này;
- Lambda ingest ở Part 3 sẽ gọi endpoint tạo ở đây;
- `.env` của root project sẽ cần:

```env
SAGEMAKER_ENDPOINT=alex-embedding-endpoint
```

Nói cách khác:

- `terraform/2_sagemaker` tạo ra **embedding service**;
- `backend/ingest` là code gọi embedding service đó;
- `terraform/3_ingestion` là hạ tầng deploy code ingest thành Lambda/API.

## Giải thích dễ hiểu: model và container khác nhau thế nào?

Đây là chỗ rất nhiều người học hay nhầm.

### `embedding_model_name`

Đây là **model** trên Hugging Face Hub.

Trong project này, giá trị mặc định là:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Model này quyết định:

- semantic space;
- chất lượng embedding;
- số chiều embedding.

Ở đây model trả về vector **384 chiều**.

### `sagemaker_image_uri`

Đây **không phải model**.

Đây là **container image** trên Amazon ECR.

Container này biết cách:

- nhận request JSON;
- tải model từ Hugging Face;
- chạy inference;
- trả về kết quả.

Hiểu đơn giản:

- `sagemaker_image_uri` là **bộ máy chạy model**;
- `embedding_model_name` là **model thật được nạp vào bộ máy đó**.

## Luồng hoạt động end-to-end

### Luồng build/deploy

1. Bạn vào `terraform/2_sagemaker`.
2. Copy file mẫu:

```bash
cp terraform.tfvars.example terraform.tfvars
```

3. Điền `aws_region`.
4. Nếu cần, điền `sagemaker_image_uri` đúng region.
5. Chạy:

```bash
terraform init
terraform apply
```

6. Terraform tạo IAM role.
7. Terraform attach policy cho role.
8. Terraform tạo SageMaker model.
9. Terraform tạo endpoint configuration.
10. Terraform chờ IAM propagate qua `time_sleep`.
11. Terraform tạo endpoint thực tế.
12. `outputs.tf` in ra tên endpoint và ARN.

### Luồng runtime sau khi deploy

Khi endpoint đã `InService`:

1. Client hoặc backend gửi request JSON tới endpoint.
2. Container Hugging Face nhận request.
3. Container tải hoặc dùng model `all-MiniLM-L6-v2`.
4. Container chạy feature extraction.
5. SageMaker trả embedding về cho bên gọi.

Ở Guide 2, bên gọi có thể là AWS CLI.
Ở Guide 3, bên gọi sẽ là Lambda ingest.

## Vì sao chọn SageMaker Serverless?

Project này dùng **SageMaker Serverless Endpoint** thay vì endpoint always-on vì:

- phù hợp môi trường học tập;
- không cần quản lý instance luôn chạy;
- chi phí thấp hơn khi ít traffic;
- đủ tốt cho bài toán embedding của project.

### Lợi ích

- scale-to-zero;
- trả tiền theo request;
- dễ triển khai;
- sát thực tế production hơn việc tự host model thủ công.

### Trade-off

- cold start có thể chậm;
- thời gian tạo endpoint lâu hơn một số service nhẹ khác;
- lần invoke đầu tiên thường chậm hơn các lần sau.

## Vì sao lỗi region hay xảy ra ở folder này?

Đây là một trong những lỗi phổ biến nhất ở Part 2.

Lỗi điển hình:

```text
Cross region ECR image pulls are not allowed
```

Ý nghĩa:

- SageMaker đang được tạo ở một region;
- nhưng `sagemaker_image_uri` lại trỏ đến ECR ở region khác.

Ví dụ lỗi:

- `aws_region = "ap-southeast-1"`
- nhưng image lại là ECR ở `us-east-1`

SageMaker không cho phép kiểu pull image cross-region như vậy trong context này.

### Quy tắc phải nhớ

- `aws_region` là region nào;
- `sagemaker_image_uri` cũng phải là ECR image ở đúng region đó.

Ví dụ đúng:

```hcl
aws_region = "ap-southeast-1"
sagemaker_image_uri = "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
```

## Vì sao cần `time_sleep`?

AWS IAM có độ trễ propagate.

Có những lúc:

1. Terraform vừa tạo role;
2. Terraform vừa attach policy;
3. SageMaker lập tức dùng role đó;
4. AWS trả lỗi rằng role chưa hợp lệ hoặc chưa assume được.

Lỗi này không nhất thiết vì policy sai.
Nó có thể chỉ vì AWS chưa kịp đồng bộ quyền.

`time_sleep` giúp:

- chờ một khoảng nhỏ;
- giảm lỗi ngẫu nhiên khi tạo endpoint quá sớm.

## Những điều quan trọng cần nhớ

### 1. Folder này không chứa code model custom

Bạn không tự đóng gói model artifact ở repo này.
Thay vào đó:

- SageMaker dùng Hugging Face container;
- container tự tải model từ Hugging Face Hub.

Điều này làm Guide 2 đơn giản hơn rất nhiều.

### 2. Đây là local-state Terraform

State của Part 2 nằm ngay trong thư mục này.

Điều đó có nghĩa:

- đây là state độc lập với Part 3;
- bạn có thể destroy Part 2 riêng;
- nếu mất state nhưng resource vẫn còn trên AWS, Terraform có thể "quên" resource.

### 3. Endpoint name là đầu ra quan trọng nhất

Thứ bạn gần như chắc chắn sẽ dùng tiếp là:

- `sagemaker_endpoint_name`

Giá trị này sẽ được copy vào `.env` hoặc vào `terraform/3_ingestion`.

### 4. Endpoint serverless tạo khá lâu là bình thường

SageMaker serverless endpoint không phải resource tạo tức thời.

Bạn nên chờ vài phút thay vì nghĩ Terraform bị treo quá sớm.

## Cách dùng nhanh

### Bước 1: tạo file biến thật

```bash
cd terraform/2_sagemaker
cp terraform.tfvars.example terraform.tfvars
```

### Bước 2: chỉnh region

Ví dụ:

```hcl
aws_region = "us-east-1"
```

Nếu dùng region khác, hãy chắc rằng `sagemaker_image_uri` cũng cùng region.

### Bước 3: khởi tạo Terraform

```bash
terraform init
```

### Bước 4: xem plan

```bash
terraform plan
```

### Bước 5: deploy

```bash
terraform apply
```

### Bước 6: xem output

```bash
terraform output
```

### Bước 7: kiểm tra endpoint

```bash
aws sagemaker describe-endpoint --endpoint-name alex-embedding-endpoint
```

### Bước 8: test invoke

```bash
cd ../../backend
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name alex-embedding-endpoint \
  --content-type application/json \
  --body fileb://vectorize_me.json \
  --output json /dev/stdout
```

## Nếu có lỗi thì nên kiểm tra gì trước?

### Trường hợp 1: lỗi region ECR

Kiểm tra:

- `aws_region`
- `sagemaker_image_uri`

Hai giá trị này phải cùng region.

### Trường hợp 2: lỗi role invalid / cannot be assumed

Kiểm tra:

- role đã attach policy chưa;
- có `time_sleep` hay không;
- thử apply lại sau một lúc.

### Trường hợp 3: endpoint tạo lâu

Đây thường là bình thường với serverless endpoint.

### Trường hợp 4: invoke không thấy endpoint

Thường là do:

- AWS CLI đang dùng region mặc định khác với region deploy.

Khi đó, thêm `--region your-region` vào lệnh test.

## Tóm tắt

Thư mục `terraform/2_sagemaker` là phần **hạ tầng embedding** cho Alex.

Nó chịu trách nhiệm:

- tạo IAM role cho SageMaker;
- cấu hình model Hugging Face;
- tạo serverless endpoint;
- xuất tên endpoint để các phần sau dùng tiếp.

Nếu `terraform/3_ingestion` là phần dựng **Lambda ingest**, thì `terraform/2_sagemaker` là phần dựng **dịch vụ tạo embedding** mà Lambda ingest phụ thuộc trực tiếp.
