# `backend/ingest` - Ingestion Code cho Part 3

Thư mục này chứa toàn bộ mã Python phục vụ **Part 3 - Ingestion Pipeline** của dự án Alex.

Vai trò của thành phần này là:

- nhận văn bản nghiên cứu hoặc tài liệu đầu vào;
- gọi **SageMaker Endpoint** để tạo **embedding vector**;
- ghi vector cùng metadata vào **S3 Vectors**;
- hỗ trợ test local, semantic search, cleanup dữ liệu;
- đóng gói mã nguồn thành file zip để deploy lên **AWS Lambda**.

Nói ngắn gọn: đây là phần **application code** của pipeline ingest.

## Mục tiêu của thư mục này

Part 3 của khóa học cần một Lambda function có thể:

1. nhận `text`;
2. biến `text` thành vector 384 chiều bằng model embedding ở Part 2;
3. lưu vector đó vào index `financial-research`;
4. cho phép kiểm tra lại bằng script test/search ở local.

Thư mục `backend/ingest` chính là nơi chứa toàn bộ logic đó.

## Các file trong thư mục

### File mã nguồn chính

#### `ingest_s3vectors.py`

Đây là file quan trọng nhất trong thư mục.

Nhiệm vụ:

- đóng vai trò **Lambda handler** chính cho endpoint ingest;
- đọc payload đầu vào;
- kiểm tra trường `text`;
- gọi SageMaker để lấy embedding;
- tạo `document_id` duy nhất;
- ghi dữ liệu vào S3 Vectors.

Khi Terraform ở `terraform/3_ingestion` tạo Lambda `alex-ingest`, handler sẽ trỏ vào:

```python
ingest_s3vectors.lambda_handler
```

Đây là file production chính dùng khi client gọi API Gateway `/ingest`.

#### `search_s3vectors.py`

File này chứa Lambda-style handler cho chức năng search vector.

Nhiệm vụ:

- nhận query text;
- gọi SageMaker để vector hóa query;
- gọi `query_vectors`;
- trả về danh sách kết quả gần nhất về ngữ nghĩa.

Trong Part 3 hiện tại, file này chủ yếu giúp học và tái sử dụng logic search. Nó chưa phải endpoint chính đang public qua Terraform trong thư mục `3_ingestion`, nhưng rất hữu ích để hiểu cách semantic retrieval hoạt động.

### File test và tiện ích local

#### `test_ingest_s3vectors.py`

Script test local để kiểm tra ingest trực tiếp bằng SDK.

Nhiệm vụ:

- đọc cấu hình từ `.env`;
- gọi SageMaker;
- ghi trực tiếp 3 tài liệu mẫu vào S3 Vectors;
- xác minh rằng luồng ingest hoạt động mà không cần đi qua API Gateway.

Đây là cách test rất tốt để tách lỗi:

- nếu script này lỗi, vấn đề thường nằm ở cấu hình local, quyền AWS, SageMaker, hoặc S3 Vectors;
- nếu script này chạy được nhưng API lỗi, vấn đề thường nằm ở API Gateway hoặc Lambda deploy.

#### `test_search_s3vectors.py`

Script test local cho semantic search.

Nhiệm vụ:

- đọc bucket/index từ `.env`;
- tạo embedding cho query;
- gọi `query_vectors`;
- in ra các kết quả liên quan;
- minh họa semantic search bằng các truy vấn mẫu.

File này giúp bạn thấy rõ lợi ích của vector search:

- truy vấn không cần khớp keyword y hệt;
- hệ thống vẫn tìm được tài liệu liên quan về mặt ngữ nghĩa.

#### `cleanup_s3vectors.py`

Script tiện ích để xóa dữ liệu test trong index.

Nhiệm vụ:

- query toàn bộ dữ liệu theo từng batch;
- xóa từng vector ra khỏi index;
- đưa knowledge base về trạng thái rỗng để test lại từ đầu.

File này đặc biệt hữu ích khi bạn muốn:

- chạy lại demo nhiều lần;
- xác minh trước/sau ingest;
- dọn dữ liệu mẫu để quan sát kết quả rõ hơn.

### File đóng gói và cấu hình môi trường Python

#### `package.py`

Đây là script build artifact cho Lambda.

Nhiệm vụ:

- lấy dependencies từ `.venv`;
- copy source code cần thiết;
- tạo `lambda_function.zip`.

File zip này sẽ được Terraform dùng để deploy lên Lambda.

Luồng sử dụng chuẩn:

```bash
cd backend/ingest
uv run package.py
```

Sau đó Terraform ở `terraform/3_ingestion` sẽ tham chiếu đến:

```text
../../backend/ingest/lambda_function.zip
```

#### `pyproject.toml`

File định nghĩa thư mục này như một **uv project** riêng.

Nhiệm vụ:

- khai báo phiên bản Python;
- khai báo dependencies;
- làm nguồn để `uv` cài môi trường local.

#### `uv.lock`

File lock dependency do `uv` tạo ra.

Nhiệm vụ:

- cố định phiên bản package;
- giúp môi trường của bạn ổn định hơn giữa các lần cài đặt.

Thông thường không chỉnh tay file này.

#### `.python-version`

File nhỏ dùng để gợi ý phiên bản Python cho môi trường local.

### File generated

#### `lambda_function.zip`

Artifact build ra từ `package.py`.

Nhiệm vụ:

- là gói code + dependency để deploy Lambda.

Đây không phải file nên sửa tay.

## Cách các file liên kết với nhau

### Liên kết nội bộ trong thư mục

Luồng chính:

1. `pyproject.toml` định nghĩa môi trường Python.
2. `uv` cài dependency vào `.venv`.
3. `package.py` lấy dependency từ `.venv` và tạo `lambda_function.zip`.
4. `ingest_s3vectors.py` là source code handler chính được đóng gói vào zip.
5. `terraform/3_ingestion/main.tf` dùng zip đó để tạo Lambda `alex-ingest`.

Luồng test local:

1. `test_ingest_s3vectors.py` đọc `.env`.
2. Script gọi SageMaker để lấy embedding.
3. Script ghi dữ liệu vào S3 Vectors.
4. `test_search_s3vectors.py` truy vấn lại để kiểm tra.
5. `cleanup_s3vectors.py` dọn dữ liệu khi cần reset.

### Liên kết với thư mục khác

Thư mục này phụ thuộc trực tiếp vào:

- `terraform/2_sagemaker`
  - vì cần endpoint embedding đã deploy trước đó;
- `terraform/3_ingestion`
  - vì thư mục đó dùng `lambda_function.zip` để tạo hạ tầng AWS;
- `.env` ở root project
  - vì các script local đọc cấu hình từ đó.

## Luồng hoạt động end-to-end

### Luồng production qua API Gateway

1. Client gửi request `POST /ingest` đến API Gateway.
2. API Gateway kiểm tra `x-api-key`.
3. API Gateway invoke Lambda `alex-ingest`.
4. Lambda chạy `ingest_s3vectors.lambda_handler`.
5. Handler lấy `text` từ payload.
6. Handler gọi SageMaker endpoint để tạo embedding.
7. Handler ghi vector vào S3 Vectors cùng metadata.
8. Lambda trả `document_id` về cho client.

### Luồng test local trực tiếp

1. Chạy `uv run test_ingest_s3vectors.py`.
2. Script đọc `VECTOR_BUCKET` và `SAGEMAKER_ENDPOINT` từ `.env`.
3. Script nạp 3 tài liệu mẫu.
4. Chạy `uv run test_search_s3vectors.py`.
5. Script search truy vấn dữ liệu vừa nạp.
6. Nếu cần reset, chạy `uv run cleanup_s3vectors.py`.

## Vì sao thư mục này được tách riêng

Việc tách `backend/ingest` thành một thư mục riêng có lợi vì:

- đây là một đơn vị deploy độc lập;
- dependency của nó khác với các phần khác của backend;
- dễ package thành Lambda;
- dễ test local mà không cần kéo toàn bộ hệ thống lên.

Đây là một pattern tốt cho serverless project:

- mỗi thành phần deployable nên có code, dependency, và script build riêng.

## Cấu hình mà thư mục này cần

Khi chạy local hoặc deploy, các giá trị quan trọng gồm:

- `VECTOR_BUCKET`
- `SAGEMAKER_ENDPOINT`
- `INDEX_NAME` nếu muốn override

Trong production, Terraform sẽ inject một phần các biến này vào Lambda.
Trong local, script test đọc chúng từ `.env`.

## Cách dùng nhanh

### Cài môi trường

```bash
cd backend/ingest
uv sync
```

### Tạo package Lambda

```bash
uv run package.py
```

### Test ingest local

```bash
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

## Tóm tắt

Thư mục `backend/ingest` là phần **code thực thi** của Part 3.

Nó chịu trách nhiệm:

- ingest dữ liệu;
- vector hóa dữ liệu bằng SageMaker;
- lưu dữ liệu vào S3 Vectors;
- test/search/cleanup ở local;
- đóng gói thành artifact để deploy Lambda.

Nếu `terraform/3_ingestion` là phần **hạ tầng**, thì `backend/ingest` là phần **logic ứng dụng** mà hạ tầng đó chạy.
