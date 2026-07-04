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

# Day 4 - Ingestion Pipeline With S3 Vectors

## Phạm vi Day 4

Day 4 trong repo này bao gồm:

- `tai_lieu/week3/day4_summary.md`
- `guides/3_ingest.md`
- `backend/ingest`
- `terraform/3_ingestion`

Đây là ngày xây dựng đường ống nạp dữ liệu vector đầu tiên cho Alex.

Mục tiêu kỹ thuật của Day 4:

1. tạo lớp ingest để biến `text -> embedding -> stored vector`;
2. đóng gói code Python thành `lambda_function.zip` để deploy Lambda;
3. triển khai API Gateway + Lambda + IAM cho endpoint `/ingest`;
4. lưu lại các giá trị output vào `.env`;
5. kiểm tra semantic ingest/search end-to-end bằng các script local.

## Những file đã được dùng để lấy ngữ cảnh

Các file nền tảng cần đọc trước hoặc song song trong Day 4:

- `README.md`
- `gameplan.md`
- `guides/architecture.md`
- `guides/agent_architecture.md`
- `guides/1_permissions.md`
- `guides/2_sagemaker.md`
- `guides/3_ingest.md`
- `tai_lieu/week3/day4_summary.md`
- `backend/ingest/README.md`
- `backend/ingest/ingest_s3vectors.py`
- `backend/ingest/search_s3vectors.py`
- `backend/ingest/test_ingest_s3vectors.py`
- `backend/ingest/test_search_s3vectors.py`
- `backend/ingest/cleanup_s3vectors.py`
- `backend/ingest/package.py`
- `backend/ingest/pyproject.toml`
- `terraform/3_ingestion/README.md`
- `terraform/3_ingestion/main.tf`
- `terraform/3_ingestion/variables.tf`
- `terraform/3_ingestion/outputs.tf`
- `terraform/3_ingestion/terraform.tfvars.example`

Vai trò của từng nhóm file:

- `guides/3_ingest.md`: hướng dẫn học viên tạo bucket/index vector, package Lambda, deploy Terraform, và test ingest/search.
- `tai_lieu/week3/day4_summary.md`: tóm tắt lý thuyết Day 4, luồng RAG ingest, semantic search, và phần test end-to-end.
- `backend/ingest/*`: phần application code cho ingest, search, cleanup, packaging, và local verification.
- `terraform/3_ingestion/*`: phần hạ tầng AWS để đưa code ingest lên Lambda và public hóa qua API Gateway.

## Day 4 - Phần 1: Kiến trúc ingest pipeline

### Mục tiêu

Thiết lập mắt xích trung gian để mọi nghiên cứu hoặc tài liệu tài chính có thể được nạp vào knowledge base vector của Alex.

### Luồng lớn cần nắm

1. client hoặc service khác gửi `text`;
2. Lambda ingest gọi SageMaker endpoint từ Day 3;
3. SageMaker trả embedding 384 chiều;
4. vector cùng metadata được ghi vào index `financial-research`;
5. về sau researcher hoặc các agent khác sẽ truy xuất lại bằng semantic search.

### Điểm phải nhớ

Part 3 là chỗ nối giữa:

- **Part 2**: dịch vụ embedding;
- **storage layer**: vector bucket / index;
- **future agents**: nơi sẽ khai thác knowledge base về sau.

## Day 4 - Phần 2: `backend/ingest`

### Mục tiêu

Có một codebase Python nhỏ, độc lập, có thể:

1. nhận văn bản đầu vào;
2. gọi SageMaker để lấy embedding;
3. ghi trực tiếp vào S3 Vectors;
4. hỗ trợ search local;
5. package thành artifact deploy cho Lambda.

### Những file chính trong `backend/ingest`

- `ingest_s3vectors.py`
  - Lambda handler chính.
  - Parse `event.body`, lấy `text`, gọi `get_embedding(text)`, rồi `put_vectors`.
- `search_s3vectors.py`
  - Search handler theo kiểu Lambda-style.
  - Vector hóa query text rồi gọi `query_vectors`.
- `test_ingest_s3vectors.py`
  - Test local trực tiếp bằng SDK.
  - Nạp 3 tài liệu mẫu: Tesla, Amazon, NVIDIA.
- `test_search_s3vectors.py`
  - Liệt kê dữ liệu hiện có và chạy semantic search mẫu.
- `cleanup_s3vectors.py`
  - Xóa dữ liệu test khỏi index để reset bài thực hành.
- `package.py`
  - Lấy dependencies từ `.venv`, copy source cần thiết, và build `lambda_function.zip`.
- `pyproject.toml`
  - Khai báo uv project độc lập cho thư mục này.

### Logic chính của `ingest_s3vectors.py`

Luồng xử lý:

1. đọc `VECTOR_BUCKET`, `SAGEMAKER_ENDPOINT`, `INDEX_NAME`;
2. gọi `sagemaker-runtime invoke_endpoint` với payload `{"inputs": text}`;
3. bóc response lồng kiểu `[[[embedding]]]` về mảng 1 chiều;
4. sinh `uuid4` làm `document_id`;
5. gọi `s3vectors.put_vectors(...)`;
6. trả JSON response thành công hoặc lỗi.

### Điểm kỹ thuật quan trọng

- embedding model của Day 3 trả vector **384 chiều**;
- index Day 4 phải cấu hình đúng `dimension = 384`;
- code đang xử lý đặc biệt response nested array từ Hugging Face container;
- local test và production Lambda dùng cùng logic embedding cốt lõi.

### Dependencies đáng chú ý

`backend/ingest/pyproject.toml` hiện có:

- `boto3`
- `python-dotenv`
- `requests`
- `requests-aws4auth`
- `opensearch-py`
- `tenacity`

Trong đó:

- `boto3` và `python-dotenv` là phần dùng trực tiếp cho flow hiện tại;
- `opensearch-py` và `requests-aws4auth` có dấu hiệu là dư âm từ implementation vector storage cũ hơn.

## Day 4 - Phần 3: Packaging Lambda

### Mục tiêu

Tạo artifact `lambda_function.zip` để Terraform có thể deploy code ingest lên AWS Lambda.

### Cách `package.py` hoạt động

1. tìm `site-packages` trong `.venv`;
2. copy dependencies vào `build/package`;
3. copy `ingest_s3vectors.py` và `search_s3vectors.py`;
4. zip toàn bộ thành `lambda_function.zip`;
5. xóa thư mục build tạm.

### Ý nghĩa thực tế

Terraform ở `terraform/3_ingestion` **không tự build code**.

Nó chỉ deploy file zip đã tồn tại tại:

```text
../../backend/ingest/lambda_function.zip
```

Nên quy trình đúng là:

1. vào `backend/ingest`;
2. chạy `uv run package.py`;
3. xác nhận zip đã được tạo;
4. mới sang `terraform/3_ingestion` để `terraform apply`.

## Day 4 - Phần 4: `terraform/3_ingestion`

### Mục tiêu

Deploy hạ tầng cho ingest pipeline:

1. IAM role/policy cho Lambda;
2. Lambda `alex-ingest`;
3. CloudWatch Log Group;
4. API Gateway REST API;
5. endpoint `POST /ingest`;
6. API key + usage plan để bảo vệ endpoint public.

### Các file quan trọng

#### `main.tf`

Định nghĩa:

- provider AWS;
- data source `aws_caller_identity`;
- bucket `alex-vectors-${account_id}`;
- IAM role/policy cho Lambda;
- `aws_lambda_function.ingest`;
- log group `/aws/lambda/alex-ingest`;
- REST API `alex-api`;
- resource `/ingest`;
- method `POST`;
- Lambda proxy integration;
- Lambda permission cho API Gateway;
- deployment + stage `prod`;
- API key;
- usage plan;
- usage plan key binding.

#### `variables.tf`

Khai báo:

- `aws_region`
- `sagemaker_endpoint_name`

#### `outputs.tf`

Xuất ra:

- `vector_bucket_name`
- `api_endpoint`
- `api_key_id`
- `api_key_value`
- `setup_instructions`

#### `terraform.tfvars.example`

Cho biết hai giá trị quan trọng phải điền:

- `aws_region`
- `sagemaker_endpoint_name`

### Cấu hình hạ tầng chính

Lambda `alex-ingest` hiện được cấu hình:

- runtime: `python3.12`
- timeout: `60`
- memory: `512`
- handler: `ingest_s3vectors.lambda_handler`

Biến môi trường được inject vào Lambda:

```text
VECTOR_BUCKET
SAGEMAKER_ENDPOINT
```

API Gateway hiện dùng:

- REST API
- stage `prod`
- route `POST /ingest`
- `api_key_required = true`
- integration kiểu `AWS_PROXY`

Usage plan hiện đặt:

- quota: `10000 requests / month`
- rate limit: `100 req/s`
- burst limit: `200`

## Day 4 - Phần 5: S3 Vectors và điểm lệch cần nhớ

### Điều guide mô tả

Guide Day 4 mô tả:

- học viên tạo **Vector Bucket** thủ công trên S3 Console;
- tạo index `financial-research`;
- dùng bucket đó như một stateful resource tách khỏi Terraform destroy.

### Điều implementation hiện tại của repo đang làm

`terraform/3_ingestion/main.tf` hiện:

- tạo `aws_s3_bucket.vectors` bằng Terraform;
- đồng thời IAM policy lại cấp quyền theo namespace `s3vectors:*`.

Điều này cho thấy repo đang có một điểm lệch cần nhớ:

- **guide/course narrative** nhấn mạnh S3 Vectors bucket/index tạo thủ công;
- **implementation Terraform hiện tại** lại có thêm phần regular S3 bucket tên `alex-vectors-<account_id>`.

### Ý nghĩa khi debug về sau

Nếu ingest/search lỗi trong những ngày sau, cần xác minh rõ:

1. đang lỗi ở regular S3 hay ở S3 Vectors namespace;
2. bucket/index thực tế đã được tạo ở Console chưa;
3. ARN và permissions `s3vectors:*` có đang khớp với resource thật không;
4. code local test đang đọc đúng `VECTOR_BUCKET` nào trong `.env`.

## Day 4 - Phần 6: Test end-to-end

### Mục tiêu

Xác minh chuỗi:

1. search khi database trống;
2. ingest 3 tài liệu mẫu;
3. search lại bằng semantic queries;
4. nếu cần thì cleanup để làm lại từ đầu.

### Bộ dữ liệu mẫu đang dùng

`test_ingest_s3vectors.py` ingest 3 tài liệu về:

- Tesla
- Amazon
- NVIDIA

### Semantic queries mẫu đang dùng

`test_search_s3vectors.py` dùng các truy vấn:

- `"electric vehicles and sustainable transportation"`
- `"cloud computing and AWS services"`
- `"artificial intelligence and GPU computing"`

Điểm hiển thị ra màn hình được tính theo:

```python
score = 1 - distance
```

### Ý nghĩa học thuật

Đây là bước xác minh semantic search thật sự hoạt động theo ngữ nghĩa, không chỉ theo keyword exact match.

## Giá trị output quan trọng cần lưu cho ngày sau

Sau Day 4, các giá trị tối thiểu cần có hoặc cần xác minh trong `.env` là:

```env
SAGEMAKER_ENDPOINT=alex-embedding-endpoint
VECTOR_BUCKET=alex-vectors-...
ALEX_API_ENDPOINT=https://.../prod/ingest
ALEX_API_KEY=...
```

Ngoài ra cần nhớ:

- region thực tế đang deploy;
- endpoint SageMaker dùng region nào;
- `terraform/3_ingestion` có local state riêng;
- `backend/ingest/lambda_function.zip` là artifact build quan trọng.

## Lỗi và bẫy quan trọng của Day 4

### Lỗi 1: thiếu `lambda_function.zip`

- triệu chứng:
  - `terraform apply` lỗi khi tạo Lambda hoặc deploy code không đúng.
- root cause:
  - chưa chạy `uv run package.py` trước khi deploy.
- cách fix:
  - build zip trước rồi chạy lại Terraform.

### Lỗi 2: API Gateway gọi lỗi `403` hoặc `500`

- triệu chứng:
  - gọi endpoint `/ingest` bị `Forbidden` hoặc `Internal Server Error`.
- root cause:
  - thiếu API key, API key chưa gắn usage plan, hoặc permission invoke Lambda chưa đúng.
- cách fix:
  - kiểm tra `aws_lambda_permission.api_gateway`, `aws_api_gateway_usage_plan_key`, và key value thật lấy từ CLI.

### Lỗi 3: ingest lỗi do embedding trả nested arrays

- triệu chứng:
  - put vector thất bại hoặc format vector không hợp lệ.
- root cause:
  - response từ Hugging Face container có dạng `[[[embedding]]]`.
- cách fix:
  - bóc response về mảng 1 chiều trước khi ghi vào vector store.

### Lỗi 4: nhầm giữa regular S3 bucket và S3 Vectors bucket/index

- triệu chứng:
  - cấu hình tưởng đúng nhưng local test hoặc Lambda vẫn không ghi/query được như kỳ vọng.
- root cause:
  - guide và implementation hiện tại không hoàn toàn đồng nhất về cách thể hiện lớp lưu trữ vector.
- cách fix:
  - xác minh lại resource thật trên AWS Console, `.env`, IAM policy, và tên bucket/index đang được code sử dụng.

## Các lệnh cốt lõi của Day 4

### Build package Lambda

```bash
cd backend/ingest
uv run package.py
```

### Deploy hạ tầng ingest

```bash
cd ../../terraform/3_ingestion
terraform init
terraform apply
```

### Xem output Terraform

```bash
terraform output
```

### Lấy API key thật

```bash
aws apigateway get-api-key --api-key YOUR_API_KEY_ID --include-value --query 'value' --output text
```

### Test ingest local trực tiếp

```bash
cd ../../backend/ingest
uv run test_ingest_s3vectors.py
```

### Test semantic search

```bash
uv run test_search_s3vectors.py
```

### Cleanup dữ liệu test

```bash
uv run cleanup_s3vectors.py
```

## Trạng thái kết thúc Day 4

Nếu Day 4 hoàn thành đúng, trạng thái mong muốn là:

1. đã hiểu rõ ingest pipeline nối giữa SageMaker và vector storage;
2. đã có `backend/ingest` như một uv project độc lập;
3. đã build được `lambda_function.zip`;
4. đã có hạ tầng `terraform/3_ingestion` với Lambda + API Gateway + API key;
5. đã lưu các output cần thiết vào `.env`;
6. đã hiểu cách test direct ingest, semantic search, và cleanup;
7. đã nhận diện được điểm lệch cần theo dõi giữa guide và implementation hiện tại của repo.

## Handoff sang Day 5

Trước khi bắt đầu Day 5, nên xác minh lại:

1. `SAGEMAKER_ENDPOINT`, `VECTOR_BUCKET`, `ALEX_API_ENDPOINT`, `ALEX_API_KEY` đã có trong `.env` chưa;
2. `terraform/3_ingestion` đã có state ổn định chưa;
3. local test ingest/search có chạy đúng chưa;
4. bucket/index vector thật trên AWS đang ở trạng thái nào;
5. region của SageMaker, API Gateway, và các script local có nhất quán chưa.

Khi sang Day 5, các thông tin từ Day 4 sẽ còn được dùng tiếp:

- knowledge base vector đã ingest được hay chưa;
- endpoint ingest public đang dùng URL nào;
- API key hiện tại là gì;
- region đang vận hành thực tế;
- thói quen debug theo từng lớp: local SDK -> Lambda -> API Gateway.

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

## Day 4

- Đã append nhật ký cho:
  - `tai_lieu/week3/day4_summary.md`
  - `guides/3_ingest.md`
  - `backend/ingest`
  - `terraform/3_ingestion`
- Đã ghi lại đầy đủ flow ingest, packaging, Terraform deploy, local test, và semantic search.
- Đã ghi chú điểm lệch cần theo dõi giữa guide Day 4 và implementation hiện tại của repo ở lớp vector storage.
