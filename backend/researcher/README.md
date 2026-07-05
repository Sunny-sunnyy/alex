# `backend/researcher` - Mã nguồn Researcher Service cho Part 4

Thư mục này chứa toàn bộ **application code** của thành phần **Researcher** trong dự án Alex.

Researcher là một AI service chuyên:

- nhận yêu cầu nghiên cứu một chủ đề đầu tư;
- dùng OpenAI Agents SDK để điều phối agent;
- dùng Playwright MCP để duyệt web khi cần;
- tạo ghi chú/phân tích tài chính ngắn;
- gọi ingest pipeline của Part 3 để lưu kết quả vào knowledge base.

Nói ngắn gọn:

- `backend/researcher` là **logic chạy thật** của Researcher;
- `terraform/4_researcher` là **hạ tầng AWS** để deploy logic đó.

## Thành phần này làm gì?

Researcher là service nghiên cứu độc lập, không phải orchestrator của Part 6.

Nhiệm vụ chính:

1. nhận `topic` từ request hoặc tự chọn chủ đề;
2. duyệt web để lấy thông tin thị trường nếu browser hoạt động ổn;
3. tóm tắt thành ghi chú đầu tư ngắn;
4. lưu ghi chú đó vào knowledge base qua ingest API;
5. trả kết quả cho caller.

Trong implementation hiện tại của repo:

- Researcher chạy dưới dạng **FastAPI app**
- được đóng gói thành **Docker image**
- deploy lên **AWS Lambda container image**
- public qua **Lambda Function URL**

Điều này quan trọng vì một số guide cũ vẫn mô tả App Runner, nhưng code hiện tại của repo đã đi theo hướng Lambda Function URL.

## Các file trong thư mục

### File runtime chính

#### `server.py`

Đây là file quan trọng nhất của thư mục.

Nhiệm vụ:

- khởi tạo FastAPI app;
- đọc cấu hình môi trường;
- dựng model runtime;
- chạy Researcher agent;
- xử lý fallback khi browser/MCP gặp lỗi;
- expose các endpoint:
  - `/`
  - `/health`
  - `/research`
  - `/research/auto`
  - `/test-bedrock`

Đây là nơi chứa luồng nghiệp vụ chính của Researcher.

### File prompt / instruction

#### `context.py`

File này chứa prompt và instruction cho agent.

Nhiệm vụ:

- định nghĩa cách agent phải browse, analyze, và save;
- giới hạn số trang browse;
- ưu tiên nguồn nào;
- tạo prompt mặc định khi người dùng không truyền topic.

Nếu muốn tinh chỉnh hành vi research, đây là một trong những file đầu tiên cần đọc.

### File tool

#### `tools.py`

File này định nghĩa tool mà agent dùng để lưu kết quả research.

Nhiệm vụ:

- nhận `topic` và `analysis` từ agent;
- đóng gói thành payload ingest;
- gọi API Gateway ingest của Part 3;
- retry nếu gặp lỗi tạm thời.

Nói cách khác:

- `tools.py` là điểm nối giữa Researcher và `backend/ingest`.

### File MCP / browser

#### `mcp_servers.py`

File này tạo và cấu hình Playwright MCP server.

Nhiệm vụ:

- tạo MCPServerStdio cho Playwright;
- cấu hình browser args phù hợp môi trường headless/container;
- chọn chrome binary;
- ghi config tạm ra `/tmp`;
- hỗ trợ logging stderr của MCP subprocess khi debug.

Đây là file rất quan trọng khi Researcher gặp lỗi liên quan đến browser, captcha, redirect, hoặc filesystem.

### File deploy

#### `deploy.py`

Đây là script deploy chính cho Researcher.

Nhiệm vụ:

- lấy account/region;
- bảo đảm ECR repo đã có;
- build Docker image;
- push image lên ECR;
- ghi image URI vào `terraform/4_researcher/researcher.auto.tfvars.json`;
- chạy `terraform apply`;
- chờ Lambda active;
- in ra service URL sau deploy.

Đây là file phản ánh rõ nhất cách deployment thực tế hiện nay đang hoạt động.

### File test

#### `test_research.py`

Script test end-to-end cho service đã deploy.

Nhiệm vụ:

- lấy `researcher_url` từ Terraform output;
- gọi `/health`;
- gọi `/research`;
- in kết quả research;
- nhắc người dùng kiểm tra knowledge base bằng `backend/ingest/test_search_s3vectors.py`.

Đây là script phù hợp nhất để test Step 4 của Guide 4.

#### `test_local.py`

Script test agent ở local.

Nhiệm vụ:

- chạy Researcher mà không cần gọi Lambda URL;
- dùng MCP local;
- in final output ra console.

Script này hữu ích để test nhanh prompt hoặc tool behavior trước khi deploy.

### File build local

#### `build_local.sh`

Script shell chạy Researcher container ở local.

Nhiệm vụ:

- đọc `.env` từ root repo;
- build image local;
- chạy container local trên cổng `8000`.

Nó giúp kiểm tra môi trường container gần với production hơn so với chạy `uvicorn` trực tiếp.

### File container

#### `Dockerfile`

File build image cho Researcher.

Nhiệm vụ:

- cài Node.js;
- cài Playwright MCP;
- cài Chromium và dependency Linux;
- cài dependency Python bằng `uv`;
- copy code ứng dụng;
- thêm Lambda Web Adapter;
- chạy `uvicorn`.

Đây là nền tảng để Lambda có thể chạy FastAPI app như một HTTP service.

### File cấu hình project Python

#### `pyproject.toml`

File định nghĩa đây là một `uv` project độc lập.

Nhiệm vụ:

- khai báo Python version;
- khai báo dependency;
- làm nguồn cho local development và Docker build.

#### `uv.lock`

File lock dependency do `uv` sinh ra.

Nhiệm vụ:

- cố định version package;
- giúp môi trường local/container ổn định hơn.

Thông thường không chỉnh tay file này.

### File môi trường phụ

#### `.python-version`

Gợi ý version Python cho local environment.

#### `.dockerignore`

Giảm bớt file không cần thiết khi build Docker image.

### File ghi nhận incident

#### `BUG_AND_FIX.md`

Đây là file lịch sử debugging và incident notes.

Nhiệm vụ:

- ghi lại các lỗi đã gặp;
- root cause đã xác minh;
- các thay đổi đã làm;
- tình trạng hiện tại;
- các bước tiếp theo.

Nếu bạn muốn biết vì sao Researcher đã được sửa như hiện nay, hãy đọc file này.

## Cách các file trong thư mục liên kết với nhau

### Luồng runtime chính

1. `server.py` nhận request HTTP.
2. `server.py` lấy prompt từ `context.py`.
3. `server.py` tạo MCP browser qua `mcp_servers.py` nếu chạy browser mode.
4. `server.py` tạo agent và gắn tool từ `tools.py`.
5. Agent tạo nội dung research.
6. Agent gọi `ingest_financial_document()` trong `tools.py`.
7. `tools.py` gọi ingest API của Part 3.
8. Kết quả được lưu vào knowledge base.

### Luồng deploy

1. `deploy.py` build image từ `Dockerfile`.
2. `deploy.py` push image lên ECR.
3. `deploy.py` ghi image URI cho Terraform.
4. `terraform/4_researcher` deploy hoặc update Lambda bằng image đó.

### Luồng test

#### Test local

1. chạy `uv run test_local.py`
2. script tạo agent local
3. script dùng `context.py`, `mcp_servers.py`, `tools.py`
4. in output ra console

#### Test deployed service

1. chạy `uv run test_research.py`
2. script lấy URL từ `terraform/4_researcher`
3. gọi `/health`
4. gọi `/research`
5. Researcher lưu kết quả vào ingest pipeline
6. sau đó có thể kiểm tra bằng `backend/ingest/test_search_s3vectors.py`

## Luồng hoạt động end-to-end của Researcher

### Luồng research thành công

1. Client gọi `POST /research`
2. `server.py` xây query từ topic hoặc prompt mặc định
3. Agent dùng browser nếu có thể
4. Agent viết ghi chú đầu tư ngắn
5. Agent gọi `ingest_financial_document`
6. Tool gọi ingest API
7. Ingest pipeline tạo embedding và lưu vào vector store
8. Researcher trả nội dung về cho client

### Luồng fallback

Nếu browser mode không ổn:

1. `server.py` thử prompt constrained hơn
2. nếu vẫn fail vì `MaxTurnsExceeded`, chuyển sang browserless fallback
3. vẫn tạo một ghi chú ngắn
4. vẫn ingest vào knowledge base

Điều này giúp request không bị fail hoàn toàn chỉ vì browser bị loop hoặc captcha.

## Thư mục này liên kết với các phần trước như thế nào?

### Liên kết với `backend/ingest`

Đây là mối liên kết quan trọng nhất.

Researcher **không tự lưu trực tiếp** vào vector store.

Thay vào đó:

- `tools.py` gọi ingest API của Part 3;
- API đó được phục vụ bởi Lambda ingest;
- Lambda ingest dùng SageMaker để tạo embedding;
- rồi lưu vào vector storage.

Nói cách khác:

- `backend/researcher` tạo **nội dung research**
- `backend/ingest` chịu trách nhiệm **vector hóa và lưu**

### Liên kết với `terraform/3_ingestion`

Researcher cần:

- `ALEX_API_ENDPOINT`
- `ALEX_API_KEY`

Hai giá trị này đến từ output của `terraform/3_ingestion`.

Nếu Part 3 chưa deploy hoặc cấu hình sai:

- Researcher vẫn có thể tạo text,
- nhưng bước ingest sẽ không hoạt động đúng.

### Liên kết với `terraform/2_sagemaker`

Researcher không gọi SageMaker trực tiếp.

Nhưng ingest pipeline của Part 3 lại gọi SageMaker endpoint từ Part 2.

Vì vậy theo chuỗi phụ thuộc:

- Researcher -> Ingest -> SageMaker

Nếu endpoint SageMaker hỏng:

- bước ingest của Researcher cũng sẽ hỏng theo.

### Liên kết với `terraform/4_researcher`

`backend/researcher` là code.

`terraform/4_researcher` là hạ tầng để chạy code đó trên AWS.

Quan hệ chính:

- `deploy.py` dùng `terraform/4_researcher` để deploy
- `test_research.py` dùng Terraform output từ folder đó để lấy URL

## Các biến môi trường mà Researcher cần

Các biến quan trọng gồm:

- `OPENAI_API_KEY`
- `ALEX_API_ENDPOINT`
- `ALEX_API_KEY`
- `RESEARCHER_MODEL`
- `BEDROCK_REGION`
- `MCP_LOGGING`

Ý nghĩa:

- `OPENAI_API_KEY`: tracing hoặc runtime OpenAI model
- `ALEX_API_ENDPOINT`: URL ingest từ Part 3
- `ALEX_API_KEY`: API key cho ingest endpoint
- `RESEARCHER_MODEL`: model đang dùng, hiện thường là `openai/gpt-5.4-nano`
- `BEDROCK_REGION`: giữ lại cho nhánh AWS/Bedrock hoặc cấu hình liên quan
- `MCP_LOGGING`: bật log chi tiết cho MCP/browser

## Cách hiểu thư mục này theo vai trò

Nếu phải tóm tắt ngắn:

- `server.py` là bộ não điều phối request
- `context.py` là prompt/policy
- `mcp_servers.py` là browser layer
- `tools.py` là cầu nối sang ingest
- `deploy.py` là đường deploy production
- `test_research.py` là bài test Step 4
- `BUG_AND_FIX.md` là lịch sử lỗi và hướng sửa

## Tóm tắt

`backend/researcher` là phần **service logic** của Researcher trong Part 4.

Nó:

- tạo research note;
- dùng browser khi có thể;
- fallback khi browser không ổn;
- lưu kết quả vào knowledge base qua ingest pipeline;
- và được deploy dưới dạng Lambda container image trong implementation hiện tại của repo.

