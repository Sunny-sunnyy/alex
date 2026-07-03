# 83. Day 5 - Building AI Research Agents with MCP Servers and Data Pipelines

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [83. Day 5 - Building AI Research Agents with MCP Servers and Data Pipelines.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/83.%20Day%205%20-%20Building%20AI%20Research%20Agents%20with%20MCP%20Servers%20and%20Data%20Pipelines.txt) - Đã dùng
- Slide: [Production W3D5.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D5.pdf) - Đã dùng (đối chiếu nội dung qua transcript)
- Code: Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này (đây là bài lý thuyết định hướng ban đầu)
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) và [day4_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day4_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Mở đầu Day 5 với nhiệm vụ hoàn thành đường ống dữ liệu (data pipeline) tự động cho ứng dụng capstone Alex bằng cách xây dựng một tác tử nghiên cứu độc lập (Researcher Agent).
- Giới thiệu khái quát về ngành khoa học dữ liệu (Data Engineering): Thiết lập các đường ống dẫn dữ liệu (data pipelines) có khả năng co giãn (scalable) và chịu lỗi tốt.
- Giải thích chi tiết khái niệm ETL (Extract - trích xuất, Transform - chuyển đổi, Load - nạp) cùng các framework xử lý dữ liệu lớn như Apache Spark và Apache Beam phục vụ tính toán phân tán.
- Trình bày kiến trúc dữ liệu doanh nghiệp Medallion Architecture với ba phân tầng dữ liệu: Bronze (dữ liệu thô), Silver (dữ liệu làm sạch và chuẩn hóa), và Gold (dữ liệu tinh lọc sẵn sàng phân tích).
- Giải thích vị trí của Researcher Agent trong kiến trúc dữ liệu của dự án Alex: Đóng vai trò là nguồn dữ liệu (Source) thu thập thông tin tài chính qua trình duyệt Playwright MCP Server, tự chuyển đổi qua Bedrock LLM và nạp vào database qua Ingest Lambda.
- Định hướng triển khai tác tử trong một Docker container đẩy lên ECR và deploy thông qua Terraform.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu định nghĩa cốt lõi của ngành khoa học dữ liệu (Data Engineering) và vai trò của nó trong hệ thống sản xuất.
  - Nắm được khái niệm Medallion Architecture (Bronze, Silver, Gold) trong thiết kế kho dữ liệu doanh nghiệp.
  - Hiểu luồng di chuyển của dữ liệu từ internet vào S3 Vectors qua trung gian Researcher Agent.
- **Practical goals - mục tiêu thực hành**:
  - Có khả năng phác thảo được sơ đồ luồng dữ liệu ETL mini trong hệ thống của dự án Alex.
- **What learner should be able to explain - người học cần giải thích được**:
  - Sự khác nhau giữa các tầng dữ liệu Bronze, Silver, và Gold.
  - Vai trò của các framework Spark/Beam đối với các đường ống dữ liệu lớn.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này tích hợp trực tiếp với kết quả của Day 4 (Ingest Lambda + API Gateway + S3 Vectors). Researcher Agent được xây dựng ở bài học này sẽ đóng vai trò là "client" gọi đến Ingest API Gateway đã dựng tại Day 4 để nạp thông tin.

## 5. Core Theory - Lý thuyết cốt lõi
- **Data Engineering - Khoa học dữ liệu**: Lĩnh vực chuyên biệt tập trung vào việc thiết kế, xây dựng và quản trị các hệ thống thu thập, xử lý và lưu trữ dữ liệu quy mô lớn một cách đáng tin cậy.
- **ETL (Extract, Transform, Load)**: Quy trình chuẩn trong kỹ thuật dữ liệu: trích xuất dữ liệu từ nguồn thô (Extract), biến đổi dữ liệu sang định dạng chuẩn ngữ nghĩa (Transform), và ghi dữ liệu vào kho lưu trữ đích (Load).
- **Medallion Architecture - Kiến trúc Huy chương**: Mô hình thiết kế kho dữ liệu phân tầng nhằm tăng chất lượng dữ liệu qua từng bước xử lý:
  - Tầng Bronze (Raw): Lưu trữ dữ liệu gốc chưa qua xử lý.
  - Tầng Silver (Cleaned): Dữ liệu được làm sạch, lọc trùng, chuẩn hóa cấu trúc.
  - Tầng Gold (Curated): Dữ liệu phân tích cao cấp đã được tổng hợp, sẵn sàng phục vụ cho các báo cáo hoặc AI models.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
`Không có pipeline rõ ràng trong tài liệu nguồn`
Thay vào đó, bài học giới thiệu về luồng tư duy thiết kế Medallion trong RAG Pipeline của Alex:
1. **Bronze Stage**: Researcher thu thập tin tức dạng HTML/Text thô từ các trang tài chính.
2. **Silver Stage**: Bedrock LLM tóm tắt, trích lọc các ý chính quan trọng của doanh nghiệp.
3. **Gold Stage**: SageMaker Endpoint sinh vector và Ingest Lambda lập chỉ mục lưu vào S3 Vectors, sẵn sàng cho các Agent khác truy vấn báo cáo.

## 7. Techniques - Kỹ thuật sử dụng
- **Medallion Data Staging - Phân tầng dữ liệu Medallion**:
  - Purpose (mục đích): Tăng chất lượng dữ liệu và tính minh bạch, cho phép truy vết và phục hồi dữ liệu gốc khi có lỗi xảy ra ở các bước biến đổi.
  - When to use (dùng khi nào): Khi xây dựng các hệ thống dữ liệu doanh nghiệp lớn, tích hợp nhiều nguồn dữ liệu thô không đồng nhất.
  - Trade-off (đánh đổi): Làm tăng cost (chi phí) lưu trữ do phải nhân bản dữ liệu qua nhiều tầng và tăng độ phức tạp của pipeline.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Ingest trực tiếp dữ liệu thô (Bronze) vào cơ sở dữ liệu vector**
  - Pros: Nhanh gọn, không cần tốn chi phí gọi LLM ở đầu nạp để chuyển đổi.
  - Cons: Dữ liệu chứa nhiều rác (quảng cáo, mã HTML), làm giảm chất lượng tìm kiếm ngữ nghĩa và tăng cost (chi phí) xử lý token của LLM ở đầu đọc.
  - When to choose: Các tài liệu nguồn đã được định dạng sạch sẽ từ trước (như PDF chuẩn, text thuần).
- **Option 2: Áp dụng quy trình ETL tinh lọc dữ liệu (Silver/Gold) trước khi nạp (Lựa chọn của dự án)**
  - Pros: Dữ liệu được cô đọng, chất lượng embeddings cao, tiết kiệm chi phí token cho LLM khi đọc ngữ cảnh.
  - Cons: Phát sinh chi phí gọi LLM nạp (Bedrock) để tóm tắt dữ liệu thô ban đầu.
  - When to choose: (Recommended) Các nguồn dữ liệu cào từ web, tin tức báo chí chứa nhiều tạp chất.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Hỏng hóc đường ống dữ liệu (data pipeline silent failure).
  - Root cause: Dữ liệu đầu vào thay đổi cấu trúc đột ngột (ví dụ giao diện web thay đổi khiến playwright crawl sai lớp css), nhưng pipeline không có cơ chế cảnh báo, tiếp tục đẩy dữ liệu rác hoặc rỗng vào database.
  - Symptom: Cơ sở dữ liệu chứa các vector rỗng hoặc thông tin rác, làm giảm độ chính xác của chatbot AI mà không báo lỗi runtime.
  - Fix / prevention: Thiết lập các bước validation (kiểm chứng dữ liệu) ở tầng Silver trước khi chuyển sang Gold và ghi logs chi tiết.

## 11. Knowledge Extension - Kiến thức mở rộng
- Các hệ thống lớn thường sử dụng công cụ điều phối (orchestration tools) như Apache Airflow hoặc Prefect để quản lý vòng đời của các tác vụ ETL. Trong bài học này, chúng ta sử dụng một cơ chế serverless tối giản hơn là AWS EventBridge kết hợp với Lambda Scheduler để quản lý cadence (nhịp độ) nạp dữ liệu.

## 12. Study Pack - Gói ôn tập
### Must remember
1. ETL viết tắt của **Extract - trích xuất, Transform - chuyển đổi, Load - nạp**.
2. Medallion Architecture gồm ba tầng dữ liệu: Bronze (thô), Silver (làm sạch), và Gold (sẵn sàng phân tích).
3. Spark và Beam là các công cụ hỗ trợ tính toán phân tán cho dữ liệu lớn.
4. Researcher Agent đóng vai trò là "extractor" (trích xuất) dữ liệu thô từ internet.

### Self-check questions
1. Hãy trình bày ý nghĩa của ba tầng Bronze, Silver, Gold trong Medallion Architecture.
2. Tại sao việc chuyển đổi dữ liệu thô sang dữ liệu tinh lọc (ETL) lại quan trọng đối với các hệ thống RAG?

### Flashcards
- Q: Quy trình chuẩn của Data Engineering để đưa dữ liệu vào kho lưu trữ là gì?
  A: ETL (Extract, Transform, Load).
- Q: Tầng dữ liệu chứa thông tin nguyên bản nhất trong Medallion Architecture là gì?
  A: Bronze (Raw data).

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 84. Day 5 - Building AI Research Agents with Bedrock and OpenAI SDK on AWS

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [84. Day 5 - Building AI Research Agents with Bedrock and OpenAI SDK on AWS.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/84.%20Day%205%20-%20Building%20AI%20Research%20Agents%20with%20Bedrock%20and%20OpenAI%20SDK%20on%20AWS.txt) - Đã dùng
- Slide: [Production W3D5.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D5.pdf) - Đã dùng (đối chiếu nội dung qua transcript)
- Code:
  - [server.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/server.py) - Đã dùng và phân tích
  - [tools.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/tools.py) - Đã dùng và phân tích
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) và [day4_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day4_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Thiết lập quyền truy cập cho Bedrock models trên AWS Console (yêu cầu root user).
- Mô hình mã nguồn mở GPT OSS 120B chỉ khả dụng tại region `us-west-2` (Oregon), trong khi các mô hình Amazon Nova Pro có thể sử dụng tại region mặc định của học viên (như `us-east-1`).
- Giải thích lỗi kỹ thuật tạm thời (bug) liên quan đến tính năng gọi công cụ (tool calling) của mô hình OSS 120B trên Bedrock, do đó dự án linh hoạt chuyển hướng cấu hình sang sử dụng **Amazon Nova Pro** làm model chính.
- Làm rõ vai trò của `OPENAI_API_KEY`: Dù mô hình LLM chạy thông qua AWS Bedrock, OpenAI Agents SDK vẫn yêu cầu một API key để kích hoạt dashboard giám sát và lưu trữ log thực thi tác tử (agent tracing). Việc này hoàn toàn không phát sinh chi phí token của OpenAI.
- Thiết lập tệp tin biến môi trường `.env` ở thư mục gốc chứa `OPENAI_API_KEY` và cấu hình file `terraform.tfvars` trong thư mục `terraform/4_researcher` để chuẩn bị các tham số cho hạ tầng.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu cách thức cấu hình và yêu cầu quyền sử dụng mô hình (model access) trên Amazon Bedrock.
  - Hiểu được tại sao một SDK (như OpenAI Agents SDK) lại có thể tích hợp đa dạng với các nhà cung cấp mô hình khác (như Bedrock qua LiteLLM).
  - Nắm được cơ chế bảo mật xác thực của Bedrock thông qua IAM role thay vì dùng API Key truyền thống.
- **Practical goals - mục tiêu thực hành**:
  - Thực hành kích hoạt quyền sử dụng các mô hình Nova Pro và GPT OSS trên AWS Bedrock Console.
  - Tạo lập và điền đầy đủ các tham số cấu hình trong tệp `terraform.tfvars` và `.env`.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao mô hình Nova Pro lại cần thiết cho Researcher Agent thay vì dùng Nova Lite.
  - Lý do cần cấu hình `OPENAI_API_KEY` dù LLM chạy hoàn toàn trên Bedrock.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này kế thừa và sử dụng endpoint và API key sinh ra từ Day 4 (`ALEX_API_ENDPOINT`, `ALEX_API_KEY`) để cấu hình cho biến môi trường của Researcher Agent.

## 5. Core Theory - Lý thuyết cốt lõi
- **Model Access - Quyền truy cập mô hình**: Quy trình bảo mật bắt buộc của AWS Bedrock yêu cầu người dùng phải xác nhận cam kết sử dụng và gửi yêu cầu kích hoạt trước khi có thể gọi API của các dòng mô hình lớn.
- **Agent Tracing - Theo dõi vết tác tử**: Cơ chế ghi lại chi tiết các bước suy luận, các lượt suy nghĩ (thought) và các lần gọi công cụ (tool calls) của tác tử để hỗ trợ giám sát và gỡ lỗi.
- **LiteLLM**: Thư viện Python trung gian cho phép lập trình viên sử dụng một API chuẩn duy nhất (thường bám theo chuẩn của OpenAI) để gọi tới hàng trăm mô hình ngôn ngữ lớn của các nhà cung cấp khác nhau (như AWS Bedrock, Anthropic, Cohere).

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
`Không có pipeline rõ ràng trong tài liệu nguồn`
Thay vào đó là quy trình thiết lập biến và cấu hình model:
1. **Thiết lập quyền Bedrock**: Vào Console Bedrock -> Model Access -> Yêu cầu access Nova Pro và OSS 120B.
2. **Cấu hình Local `.env`**: Điền `OPENAI_API_KEY` của học viên (dành riêng cho tracing).
3. **Cấu hình Terraform Variables**: Copy `terraform.tfvars` và khai báo các thông số `aws_region`, `openai_api_key`, `alex_api_endpoint`, `alex_api_key`.
4. **Cấu hình Code Agent**: Cập nhật file [server.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/server.py) để trỏ đúng model ID `bedrock/us.amazon.nova-pro-v1:0` và region `us-east-1` (hoặc model OSS 120B ở `us-west-2`).

## 7. Techniques - Kỹ thuật sử dụng
- **Model Provider Abstraction - Trừu tượng hóa nhà cung cấp mô hình**:
  - Purpose (mục đích): Cho phép dễ dàng chuyển đổi qua lại giữa các mô hình (như từ OpenAI OSS sang Amazon Nova) bằng cách thay đổi chuỗi cấu hình mà không phải viết lại logic gọi API của Agent.
  - When to use (dùng khi nào): Khi xây dựng ứng dụng AI trong thực tế để phòng ngừa rủi ro một nhà cung cấp bị sập hoặc thay đổi chính sách/giá cả.
  - Trade-off (đánh đổi): Một số tính năng đặc thù của từng mô hình (như định dạng system prompt đặc biệt) có thể bị mất hoặc hoạt động không tối ưu khi đi qua lớp trừu tượng.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích file [server.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/server.py) (phần khởi tạo agent)
- **Thiết lập model**:
  - Sử dụng lớp `LitellmModel` để bọc model ID của Bedrock. Thiết lập các biến môi trường cho LiteLLM nhận diện region:
    ```python
    region = os.environ.get("BEDROCK_REGION", "us-west-2")
    os.environ["AWS_REGION_NAME"] = region  # LiteLLM bắt buộc dùng biến này
    os.environ["AWS_REGION"] = region
    os.environ["AWS_DEFAULT_REGION"] = region
    model_name = os.environ.get("RESEARCHER_MODEL", "bedrock/global.openai.gpt-oss-120b-1:0")
    model = LitellmModel(model=model_name)
    ```

### Phân tích file [tools.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/tools.py)
- **Tool `ingest_financial_document`**:
  - Khai báo decorator `@function_tool` để biến hàm Python thông thường thành một công cụ mà AI Agent có thể tự quyết định gọi.
  - Nhận tham số `topic` và `analysis` từ mô hình AI.
  - Đóng gói dữ liệu thành JSON và gọi hàm `ingest_with_retries(document)`.
  - Sử dụng thư viện `tenacity` để cấu hình retry logic (cơ chế thử lại):
    ```python
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def ingest_with_retries(document: Dict[str, Any]) -> Dict[str, Any]:
        return _ingest(document)
    ```
    *Ghi chú:* Cơ chế này cực kỳ quan trọng để xử lý lỗi timeout do khởi động lạnh (cold start) của SageMaker Serverless Endpoint ở Day 3.

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Sử dụng Amazon Nova Lite**
  - Pros: Chi phí rẻ, tốc độ xử lý nhanh.
  - Cons: Không đủ khả năng xử lý các tác vụ phức tạp như gọi công cụ (tool calling) hoặc tích hợp MCP server, dẫn đến Agent bị lỗi vòng lặp.
  - When to choose: Các tác vụ tóm tắt văn bản hoặc trả lời câu hỏi chatbot đơn giản.
- **Option 2: Sử dụng Amazon Nova Pro (Lựa chọn của dự án)**
  - Pros: Khả năng lập luận mạnh mẽ, hỗ trợ hoàn hảo cho tool calling và MCP server.
  - Cons: Chi phí token đắt hơn Nova Lite.
  - When to choose: (Recommended) Xây dựng các AI agent tự động cần gọi công cụ và xử lý logic phức tạp.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Lỗi gọi mô hình Bedrock do cấu hình sai region của LiteLLM.
  - Root cause: LiteLLM yêu cầu đặt chính xác biến môi trường `AWS_REGION_NAME` thay vì `AWS_REGION` truyền thống của AWS CLI/Boto3 để gọi Bedrock.
  - Symptom: Lỗi `ModelNotSupported` hoặc `ClientError: Parameter validation failed`.
  - Fix / prevention: Ghi đè cả 3 biến môi trường `AWS_REGION_NAME`, `AWS_REGION`, và `AWS_DEFAULT_REGION` trong mã nguồn Python trước khi khởi tạo `LitellmModel`.

## 11. Knowledge Extension - Kiến thức mở rộng
- Kỹ thuật retry logic với `tenacity` sử dụng cơ chế giãn cách lũy thừa (`wait_exponential`). Điều này có nghĩa là khoảng thời gian chờ giữa các lần thử lại sẽ tăng dần (ví dụ: 1s, 2s, 4s, 8s...) nhằm giúp hệ thống backend (như SageMaker serverless container đang khởi động lạnh) có đủ thời gian để sẵn sàng phục vụ, giảm tải yêu cầu dồn dập gây nghẽn cổ chai.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Mô hình OpenAI OSS chỉ có sẵn tại region `us-west-2` (Oregon).
2. Amazon Nova Pro được chọn thay thế do hỗ trợ tốt tool calling và MCP server.
3. `OPENAI_API_KEY` được dùng cho tính năng tracing (theo dõi vết) của OpenAI Agents SDK.
4. Thư viện `tenacity` cung cấp cơ chế retry tự động để chống lỗi khởi động lạnh của SageMaker.

### Self-check questions
1. Tại sao OpenAI Agents SDK lại yêu cầu cấu hình OpenAI API key mặc dù chúng ta gọi mô hình thông qua AWS Bedrock?
2. Ý nghĩa của decorator `@function_tool` trong file `tools.py` là gì?

### Flashcards
- Q: Biến môi trường nào LiteLLM yêu cầu để thiết lập region cho Bedrock?
  A: `AWS_REGION_NAME`.
- Q: Dòng mô hình Amazon Nova nào hỗ trợ đầy đủ cho các công cụ và MCP server?
  A: Amazon Nova Pro.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 85. Day 5 - Deploying AI Research Agents with Docker, ECR, and App Runner

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [85. Day 5 - Deploying AI Research Agents with Docker, ECR, and App Runner.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/85.%20Day%205%20-%20Deploying%20AI%20Research%20Agents%20with%20Docker,%20ECR,%20and%20App%20Runner.txt) - Đã dùng
- Code:
  - [Dockerfile](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/Dockerfile) - Đã dùng và phân tích
  - [deploy.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/deploy.py) - Đã dùng và phân tích
  - [main.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/4_researcher/main.tf) - Đã dùng và phân tích (bài học này liên quan đến chicken-and-egg problem)
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) và [day4_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day4_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Phân tích bài toán phụ thuộc chéo trong triển khai container lên đám mây (chicken-and-egg problem): Terraform không thể tạo App Runner/Lambda từ container image nếu image đó chưa tồn tại trên ECR, nhưng ECR repository lại được quản lý và tạo ra bởi chính Terraform.
- Giải pháp xử lý: Chạy Terraform apply có giới hạn bằng tùy chọn target để chỉ tạo ECR và IAM roles trước:
  `terraform apply -target=aws_ecr_repository.researcher -target=aws_iam_role.researcher_lambda_role`
- Giới thiệu cấu trúc của [Dockerfile](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/Dockerfile): Cài đặt Node, Playwright Chromium, trình quản lý gói `uv`, sao chép code và chạy server Uvicorn trên port 8000.
- Giải thích kịch bản triển khai [deploy.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/deploy.py): Lấy ECR repo URL từ Terraform outputs, build Docker image cho platform `linux/amd64`, thực hiện login docker và push image lên AWS ECR.
- Tự động hóa toàn bộ quy trình build và push giúp giảm sai sót thao tác thủ công.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu bản chất và cách giải quyết bài toán phụ thuộc chéo (chicken-and-egg problem) trong quản trị hạ tầng dạng code (IaC).
  - Nắm vững cấu trúc của một Dockerfile dành cho việc chạy AI Agent có MCP và Playwright browser.
  - Hiểu cách thức kịch bản Python tương tác với CLI để điều phối build và push Docker image.
- **Practical goals - mục tiêu thực hành**:
  - Thực hành chạy thành công lệnh `terraform apply` nhắm mục tiêu (targeted apply).
  - Đọc hiểu cấu trúc phân tầng (layers) của Dockerfile và vai trò của Playwright Chromium dependencies.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao cần cài đặt Node và Playwright Chromium bên trong container của Agent.
  - Tác dụng của tham số `--platform linux/amd64` khi build Docker image.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này sử dụng ECR repository và các IAM roles cấu hình tại Day 1 và Day 2 của tuần học, đồng thời chuẩn bị hạ tầng container để chạy mã nguồn tác tử của bài 84.

## 5. Core Theory - Lý thuyết cốt lõi
- **ECR (Elastic Container Registry)**: Dịch vụ lưu trữ registry các Docker container images được quản lý hoàn toàn bởi AWS, cho phép các dịch vụ compute (như Lambda, ECS, App Runner) kéo image về chạy một cách bảo mật.
- **Targeted Apply - Áp dụng nhắm mục tiêu**: Tính năng của Terraform cho phép chỉ chỉ định một số tài nguyên cụ thể được tạo ra hoặc cập nhật trước, bỏ qua các tài nguyên phụ thuộc khác trong file cấu hình.
- **Playwright Chromium**: Phiên bản trình duyệt Chromium mã nguồn mở được tối ưu hóa cho việc tự động hóa (automation) và cào dữ liệu (scraping) bằng code, yêu cầu cài đặt thêm các thư viện hệ thống (dependencies) của Linux để chạy headless (không giao diện).

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Quy trình giải quyết bài toán phụ thuộc chéo khi deploy container:
1. **Khởi tạo hạ tầng ECR**: Học viên chạy `terraform apply` nhắm vào các tài nguyên ECR và IAM role. ECR Repository rỗng được tạo ra trên AWS.
2. **Build Docker Image local**: Chạy script `deploy.py` để đóng gói mã nguồn Python và cài đặt Playwright Chromium headless.
3. **Push Image lên Cloud**: Script `deploy.py` lấy URL ECR, xác thực docker login qua AWS CLI, và thực hiện `docker push` để đẩy container image lên ECR repository vừa tạo.
4. **Deploy hoàn tất hạ tầng**: Chạy lại lệnh `terraform apply` toàn phần (không target) để tạo Lambda Function và các tài nguyên scheduler liên kết với container image đã có sẵn trên ECR.

## 7. Techniques - Kỹ thuật sử dụng
- **Docker Multi-Platform Build - Build Docker đa nền tảng**:
  - Purpose (mục đích): Đảm bảo container image chạy ổn định trên môi trường AWS compute (thường dùng kiến trúc x86_64 của Linux) bất kể máy local của nhà phát triển sử dụng chip gì (như Apple Silicon M1/M2/M3 kiến trúc ARM64).
  - When to use (dùng khi nào): Khi đóng gói container trên máy Mac M-series để deploy lên các dịch vụ đám mây của AWS, Azure, GCP.
  - Trade-off (đánh đổi): Quá trình build giả lập trên local bằng Docker Buildx có thể diễn ra lâu hơn do phải chuyển đổi tập lệnh kiến trúc chip.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích tệp tin [Dockerfile](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/Dockerfile)
- **Cài đặt môi trường hệ thống**:
  - Sử dụng base image Python 3.12: `FROM --platform=linux/amd64 python:3.12-slim`.
  - Cài đặt Node.js (cần thiết cho một số công cụ MCP):
    ```dockerfile
    RUN apt-get update && apt-get install -y curl gnupg && \
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
        apt-get install -y nodejs
    ```
  - Cài đặt playwright-mcp server globally: `RUN npm install -g playwright-mcp`.
  - Cài đặt các thư viện hệ thống bắt buộc của Linux để chạy trình duyệt Chromium headless:
    ```dockerfile
    RUN npx playwright install-deps chromium
    RUN npx playwright install chromium
    ```
  - Sao chép mã nguồn, cài đặt Python dependencies bằng `uv` và chạy Uvicorn server:
    ```dockerfile
    CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

### Phân tích kịch bản triển khai [deploy.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/deploy.py)
- **Truy xuất ECR URL**: Gọi lệnh `terraform output` từ thư mục `terraform/4_researcher` để lấy địa chỉ ECR Repo.
- **Xác thực docker login**:
  - Chạy lệnh: `aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {ecr_url}`.
- **Build và Push**:
  - Gọi sub-process thực thi lệnh: `docker build --platform linux/amd64 -t {ecr_url}:latest .`
  - Gọi lệnh: `docker push {ecr_url}:latest` để hoàn tất đẩy image lên Cloud.

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Viết script Bash/PowerShell để tự động build và push container**
  - Pros: Tốc độ thực thi nhanh, cú pháp shell tự nhiên cho các lệnh docker.
  - Cons: Phụ thuộc vào hệ điều hành (file `.sh` không chạy được trực tiếp trên Windows PowerShell và ngược lại).
  - When to choose: Các dự án chỉ chạy trên môi trường Linux CI/CD chuyên biệt.
- **Option 2: Viết kịch bản Python deploy.py (Lựa chọn của dự án)**
  - Pros: Độc lập nền tảng, chạy mượt mà trên cả Windows, Mac, Linux thông qua `uv run`. Dễ dàng tương tác cấu trúc hóa với API của AWS SDK.
  - Cons: Tốn thêm thời gian viết mã xử lý bắt lỗi và đọc output của subprocess.
  - When to choose: (Recommended) Các dự án học tập hoặc làm việc nhóm có các lập trình viên sử dụng đa dạng hệ điều hành khác nhau.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Lỗi `Exit code 255` hoặc container không thể khởi chạy trên AWS.
  - Root cause: Container image được build trên máy Mac M-series (ARM64) mà quên không cấu hình tham số `--platform linux/amd64`, dẫn đến việc AWS Lambda/App Runner không thể giải mã các tập lệnh của CPU.
  - Symptom: Lệnh apply Terraform thành công nhưng container bị crash loop ngay khi khởi động.
  - Fix / prevention: Đảm bảo có cờ `--platform linux/amd64` trong cả Dockerfile (ở dòng `FROM`) và trong lệnh build docker của file `deploy.py`.

## 11. Knowledge Extension - Kiến thức mở rộng
- Kỹ thuật **Docker layer caching** (bộ nhớ đệm phân tầng): Trong Dockerfile, các lệnh ít thay đổi (như cài đặt Node, Playwright Chromium dependencies) được đặt ở phía trên, các lệnh sao chép code thường xuyên thay đổi được đặt ở cuối cùng. Điều này giúp Docker tái sử dụng các layers cũ đã build, rút ngắn thời gian build từ 10 phút xuống còn vài giây cho các lần thay đổi code tiếp theo.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Bài toán chicken-and-egg được giải quyết bằng lệnh `terraform apply -target`.
2. Dockerfile cần cài đặt cả Node.js và các thư viện hệ thống của Chromium để chạy MCP.
3. Tham số `--platform linux/amd64` giúp tương thích tuyệt đối với máy chủ AWS.
4. Lệnh deploy image lên Cloud: `uv run deploy.py` từ thư mục `backend/researcher`.

### Self-check questions
1. Tại sao ECR repository cần phải được khởi tạo trước khi chạy lệnh deploy của docker?
2. Hãy phân tích các layer trong Dockerfile của Researcher và chỉ ra layer nào tốn nhiều thời gian build nhất.

### Flashcards
- Q: Lệnh của Terraform để chỉ tạo một tài nguyên cụ thể là gì?
  A: `terraform apply -target=tên_tài_nguyên`.
- Q: Trình duyệt headless nào được cài đặt để AI Agent duyệt web?
  A: Chromium (thông qua Playwright).

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 86. Day 5 - Testing End-to-End AI Agent Workflows from Research to Vector Storage

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [86. Day 5 - Testing End-to-End AI Agent Workflows from Research to Vector Storage.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/86.%20Day%205%20-%20Testing%20End-to-End%20AI%20Agent%20Workflows%20from%20Research%20to%20Vector%20Storage.txt) - Đã dùng
- Code:
  - [test_research.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/test_research.py) - Đã dùng và phân tích
  - [mcp_servers.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/mcp_servers.py) - Đã dùng và phân tích
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) và [day4_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day4_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Học viên thực thi lệnh `terraform apply` toàn phần (không target) sau khi đã push thành công image lên ECR để hoàn tất triển khai Researcher Lambda (sử dụng container image) và cấu hình Function URL.
- Thực hiện quy trình test E2E sạch sẽ: Đầu tiên, làm rỗng database bằng `uv run cleanup_s3vectors.py` trong folder `backend/ingest`.
- Kích hoạt chạy thử nghiệm tác tử nghiên cứu bằng script [test_research.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/test_research.py) trong folder `backend/researcher`.
- Tác tử tự động tìm kiếm chủ đề thị trường thịnh hành (trending topic) hoặc chủ đề được chỉ định, khởi tạo Playwright browser để cào tin tức, tóm tắt và tự động lưu vào S3 Vectors.
- Phân tích hiện tượng lỗi timeout (Bad Gateway 502) khi sử dụng mô hình yếu Nova Pro do nó lập luận kém hơn và đi vòng quanh duyệt web quá nhiều bước trước khi quyết định gọi tool. Lần chạy thứ hai thành công (mất khoảng 80 giây).
- Giới thiệu cách quan sát logs (trên CloudWatch Logs) và traces (trên OpenAI Platform Dashboard) để theo dõi chi tiết từng bước hoạt động của agent trong sản xuất.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu cách thức theo dõi vết (agent tracing) để kiểm toán hành vi của AI Agent.
  - Hiểu được sự ảnh hưởng của năng lực mô hình (model capability) đối với hiệu suất và thời gian thực thi của tác tử (ví dụ: Nova Pro vs OpenAI OSS/Claude).
  - Nắm được cách thức hoạt động của cơ chế MCP Server Stdio kết nối trong container.
- **Practical goals - mục tiêu thực hành**:
  - Chạy thành công lệnh kiểm thử E2E: Clean -> Research -> Search.
  - Đăng nhập OpenAI platform để trực quan hóa và đọc biểu đồ traces của Agent.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao Nova Pro đôi khi lại bị lỗi vượt quá số lượt tối đa (`Max turns exceeded`).
  - Cách thức Agent gọi các công cụ của MCP Playwright Server (navigate, click, snapshot).

## 4. Previous Context - Liên hệ với bài trước
- Bài học này là sự tích hợp hoàn chỉnh của Researcher Agent (bài 85) với API Gateway và Ingest Lambda (Day 4) để thực hiện chuỗi hành động lưu dữ liệu tự động.

## 5. Core Theory - Lý thuyết cốt lõi
- **Headless Browser - Trình duyệt không giao diện**: Trình duyệt web (như Chromium) chạy trên môi trường máy chủ Linux không có màn hình hiển thị, được điều khiển hoàn toàn bằng code để cào dữ liệu hoặc chụp ảnh màn hình.
- **Trace Chart - Biểu đồ vết truy vết**: Biểu đồ phân cấp thể hiện thứ tự thời gian gọi và phản hồi của các tiến trình con bên trong Agent (gọi mô hình, gọi tool, trả kết quả).
- **Max Turns - Lượt chạy tối đa**: Hạn mức số vòng lặp suy nghĩ và hành động (thought-action loop) tối đa được cấu hình cho Agent trong một phiên chạy để ngăn chặn Agent rơi vào vòng lặp vô hạn gây tốn chi phí.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng thực thi chi tiết của Researcher Agent khi nhận yêu cầu:
1. **Khởi tạo**: Nhận request từ `test_research.py`, setup biến môi trường Bedrock.
2. **Kích hoạt MCP**: Spawn tiến trình phụ chạy Playwright MCP Server (`playwright-mcp`).
3. **Thought Loop (Vòng lặp suy nghĩ)**:
   - Agent (Bedrock) quyết định công cụ cần dùng -> gọi tool `browser_navigate` của MCP để truy cập trang tin tài chính.
   - MCP trả kết quả HTML/Text về cho Agent.
   - Agent phân tích, nếu cần click thêm -> gọi `browser_click` hoặc lấy toàn bộ nội dung qua `browser_snapshot`.
4. **Ingestion (Nạp dữ liệu)**:
   - Sau khi tổng hợp đủ thông tin, Agent quyết định gọi tool `ingest_financial_document` (định nghĩa trong `tools.py`).
   - Tool thực hiện gửi HTTP POST request chứa bài phân tích sang Ingest API Gateway của Day 4.
5. **Dọn dẹp**: Giải phóng kết nối MCP Playwright và trả về bài báo cáo nghiên cứu cho client.

## 7. Techniques - Kỹ thuật sử dụng
- **Agent Action Tracing - Truy vết hành động tác tử**:
  - Purpose (mục đích): Giám sát chính xác từng hành vi của Agent trên môi trường production, hỗ trợ debug khi Agent hành động sai hoặc lặp vô hạn.
  - When to use (dùng khi nào): Bắt buộc trong mọi ứng dụng Agent chạy tự động không có con người giám sát (autonomous agents).
  - Trade-off (đánh đổi): Làm tăng độ trễ mạng do phải gửi dữ liệu log trace về máy chủ giám sát.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích file [test_research.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/test_research.py)
- **Tự động quét URL**: Đọc file state của Terraform `/terraform/4_researcher/terraform.tfstate` để tự động trích xuất public URL của lambda function (`researcher_url`), giúp học viên không phải copy-paste thủ công.
- **Gửi yêu cầu kiểm tra**:
  - Gửi yêu cầu GET tới `/health` để kiểm tra độ khỏe mạnh của service.
  - Gửi yêu cầu POST tới `/research` truyền body JSON chứa `topic` cần nghiên cứu (mặc định hoặc từ tham số dòng lệnh CLI).
  - In bài báo cáo Markdown trả về từ Agent ra màn hình terminal.

### Phân tích file [mcp_servers.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/researcher/mcp_servers.py)
- **Khởi tạo Playwright MCP**:
  - Xây dựng arguments khởi chạy: `--headless`, `--isolated`, `--no-sandbox`, `--user-agent`.
  - Quét tìm đường dẫn file thực thi Chrome trong container bằng `glob.glob("/ms-playwright/chromium-*/chrome-linux*/chrome")` để chỉ định chính xác cho Playwright, tránh lỗi không tìm thấy trình duyệt trên môi trường Linux của AWS Lambda.
  - Trả về `MCPServerStdio` bọc tham số command `playwright-mcp` để OpenAI Agents SDK quản lý giao tiếp qua Stdio.

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Thiết lập Max Turns thấp (ví dụ: max_turns = 5)**
  - Pros: Tiết kiệm chi phí token Bedrock tối đa, Agent kết thúc nhanh.
  - Cons: Agent dễ bị thất bại nửa chừng khi chưa kịp hoàn thành việc duyệt web và gọi tool nạp dữ liệu.
  - When to choose: Các tác vụ tìm kiếm cực kỳ đơn giản chỉ cần truy cập 1 trang web.
- **Option 2: Thiết lập Max Turns cao (ví dụ: max_turns = 15 hoặc 20 - Lựa chọn của dự án)**
  - Pros: Cho phép các dòng mô hình yếu hơn (như Nova Pro) có đủ số lượt lập luận và sửa sai để hoàn thành tác vụ.
  - Cons: Chi phí token cao hơn, thời gian chạy lâu hơn, có thể bị timeout 3 phút của Lambda nếu rơi vào vòng lặp lỗi.
  - When to choose: (Recommended) Các tác vụ cào web phức tạp, yêu cầu đi qua nhiều bước click và phân tích.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Agent bị lỗi `Max turns exceeded` hoặc chạy quá lâu rồi chết.
  - Root cause: Mô hình Nova Pro lập luận yếu hơn Claude/GPT, dễ bị lạc lối trong cấu trúc trang web phức tạp hoặc prompt hệ thống quá lỏng lẻo không giới hạn phạm vi duyệt web.
  - Symptom: Lọc log CloudWatch thấy lỗi vượt quá số lượt hoặc client nhận lỗi Timeout 504.
  - Fix / prevention: Tinh chỉnh lại prompt hệ thống trong `context.py` để ra lệnh rõ ràng cho Agent: "chỉ được phép truy cập tối đa 1 hoặc 2 trang web và phải gọi tool ingest ngay sau khi có thông tin chính".

## 11. Knowledge Extension - Kiến thức mở rộng
- OpenAI Agents SDK hỗ trợ cơ chế Run Hooks (`on_tool_start`, `on_tool_end`) cho phép lập trình viên can thiệp vào vòng đời gọi công cụ. Trong file `server.py`, chúng ta cấu hình lớp `ResearchLoggingHooks` để in log trực quan ra CloudWatch mỗi khi Agent bắt đầu hoặc kết thúc gọi một công cụ MCP, giúp tăng khả năng quan sát trạng thái của container.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Deploy hạ tầng toàn phần bằng lệnh `terraform apply` không target.
2. Script `cleanup_s3vectors.py` xóa sạch database để chuẩn bị môi trường test E2E.
3. Lệnh test research: `uv run test_research.py "topic_cần_tìm"` từ thư mục `backend/researcher`.
4. OpenAI Traces Dashboard là nơi tốt nhất để xem các bước gọi tool MCP của Agent.

### Self-check questions
1. Tại sao Researcher Agent cần sử dụng Playwright browser ở chế độ headless?
2. Hãy mô tả hiện tượng xảy ra khi Agent bị quá hạn mức số lượt chạy (max turns).

### Flashcards
- Q: Nền tảng nào được dùng để trực quan hóa sơ đồ gọi tool của OpenAI Agents SDK?
  A: OpenAI Platform Traces.
- Q: Lệnh kiểm tra sức khỏe của service Researcher là gì?
  A: Gửi GET request tới `/health`.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 87. Day 5 - Automating AI Agent Workflows with AWS EventBridge Scheduling

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [87. Day 5 - Automating AI Agent Workflows with AWS EventBridge Scheduling.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/87.%20Day%205%20-%20Automating%20AI%20Agent%20Workflows%20with%20AWS%20EventBridge%20Scheduling.txt) - Đã dùng
- Slide: [Production W3D5.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D5.pdf) - Đã dùng (đối chiếu nội dung qua transcript)
- Code:
  - [main.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/4_researcher/main.tf) - Đã dùng và phân tích (phần cấu hình scheduler và scheduler Lambda)
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) và [day4_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day4_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Kích hoạt tính năng tự động hóa đường ống nghiên cứu dữ liệu bằng cách thiết lập biến `scheduler_enabled = true` trong tệp `terraform.tfvars` ở `terraform/4_researcher` và chạy `terraform apply`.
- Phân tích chi tiết giới hạn của AWS EventBridge: EventBridge Scheduler có giới hạn thời gian chờ phản hồi tối đa (timeout limit) là 5 giây đối với các API Destinations (đầu gọi HTTP). Trong khi đó, API nghiên cứu `/research/auto` của Researcher Agent có thể mất từ 30 đến 90 giây để hoàn thành.
- Giải pháp kiến trúc vượt trội: Sử dụng một AWS Lambda function làm trung gian điều phối (`alex-researcher-scheduler`). EventBridge Scheduler kích hoạt Lambda Scheduler này (nhanh chóng trong <1 giây).
- Lambda Scheduler sau đó gửi yêu cầu HTTP đến public Function URL của Researcher Agent và giữ kết nối chờ đợi phản hồi trong tối đa 3 phút (timeout của Lambda Scheduler được cấu hình là 180 giây).
- Kỹ thuật rút ngắn chu kỳ scheduler từ 2 giờ xuống còn 10 phút (`rate(10 minutes)`) để phục vụ việc kiểm thử nhanh trên môi trường phát triển và kiểm tra log CloudWatch.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu các giới hạn kỹ thuật về thời gian chờ (timeout constraints) của dịch vụ AWS EventBridge.
  - Hiểu kiến trúc điều phối bất đồng bộ sử dụng Lambda Scheduler làm proxy trung gian.
  - Nắm được cách giám sát các tác vụ chạy ngầm (cron jobs) bằng CloudWatch logs.
- **Practical goals - mục tiêu thực hành**:
  - Kích hoạt thành công scheduler bằng Terraform.
  - Cấu hình và thay đổi chu kỳ kích hoạt của EventBridge Scheduler.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao EventBridge Scheduler không thể gọi trực tiếp public Function URL của Researcher Agent mà phải qua Lambda trung gian.
  - Cách thức cấu hình biến môi trường `APP_RUNNER_URL` (hoặc Function URL) cho Lambda Scheduler.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này tự động hóa toàn bộ quy trình kiểm thử tay đã thực hiện ở bài 86 thành một quy trình chạy ngầm lặp lại liên tục trên môi trường đám mây AWS.

## 5. Core Theory - Lý thuyết cốt lõi
- **EventBridge Scheduler**: Dịch vụ quản lý tác vụ lịch trình được quản lý hoàn toàn bởi AWS, cho phép tạo hàng triệu lịch trình (cron hoặc rate) để kích hoạt các dịch vụ AWS khác.
- **Proxy Lambda Pattern - Mô hình Lambda trung gian**: Thiết kế sử dụng một Lambda function siêu nhẹ làm cầu nối trung gian giữa một dịch vụ có timeout ngắn (như EventBridge - 5s) và một dịch vụ xử lý lâu dài (như Agent - vài phút).
- **Function URL - Đường dẫn hàm**: Tính năng của AWS Lambda cung cấp một endpoint HTTP(S) duy nhất dành riêng cho một hàm Lambda cụ thể, cho phép kích hoạt trực tiếp hàm đó từ trình duyệt hoặc client mà không cần đi qua API Gateway.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng hoạt động của đường ống nghiên cứu tự động:
1. **Trigger (Kích hoạt)**: EventBridge Scheduler kích hoạt định kỳ mỗi 2 giờ (hoặc 10 phút khi test) dựa trên quy tắc `alex-research-schedule`.
2. **Proxy Call (Gọi trung gian)**: EventBridge Scheduler giả lập vai trò IAM và invoke (kích hoạt) Lambda `alex-researcher-scheduler`.
3. **Agent Request (Gọi tác tử)**: 
   - Lambda Scheduler nhận sự kiện, đọc biến môi trường `APP_RUNNER_URL` (Function URL của Researcher).
   - Gửi yêu cầu HTTP POST tới đường dẫn `{Function_URL}/research/auto` và giữ kết nối chờ đợi.
4. **Execution (Thực thi)**: 
   - Researcher Lambda thức dậy, chạy container, khởi động Playwright cào web và gọi Bedrock lưu kết quả.
   - Trả về JSON thông báo thành công cho Lambda Scheduler.
5. **Complete (Hoàn thành)**: Lambda Scheduler nhận phản hồi thành công và kết thúc lượt chạy.

## 7. Techniques - Kỹ thuật sử dụng
- **Timeout Mitigation via Lambda Proxy - Giảm thiểu lỗi timeout qua Lambda trung gian**:
  - Purpose (mục đích): Vượt qua giới hạn thời gian chờ 5 giây nghiêm ngặt của EventBridge khi gọi các API xử lý lâu dài của AI Agent.
  - When to use (dùng khi nào): Khi cần lên lịch trình tự động gọi các tác vụ AI, ETL hoặc sinh báo cáo mất nhiều thời gian xử lý.
  - Trade-off (đánh đổi): Tốn thêm chi phí chạy cho một Lambda Scheduler trung gian (tuy nhiên chi phí này rất nhỏ do Lambda scheduler chỉ chạy chờ đợi và tiêu tốn ít tài nguyên RAM).

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích cấu trúc hạ tầng Scheduler trong [main.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/4_researcher/main.tf)

- **Định cấu hình Scheduler Lambda `aws_lambda_function.scheduler_lambda`**:
  - Chỉ định file zip code: `${path.module}/../../backend/scheduler/lambda_function.zip`.
  - Handler: `lambda_function.handler`. Timeout: 180s (3 phút).
  - Cấu hình URL đích qua biến môi trường:
    ```hcl
    environment {
      variables = {
        APP_RUNNER_URL = trimsuffix(aws_lambda_function_url.researcher[0].function_url, "/")
      }
    }
    ```

- **Định cấu hình EventBridge Schedule `aws_scheduler_schedule.research_schedule`**:
  - Thiết lập chu kỳ chạy: `schedule_expression = "rate(2 hours)"`.
  - Chỉ định target là ARN của Lambda Scheduler:
    ```hcl
    target {
      arn      = aws_lambda_function.scheduler_lambda[0].arn
      role_arn = aws_iam_role.eventbridge_role[0].arn
    }
    ```

- **Phân quyền cho phép EventBridge gọi Lambda `aws_lambda_permission.allow_eventbridge`**:
  - Cấp quyền `lambda:InvokeFunction` cho principal `scheduler.amazonaws.com` với source ARN trùng khớp với schedule vừa tạo.

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: EventBridge Scheduler gọi trực tiếp API Gateway / Function URL của Agent**
  - Pros: Tiết kiệm chi phí và tinh giản hạ tầng (không cần viết Lambda Scheduler trung gian).
  - Cons: Sẽ liên tục gặp lỗi Timeout 504 và EventBridge sẽ kích hoạt cơ chế retry liên tục gây quá tải và tốn chi phí token vô ích, vì Agent mất tối thiểu 20-30s để chạy xong.
  - When to choose: Chỉ dùng khi API đích phản hồi ngay lập tức và xử lý bất đồng bộ hoàn toàn ở backend (fire-and-forget).
- **Option 2: Sử dụng Lambda Scheduler trung gian làm Proxy (Lựa chọn của dự án)**
  - Pros: Cho phép chờ đợi phản hồi đồng bộ lên tới 3 hoặc 15 phút, ghi nhận chính xác trạng thái thành công/thất bại của lượt chạy Agent.
  - Cons: Phải duy trì thêm một file zip code Lambda và cấu hình tài nguyên Terraform đi kèm.
  - When to choose: (Recommended) Các tác vụ AI Agent hoặc crawl dữ liệu chạy đồng bộ cần theo dõi trạng thái.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Scheduler chạy nhưng Agent không lưu được dữ liệu và báo lỗi timeout 3 phút.
  - Root cause: Lambda Scheduler trung gian chỉ được cấu hình timeout mặc định là 3 giây hoặc 15 giây, trong khi Agent chạy mất hơn 1 phút, dẫn đến Lambda Scheduler bị chết trước khi Agent kịp phản hồi.
  - Symptom: Log CloudWatch của Scheduler báo lỗi timeout, nhưng log của Agent vẫn hiển thị đang chạy hoặc đã chạy xong sau đó.
  - Fix / prevention: Thiết lập thuộc tính `timeout` của Lambda Scheduler trong Terraform lên tối thiểu 180 giây (3 phút) để đảm bảo có đủ thời gian chờ đợi Agent.

## 11. Knowledge Extension - Kiến thức mở rộng
- AWS EventBridge Scheduler hỗ trợ tính năng cửa sổ thời gian linh hoạt (`flexible_time_window`). Trong cấu hình của dự án, chúng ta tắt tính năng này (`mode = "OFF"`) để bắt buộc tác vụ chạy chính xác tại thời điểm định kỳ. Trong các dự án thực tế quy mô lớn, việc bật cửa sổ linh hoạt (ví dụ: trong vòng 15 phút) giúp AWS phân bổ tải đều trên hạ tầng đám mây toàn cầu, giảm thiểu hiện tượng nghẽn cổ chai.

## 12. Study Pack - Gói ôn tập
### Must remember
1. EventBridge có giới hạn thời gian chờ phản hồi tối đa là 5 giây.
2. Lambda Scheduler `alex-researcher-scheduler` làm nhiệm vụ proxy trung gian chờ phản hồi tối đa 3 phút.
3. Kích hoạt scheduler bằng cách set `scheduler_enabled = true` trong `terraform.tfvars`.
4. Xem log của scheduler bằng lệnh: `aws logs tail /aws/lambda/alex-research-scheduler --follow`.

### Self-check questions
1. Tại sao EventBridge Scheduler lại bị giới hạn timeout 5s và kiến trúc của Alex giải quyết nó ra sao?
2. Làm thế nào để cấu hình lại chu kỳ chạy của Agent từ 2 giờ xuống 10 phút bằng Terraform?

### Flashcards
- Q: Thời gian timeout tối đa của EventBridge Scheduler đối với API Destinations là bao nhiêu?
  A: 5 giây.
- Q: Tên hàm Lambda làm trung gian kích hoạt Agent trong dự án là gì?
  A: `alex-researcher-scheduler`.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 88. Day 5 - Week 3 Wrap-Up - Assignment Options & Production AI Next Steps

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [88. Day 5 - Week 3 Wrap-Up - Assignment Options & Production AI Next Steps.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/88.%20Day%205%20-%20Week%203%20Wrap-Up%20-%20Assignment%20Options%20&%20Production%20AI%20Next%20Steps.txt) - Đã dùng
- Slide: [Production W3D5.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D5.pdf) - Đã dùng (đối chiếu nội dung qua transcript)
- Code: Buổi học này không có code được cung cấp/cấu hình thêm (đây là bài tổng kết và định hướng bài tập)
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) và [day4_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day4_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Tổng kết tuần học thứ 3 của khóa học, đánh dấu việc học viên đã đi được 75% chặng đường dẫn tới chuyên môn triển khai AI trong sản xuất (production AI expertise).
- Giới thiệu bài tập lớn cuối tuần 3 (Week 3 Assignment) với 3 hướng phát triển mở rộng hệ thống RAG Ingestion Pipeline:
  - Hướng 1: AI Agent nâng cao (Polygon API, context engineering, to-do list tools).
  - Hướng 2: Platform Engineering & DevOps (SQS task queue, auto retry logic).
  - Hướng 3: Data Engineering (chuẩn hóa schema, Supabase integration).
- Nhấn mạnh nguyên tắc học tập cốt lõi: "Cách tốt nhất để học là tự tay xây dựng (build yourself), chứ không chỉ là nghe giảng hay xem code".
- Hướng dẫn quy trình đóng góp bài làm của học viên vào thư mục đóng góp cộng đồng (community contributions) của repository qua GitHub PR.
- Hướng dẫn quy trình dọn dẹp hạ tầng (cost cleanup) bảo mật bằng cách tắt scheduler (`scheduler_enabled = false`) hoặc chạy lệnh `terraform destroy` để tránh phát sinh chi phí AWS ngoài ý muốn vào cuối tuần.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Nắm được các hướng đi phát triển chuyên sâu cho một kỹ sư AI: AI Agent, Platform, Data.
  - Hiểu cách thức quản lý chi phí AWS an toàn khi kết thúc một chu kỳ phát triển.
  - Hiểu giá trị của việc đóng góp cộng đồng trong quy trình làm việc nguồn mở.
- **Practical goals - mục tiêu thực hành**:
  - Thực hiện thành công việc tắt/bật scheduler hoặc chạy `terraform destroy` dọn dẹp tài nguyên.
- **What learner should be able to explain - người học cần giải thích được**:
  - Ba hướng lựa chọn của bài tập tuần 3 là gì và mục tiêu của từng hướng.
  - Tại sao cần dọn dẹp hạ tầng AWS khi không làm việc.

## 4. Previous Context - Liên hệ với bài trước
- Bài học tổng kết toàn bộ chặng đường từ Day 1 (Azure/GCP setup) đến Day 5 (AWS Ingest/Researcher E2E), chuẩn bị kiến thức nền tảng vững chắc để tuần 4 bước vào xây dựng hệ thống multi-agent phức tạp hơn.

## 5. Core Theory - Lý thuyết cốt lõi
- **Context Engineering - Kỹ thuật ngữ cảnh**: Phương pháp tối ưu hóa toàn bộ lượng thông tin đưa vào context window của LLM (gồm system prompt, data retrieve, guidelines, history) để định hướng Agent hành động chính xác nhất.
- **Task Queueing - Xếp hàng nhiệm vụ**: Cơ chế đưa các yêu cầu xử lý vào một hàng đợi (như AWS SQS) để xử lý tuần tự và bất đồng bộ, giúp tăng tính chịu tải và khả năng tự phục hồi (resilience) của hệ thống khi có lỗi.
- **Cost Cleanup - Dọn dẹp chi phí**: Quy trình rà soát và xóa bỏ các tài nguyên đám mây nhạy cảm về chi phí (như VM instances, databases running, schedulers active) để tối ưu hóa ngân sách dự án.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
`Không có pipeline rõ ràng trong tài liệu nguồn`
Thay vào đó là quy trình dọn dẹp chi phí AWS cuối tuần:
1. **Kiểm tra billing**: Truy cập AWS Billing Console để kiểm tra lượng credit tiêu thụ.
2. **Tắt Scheduler**: Đặt `scheduler_enabled = false` trong `terraform.tfvars` ở folder `terraform/4_researcher`.
3. **Apply hạ tầng**: Chạy `terraform apply` để gỡ bỏ EventBridge Scheduler và Lambda Scheduler.
4. **Hủy tài nguyên (Nếu cần)**: Chạy `terraform destroy` trong các thư mục từ guide 2 đến 4 để xóa bỏ hoàn toàn Endpoint và Lambda để tránh tính phí rác.

## 7. Techniques - Kỹ thuật sử dụng
- **Cloud Cost Monitoring - Giám sát chi phí đám mây**:
  - Purpose (mục đích): Tránh các hóa đơn AWS khổng lồ ngoài ý muốn do quên tắt các tài nguyên chạy ngầm.
  - When to use (dùng khi nào): Bắt buộc áp dụng định kỳ sau mỗi ngày học hoặc kết thúc một dự án thử nghiệm.
  - Trade-off (đánh đổi): Phải tốn công sức khởi tạo lại hạ tầng (terraform apply) vào tuần học tiếp theo.

## 8. Code Walkthrough - Phân tích code nếu có
`Buổi học này không có code được cung cấp/cấu hình thêm`

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Hướng 1 - Đi sâu vào Agentic AI (MCP & Context)**
  - Pros: Tăng tính thông minh và độ chính xác của Researcher Agent, học được cách viết tool và MCP.
  - Cons: Không cải thiện độ bền bỉ hạ tầng hoặc cấu trúc cơ sở dữ liệu.
  - When to choose: Phù hợp cho những ai muốn định hướng làm AI Agent Engineer chuyên sâu.
- **Option 2: Hướng 2 - Đi sâu vào Platform Engineering (SQS & Retry)**
  - Pros: Giúp hệ thống đạt tiêu chuẩn enterprise thực thụ, chịu được tải lớn và tự phục hồi khi cào web lỗi.
  - Cons: Logic lập luận của Agent không thay đổi.
  - When to choose: Phù hợp cho những ai muốn định hướng làm Cloud/DevOps AI Engineer.
- **Option 3: Hướng 3 - Đi sâu vào Data Engineering (Supabase & Schema)**
  - Pros: Học được cách thiết kế schema cơ sở dữ liệu chuẩn và tích hợp dịch vụ DB bên ngoài.
  - Cons: Đòi hỏi đăng ký thêm dịch vụ ngoài (Supabase).
  - When to choose: Phù hợp cho những ai muốn định hướng làm AI Data Engineer.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Bị trừ tiền oan do quên tắt EventBridge Scheduler.
  - Root cause: Học viên cấu hình scheduler chạy tự động mỗi 2 giờ nhưng không tắt đi khi nghỉ cuối tuần, dẫn đến Lambda và Bedrock liên tục được gọi và tính phí.
  - Symptom: Tài khoản AWS phát sinh chi phí đều đặn hàng giờ.
  - Fix / prevention: Chạy `terraform destroy` hoặc đổi cấu hình `scheduler_enabled = false` và apply lại trước khi dừng làm việc.

## 11. Knowledge Extension - Kiến thức mở rộng
- Hướng đi tích hợp SQS (Simple Queue Service) sử dụng mô hình DLQ (Dead Letter Queue). Khi một nhiệm vụ nạp tài liệu bị lỗi quá 3 lần, thay vì bị mất hoàn toàn, nó sẽ tự động được chuyển vào DLQ để kỹ sư hệ thống có thể kiểm tra thủ công và tìm nguyên nhân, đảm bảo tính toàn vẹn dữ liệu cho doanh nghiệp.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Đạt 75% chặng đường hoàn thành khóa học khi kết thúc tuần 3.
2. Bài tập tuần 3 có 3 hướng lựa chọn: AI Agent, Platform, Data.
3. Cách tốt nhất để học là tự tay xây dựng dự án.
4. Tắt Scheduler bằng cách đặt `scheduler_enabled = false` và chạy `terraform apply`.
5. Đóng góp bài làm vào repository thông qua GitHub Pull Request.

### Self-check questions
1. Hãy liệt kê các công cụ cần thiết cho từng hướng đi của bài tập lớn tuần 3.
2. Các bước thực hiện để gỡ bỏ scheduler tạm thời nhằm tránh tốn chi phí AWS là gì?

### Flashcards
- Q: Ba hướng phát triển bài tập tuần 3 là gì?
  A: AI Agent, Platform/DevOps, Data Engineering.
- Q: Lệnh hủy toàn bộ tài nguyên Terraform trong một thư mục là gì?
  A: `terraform destroy`.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.
