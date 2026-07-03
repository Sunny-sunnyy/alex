# Alex - Learning Log And Build README

README này là tài liệu tích lũy theo tiến độ học và triển khai dự án Alex.

Mục tiêu của file này:

- ghi lại chính xác những gì đã làm theo từng ngày;
- giúp ngày sau chỉ cần đọc lại ngữ cảnh cũ rồi viết tiếp vào cuối file;
- tạo một nguồn tổng hợp ngắn gọn hơn `gameplan.md`, nhưng thực dụng hơn cho việc tiếp tục làm lab;
- lưu cả phần kiến trúc, phần thao tác thực tế, phần lỗi đã gặp, và cách xử lý.

## Cách dùng README này cho các ngày tiếp theo

Mỗi ngày mới, trước khi làm tiếp, nên đọc theo thứ tự:

1. `README.md`
2. `gameplan.md`
3. `guides/architecture.md`
4. `guides/agent_architecture.md`
5. nội dung các ngày trước trong chính `README.md`
6. guide hiện tại của ngày đang làm

Quy ước cập nhật:

- Không tách ra nhiều file nhật ký nhỏ.
- Mỗi ngày mới sẽ **append vào cuối README này**.
- Giữ format nhất quán để dễ tra cứu.
- Khi một ngày có thay đổi kỹ thuật quan trọng, phải ghi rõ:
  - đã đọc những file nào;
  - đã tạo/chỉnh những file nào;
  - đã deploy những gì;
  - lỗi nào đã gặp;
  - đã fix ra sao;
  - đầu ra nào cần lưu cho ngày sau.

## Kiến trúc tổng thể cần luôn ghi nhớ

Alex là một SaaS financial planning platform dùng kiến trúc multi-agent trên AWS.

Các thành phần lớn:

- `frontend/`: giao diện NextJS cho người dùng;
- `backend/`: các service, Lambda, và agent code;
- `guides/`: tài liệu hướng dẫn từng bước;
- `terraform/`: hạ tầng chia theo từng phần độc lập;
- `scripts/`: script hỗ trợ chạy local, deploy, destroy.

Luồng lớn của hệ thống:

1. Research content được tạo ra hoặc ingest vào hệ thống.
2. Text được convert thành embeddings bằng SageMaker endpoint.
3. Embeddings được lưu vào S3 Vectors.
4. Researcher và các agent khác dùng knowledge base này để hỗ trợ phân tích.
5. Các agent chuyên biệt phối hợp qua SQS, Lambda và database để tạo ra báo cáo tài chính.

## Những nguyên tắc nền tảng của repo này

### 1. Terraform tách theo thư mục độc lập

Mỗi folder trong `terraform/` là một đơn vị triển khai độc lập:

- có `terraform.tfstate` riêng;
- có `terraform.tfvars` riêng;
- có thể `apply` hoặc `destroy` riêng;
- không có remote state trong cách học này.

Ý nghĩa:

- dễ học theo từng guide;
- dễ cô lập lỗi;
- dễ tiết kiệm chi phí bằng cách destroy từng phần.

### 2. `.env` và `terraform.tfvars` là hai thứ khác nhau

`.env` dùng cho:

- Python scripts;
- backend services;
- local runtime;
- một số bước test.

`terraform.tfvars` dùng cho:

- input variables của Terraform;
- cấu hình hạ tầng của từng folder terraform.

### 3. Chi phí AWS phải được theo dõi thường xuyên

Đặc biệt cần nhớ:

- Aurora về sau là khoản tốn đáng kể;
- SageMaker serverless rẻ hơn many always-on options;
- nên destroy tài nguyên khi tạm dừng học;
- luôn check Billing / Cost Explorer định kỳ.

### 4. Khi debug, không đoán

Thứ tự đúng:

1. đọc exact error;
2. xác định service nào đang fail;
3. xác minh region;
4. xác minh quyền IAM;
5. xác minh config file (`.env`, `terraform.tfvars`, outputs của Terraform);
6. chỉ sửa đúng chỗ gây lỗi.

---

# Day 3 - Foundations: Permissions And SageMaker

## Phạm vi Day 3

Day 3 trong repo này bao gồm:

- `tai_lieu/week3/day3_summary.md`
- `guides/1_permissions.md`
- `guides/2_sagemaker.md`
- `terraform/2_sagemaker`

Đây là ngày đầu tiên thiết lập nền móng hạ tầng cho Alex.

Mục tiêu kỹ thuật của Day 3:

1. hiểu tổng quan dự án Alex;
2. thiết lập quyền AWS tối thiểu nhưng đủ dùng;
3. tạo file `.env` nền tảng;
4. deploy SageMaker Serverless Endpoint để sinh embeddings;
5. chuẩn bị đầu nối cho Day 4, nơi ingest pipeline sẽ dùng endpoint này.

## Những file đã được dùng để lấy ngữ cảnh

Các file nền tảng cần đọc trước hoặc song song trong Day 3:

- `gameplan.md`
- `guides/architecture.md`
- `guides/agent_architecture.md`
- `tai_lieu/week3/day3_summary.md`
- `guides/1_permissions.md`
- `guides/2_sagemaker.md`

Vai trò của từng file:

- `gameplan.md`: briefing tổng thể về course project, troubleshooting strategy, workflow, và những bẫy phổ biến.
- `guides/architecture.md`: sơ đồ kiến trúc tổng thể của toàn hệ thống AWS.
- `guides/agent_architecture.md`: giải thích vai trò và luồng phối hợp giữa các agent.
- `tai_lieu/week3/day3_summary.md`: tóm tắt học thuật và thực hành của Day 3.
- `guides/1_permissions.md`: hướng dẫn IAM và `.env` ban đầu.
- `guides/2_sagemaker.md`: hướng dẫn deploy embedding endpoint bằng Terraform.

## Day 3 - Phần 1: Thiết lập quyền AWS

### Mục tiêu

Thiết lập đúng quyền để tài khoản IAM `aiengineer` có thể làm việc thay vì dùng root user trong thao tác hàng ngày.

### Những gì đã cần làm

1. đăng nhập root user trên AWS Console để làm IAM setup;
2. tạo custom policy `AlexS3VectorsAccess`;
3. tạo group `AlexAccess`;
4. gắn các policy cần thiết vào group;
5. thêm user `aiengineer` vào group;
6. đăng xuất root user;
7. đăng nhập lại bằng IAM user;
8. xác minh AWS CLI đang chạy đúng identity.

### Các policy quan trọng của Day 3

Tối thiểu trong guide:

- `AmazonSageMakerFullAccess`
- `AmazonBedrockFullAccess`
- `CloudWatchEventsFullAccess`
- `AlexS3VectorsAccess`

`AlexS3VectorsAccess` là custom policy vì S3 Vectors là service mới và không có sẵn managed policy phù hợp trong ngữ cảnh bài học.

### Kết quả cần có sau bước permissions

- AWS CLI chạy được với IAM user `aiengineer`;
- `aws sts get-caller-identity` trả về ARN của IAM user đúng;
- `aws sagemaker list-endpoints` chạy được, kể cả khi danh sách còn rỗng;
- có `.env` ở root project.

## Day 3 - Phần 2: Thiết lập `.env` ban đầu

### Mục tiêu

Chuẩn bị cấu hình tối thiểu cho các bước tiếp theo.

### Giá trị quan trọng ban đầu trong `.env`

Tối thiểu cần có:

```env
AWS_ACCOUNT_ID=...
DEFAULT_AWS_REGION=...
```

Ý nghĩa:

- `AWS_ACCOUNT_ID`: dùng để điền vào nhiều chỗ ở các guide sau;
- `DEFAULT_AWS_REGION`: phải nhất quán với các bước deploy, hoặc ít nhất phải hiểu rõ khi nào đang lệch region.

### Ghi chú quan trọng

`.env` không thay thế cho `terraform.tfvars`.

Hai file này phục vụ hai mục đích khác nhau:

- `.env` dành cho code runtime;
- `terraform.tfvars` dành cho input của Terraform.

## Day 3 - Phần 3: Deploy SageMaker Serverless Endpoint

### Mục tiêu

Tạo endpoint tên `alex-embedding-endpoint` để nhận text và trả về embedding vector 384 chiều.

### Lý do chọn SageMaker

Trong Day 3, SageMaker được dùng vì:

- production-ready hơn cách chạy model thủ công;
- hỗ trợ serverless để tiết kiệm chi phí;
- phù hợp với use case embedding endpoint;
- là kỹ năng MLOps thực tế, không chỉ là API call đơn giản.

### Những gì được deploy trong `terraform/2_sagemaker`

Folder `terraform/2_sagemaker` chịu trách nhiệm tạo:

1. IAM role cho SageMaker;
2. SageMaker model declaration;
3. endpoint configuration;
4. SageMaker serverless endpoint;
5. output để lấy endpoint name và ARN.

### Các file quan trọng trong `terraform/2_sagemaker`

#### `main.tf`

Đây là file định nghĩa resource.

Nó tạo:

- `aws_iam_role.sagemaker_role`
- `aws_iam_role_policy_attachment.sagemaker_full_access`
- `aws_sagemaker_model.embedding_model`
- `aws_sagemaker_endpoint_configuration.serverless_config`
- `time_sleep.wait_for_iam_propagation`
- `aws_sagemaker_endpoint.embedding_endpoint`

#### `variables.tf`

File này khai báo các input variables:

- `aws_region`
- `sagemaker_image_uri`
- `embedding_model_name`

#### `outputs.tf`

File này xuất ra:

- `sagemaker_endpoint_name`
- `sagemaker_endpoint_arn`
- `setup_instructions`

#### `terraform.tfvars.example`

File mẫu để copy thành `terraform.tfvars`.

#### `terraform.tfvars`

File cấu hình thật cho máy / account / region đang deploy.

### Cấu hình model của Day 3

Guide này dùng:

- model: `sentence-transformers/all-MiniLM-L6-v2`
- task: `feature-extraction`
- output dimension: `384`
- memory: `3072 MB`
- `max_concurrency = 2`

### Luồng deploy thực tế

1. vào `terraform/2_sagemaker`;
2. copy `terraform.tfvars.example` thành `terraform.tfvars`;
3. set `aws_region`;
4. nếu cần, set cả `sagemaker_image_uri` cho đúng region;
5. chạy `terraform init`;
6. chạy `terraform apply`;
7. lưu output endpoint;
8. cập nhật `.env` với:

```env
SAGEMAKER_ENDPOINT=alex-embedding-endpoint
```

## Lỗi thực tế đã gặp trong Day 3

### Lỗi

Khi chạy `terraform apply`, lỗi xuất hiện là:

`Cross region ECR image pulls are not allowed`

Error chi tiết cho biết:

- SageMaker đang kỳ vọng region `ap-southeast-1`;
- nhưng `sagemaker_image_uri` lại trỏ tới ECR image ở region khác.

### Root cause

Root cause không nằm ở IAM, không nằm ở Terraform init, và cũng không nằm ở model name.

Root cause là:

- SageMaker model dùng container image trên Amazon ECR;
- ECR image đó phải ở **cùng region** với nơi SageMaker đang deploy;
- nếu `aws_region = "ap-southeast-1"` mà image URI lại là `...ecr.us-east-1.amazonaws.com/...` thì SageMaker từ chối.

### Cách fix đã xác định

Phải override `sagemaker_image_uri` đúng region.

Ví dụ cho `ap-southeast-1`:

```hcl
aws_region = "ap-southeast-1"
sagemaker_image_uri = "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
```

### Bài học rút ra

Trong guide này, có một bẫy rất dễ dính:

- `aws_region` đúng chưa đủ;
- còn phải kiểm tra `sagemaker_image_uri` có cùng region hay không.

Khi debug SageMaker create model, luôn kiểm tra cả hai giá trị này cùng lúc.

## Những cải tiến tài liệu đã làm trong Day 3

Trong quá trình làm Day 3, phần tài liệu trong `terraform/2_sagemaker` đã được làm rõ hơn để dễ học và dễ debug:

- thêm comment tiếng Việt có dấu trong các file Terraform;
- giải thích chức năng từng file;
- giải thích từng resource, variable, output;
- tạo thêm file `terraform/2_sagemaker/README_vi.md` để mô tả tổng thể folder này.

### Mục đích của phần tài liệu bổ sung này

- để lần sau nhìn vào `2_sagemaker` là hiểu ngay nó đang làm gì;
- giảm nhầm lẫn giữa model name và container image;
- giúp nhận diện nhanh lỗi region;
- tạo nền tảng để tiếp tục Day 4 dễ hơn.

## Kết quả cần đạt sau Day 3

Nếu Day 3 hoàn thành đúng, trạng thái mong muốn là:

1. đã hiểu cấu trúc tổng thể của Alex;
2. IAM user `aiengineer` có đủ quyền cho các bước đầu;
3. `.env` đã được tạo và có giá trị nền tảng;
4. SageMaker endpoint đã được deploy hoặc ít nhất đã xác định đúng config deploy;
5. đã hiểu và ghi lại cách xử lý lỗi region ECR;
6. đã có tài liệu nội bộ để tiếp tục các ngày sau.

## Các lệnh cốt lõi của Day 3

### Kiểm tra identity hiện tại

```bash
aws sts get-caller-identity
```

### Kiểm tra SageMaker permissions cơ bản

```bash
aws sagemaker list-endpoints
```

### Khởi tạo Terraform cho `2_sagemaker`

```bash
cd terraform/2_sagemaker
terraform init
```

### Deploy SageMaker endpoint

```bash
terraform apply
```

### Kiểm tra endpoint sau deploy

```bash
aws sagemaker describe-endpoint \
  --endpoint-name alex-embedding-endpoint \
  --region ap-southeast-1
```

### Test invoke endpoint

```bash
cd ../../backend
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name alex-embedding-endpoint \
  --content-type application/json \
  --body fileb://vectorize_me.json \
  --output json /dev/stdout \
  --region ap-southeast-1
```

## Những điểm phải nhớ trước khi sang Day 4

1. `terraform/2_sagemaker` là một thư mục Terraform độc lập.
2. `terraform.tfstate` của folder này là local state riêng.
3. Endpoint tạo ra ở Day 3 sẽ được dùng ở Day 4.
4. Region mismatch giữa SageMaker và ECR image là lỗi phổ biến nhất ở guide này.
5. Nếu AWS CLI default region khác region deploy, phải thêm `--region` khi test endpoint.
6. `SAGEMAKER_ENDPOINT` phải được lưu vào `.env`.

## Handoff sang Day 4

Day 4 nhiều khả năng sẽ cần đọc lại các thông tin sau từ Day 3:

- endpoint name của SageMaker;
- region thực tế đang deploy;
- `.env` hiện tại;
- cách repo dùng `terraform.tfvars`;
- nguyên tắc Terraform độc lập theo từng folder;
- bài học về việc luôn kiểm tra region trước khi debug sâu.

Khi bắt đầu Day 4, nên xác minh lại:

1. `SAGEMAKER_ENDPOINT` đã có trong `.env` chưa;
2. endpoint có tồn tại trong AWS Console / CLI chưa;
3. đang đứng đúng region chưa;
4. `terraform/2_sagemaker` có state ổn định chưa.

---

# Template Append Cho Ngày Sau

Mỗi ngày mới nên append theo form này:

```md
# Day X - Tên ngày / chủ đề

## Phạm vi Day X
- các guide đã đọc
- các thư mục terraform/backend đã dùng

## Mục tiêu
- ...

## Những gì đã làm
1. ...
2. ...

## Hạ tầng / code / config đã tạo hoặc đã sửa
- ...

## Giá trị output quan trọng cần lưu cho ngày sau
- ...

## Lỗi đã gặp
### Lỗi 1
- triệu chứng:
- root cause:
- cách fix:

## Lệnh quan trọng
```bash
...
```

## Trạng thái kết thúc ngày
- ...

## Handoff sang ngày tiếp theo
- ...
```

---

# Change Log

## Day 3

- Đã tổng hợp nội dung từ:
  - `tai_lieu/week3/day3_summary.md`
  - `guides/1_permissions.md`
  - `guides/2_sagemaker.md`
  - `terraform/2_sagemaker`
- Đã ghi lại lỗi region ECR và cách fix.
- Đã chuẩn hóa hướng dùng README như một file tích lũy cho toàn bộ các ngày sau.
