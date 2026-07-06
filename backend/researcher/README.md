# `backend/researcher` - Mã nguồn Researcher Service của Part 4

Thư mục này chứa toàn bộ **application code** cho thành phần **Researcher** trong dự án Alex.

Researcher là một service AI độc lập có nhiệm vụ:

- nhận yêu cầu nghiên cứu một chủ đề đầu tư;
- cố gắng duyệt web bằng Playwright MCP để tìm nguồn phù hợp;
- chỉ tạo ghi chú phân tích khi có **verified web-derived content**;
- chỉ gọi ingest pipeline của Part 3 khi có `source_url` sạch và nội dung web thật;
- trả kết quả về cho caller hoặc fail rõ nếu không lấy được article content thật.

Trong implementation hiện tại của repo:

- Researcher chạy bằng **FastAPI**
- được đóng gói thành **Docker image**
- deploy lên **AWS Lambda container image**
- public qua **Lambda Function URL**

Điều này quan trọng vì một số tài liệu cũ vẫn mô tả App Runner, nhưng source of truth hiện tại là Lambda Function URL.

## Vai trò của folder này trong toàn hệ thống

Nói ngắn gọn:

- `backend/researcher` là **logic chạy thật**
- `terraform/4_researcher` là **hạ tầng AWS** để chạy logic đó
- `backend/ingest` là **điểm lưu kết quả research** vào vector knowledge base

Luồng liên kết với các phần trước:

1. **Part 2** cung cấp embedding foundation qua SageMaker
2. **Part 3** cung cấp ingest API và vector storage
3. **Part 4** dùng Researcher để tạo nội dung mới rồi gửi sang ingest API của Part 3

## Luồng hoạt động chính

Luồng runtime cơ bản:

1. Client gọi `POST /research` vào Researcher
2. `server.py` nhận request và dựng query
3. `server.py` tạo agent từ:
   - prompt trong `context.py`
   - browser MCP trong `mcp_servers.py`
   - ingest tool trong `tools.py`
4. Agent thử browser path trước
5. Nếu browser path không ổn, runtime có thể đi sang:
   - constrained browser retry
6. Chỉ khi có note cuối dựa trên web content thật, agent mới được gọi `ingest_financial_document()`
7. `tools.py` gửi payload sang ingest API của Part 3
8. Kết quả được lưu vào knowledge base
9. Nếu không chứng minh được verified web content, Researcher trả `500` và không ingest gì

## Luồng deploy

1. `deploy.py` lấy AWS account/region
2. `deploy.py` build Docker image từ `Dockerfile`
3. `deploy.py` push image lên ECR
4. `deploy.py` ghi image URI vào `terraform/4_researcher/researcher.auto.tfvars.json`
5. `terraform/4_researcher` dùng image đó để deploy/update Lambda

Trong các phiên debug gần đây, do Terraform provider có lúc lỗi, team đã nhiều lần dùng đường deploy thủ công:

1. build image local
2. push ECR
3. `aws lambda update-function-code --image-uri ...`

Hiện tại `uv run deploy.py` đã deploy lại được theo flow chuẩn.

## Trạng thái thực tế hiện tại

Hiện tại Researcher đã:

- có terminal summary trong `test_research.py`;
- có structured observability ở `server.py`:
  - `run_id`
  - `phase_start`
  - `phase_end`
  - `request_end`
- có ingest telemetry rõ hơn ở `tools.py`:
  - `research_ingest`
  - `document_id`
  - `success/error`
- đã có follow-up ingest propagation để `request_end ingest_success` đọc observation theo `run_id`
- trong pass mới nhất:
  - `/research` chỉ còn chấp nhận `verified web content`
  - tool ingest yêu cầu `source_url` sạch
  - fallback note không còn được ingest vào S3 Vectors
  - agent bị cấm fabricate article URL và phải khám phá URL qua browser/search trước
  - `browser_run` chính hiện dùng `max_turns=30`
  - đã thử runtime experiment bỏ `--single-process` khỏi Playwright launch args
  - prompt đã được siết thêm `immediate-snapshot` constraint để giảm drift window
  - `browser_run` status giờ phân loại `article_captured` / `page_drifted` / `ok` thay vì chỉ `ok`
  - có `snapshot_page_url` log trong CloudWatch để truy vết URL thực tế khi snapshot
  - đã chứng minh được `success_verified` đầu tiên (NVIDIA AI datacenter demand, Investopedia article 2026-07-06)

Nhưng vẫn còn hạn chế:

- browser path trong Lambda vẫn chưa ổn định hoàn toàn (1/5 benchmark đạt `success_verified`, 4/5 vẫn fail);
- sau verified-web-only gate, đa số benchmark topic vẫn fail `500`;
- browser vẫn dễ rơi vào `about:blank`, `about:srcdoc`, client-storage/interstitial, hoặc ad-tech paths trước khi có article body sạch;
- browser có thể `status=ok` nhưng vẫn không lấy được article content usable.

## Trạng thái verify hiện tại

Các run live gần nhất xác nhận:

- `Microsoft cloud revenue growth`
  - từng fail với:
    - `Verified web content not obtained: page_not_found.`
  - sau anti-fabrication prompt fail với:
    - `Verified web content not obtained: ingest did not record a clean source URL.`
- `Tesla competitive advantages`
  - fail với:
    - `Verified web content not obtained: page_unavailable.`
- `NVIDIA AI datacenter demand`
  - **success_verified** ngày 2026-07-06
  - snapshot captured Investopedia article: `nvidia-is-telling-chinese-customers...nvda-11996472`
  - `browser_run status=article_captured`
  - đây là lần đầu tiên browser path chứng minh được verified web content extraction

Điều này có nghĩa là:

- vector store sạch hơn trước vì fallback note không còn bị ingest
- browser article retrieval trên Lambda headless runtime đã có bằng chứng thành công đầu tiên (NVIDIA/Investopedia)
- nhưng vẫn chưa đủ ổn định để gọi là fully proven (1/5, chưa reproducible)

## Các file trong folder

### Runtime chính

#### `server.py`

Đây là file quan trọng nhất trong folder.

Nhiệm vụ:

- khởi tạo FastAPI app;
- nhận request HTTP;
- dựng model runtime;
- chạy Researcher agent;
- xử lý browser run, constrained retry, và verified-web-only gate;
- ghi structured observability logs;
- expose các endpoint:
  - `/`
  - `/health`
  - `/research`
  - `/research/auto`
  - `/test-bedrock`

Đây là nơi chứa nghiệp vụ trung tâm của Researcher.

### Prompt và instruction

#### `context.py`

File này chứa prompt và instruction của agent.

Nhiệm vụ:

- quy định agent browse như thế nào;
- giới hạn số trang;
- ưu tiên nguồn nào;
- cấm fabricate article URL;
- xác định prompt mặc định khi không có topic.

Hiện tại source preference được định hướng theo:

- `Investopedia`
- `AP News`
- `CNN Business`
- `Reuters` chỉ là nguồn phụ nếu direct article page load sạch

### Tool kết nối ingest

#### `tools.py`

Đây là cầu nối giữa Researcher và Part 3.

Nhiệm vụ:

- nhận `topic`, `analysis`, và `source_url` từ agent;
- đóng gói document;
- từ chối ingest nếu content là fallback/degraded hoặc URL không sạch;
- gọi ingest API;
- retry khi gặp lỗi tạm thời.

File này liên kết trực tiếp với `backend/ingest` ở mức API.

### Browser / MCP

#### `mcp_servers.py`

File này tạo và cấu hình Playwright MCP server.

Nhiệm vụ:

- chọn browser binary;
- cấu hình launch args cho headless/container;
- ghi config tạm vào `/tmp`;
- hỗ trợ log stderr của MCP subprocess khi debug.

Đây là file rất quan trọng khi gặp:

- captcha
- redirect
- interstitial
- tracker noise
- lỗi browser trong Lambda
- networking/proxy oddities của Chromium trong Lambda headless runtime

### Deploy

#### `deploy.py`

Script deploy chính của Researcher.

Nhiệm vụ:

- lấy AWS account/region;
- bảo đảm ECR tồn tại;
- login ECR;
- build image;
- push image;
- cập nhật `researcher.auto.tfvars.json`;
- chạy Terraform apply;
- chờ Lambda active;
- in ra service URL.

### Test

#### `test_research.py`

Script test end-to-end trên service đã deploy.

Nhiệm vụ:

- lấy `researcher_url` từ Terraform output;
- gọi `/health`;
- gọi `/research`;
- in `RUN SUMMARY`;
- phân loại terminal outcome theo verified-web-only semantics;
- in nội dung research cuối;
- nhắc kiểm tra ingest bên `backend/ingest/test_search_s3vectors.py`.

Đây là script phù hợp nhất để test Step 4 hiện tại và quan sát request fail đúng khi không có verified web content.

#### `test_local.py`

Script test Researcher local.

Nhiệm vụ:

- chạy agent local;
- tạo MCP local;
- in final output.

Script này phù hợp để test nhanh trước khi deploy.

### Build local

#### `build_local.sh`

Script shell để build và chạy container Researcher local.

Nhiệm vụ:

- đọc `.env` từ repo root;
- build image local;
- chạy container local trên cổng `8000`.

Nó giúp mô phỏng môi trường container gần production hơn so với chạy `uvicorn` thuần.

### Container

#### `Dockerfile`

File build image của Researcher.

Nhiệm vụ:

- cài Node.js;
- cài `@playwright/mcp`;
- cài Chromium;
- cài Python dependency bằng `uv`;
- copy code ứng dụng;
- thêm Lambda Web Adapter;
- chạy `uvicorn`.

Đây là nền tảng để Lambda chạy FastAPI app như một HTTP service.

### Cấu hình Python project

#### `pyproject.toml`

File định nghĩa `backend/researcher` là một `uv` project độc lập.

Nhiệm vụ:

- khai báo Python version;
- khai báo dependency;
- hỗ trợ local development;
- hỗ trợ Docker build.

#### `uv.lock`

File lock dependency do `uv` sinh ra.

Nhiệm vụ:

- cố định version package;
- giúp local/container reproducible hơn.

Thông thường không nên chỉnh tay.

### File phụ trợ

#### `.python-version`

Gợi ý Python version cho local environment.

#### `.dockerignore`

Giảm file rác đi vào Docker build context.

### Tài liệu nội bộ

#### `BUG_AND_FIX.md`

Ghi lại incident history và root cause đã gặp trong Part 4.

#### `OBSERVABILITY_AND_BENCHMARK_SPEC.md`

Mô tả hướng quan sát, benchmark và failure taxonomy của Researcher.

#### `session_handoff.md`

Nhật ký handoff giữa các session để không mất context khi mở chat mới.
