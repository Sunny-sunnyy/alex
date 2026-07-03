# 79. Day 4 - Building Vector Data Pipelines with SageMaker and S3 for AI Memory

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [79. Day 4 - Building Vector Data Pipelines with SageMaker and S3 for AI Memory.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/79.%20Day%204%20-%20Building%20Vector%20Data%20Pipelines%20with%20SageMaker%20and%20S3%20for%20AI%20Memory.txt) - Đã dùng
- Slide: [Production W3D4.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D4.pdf) - Đã dùng (đối chiếu nội dung qua transcript)
- Code: Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này (đây là bài lý thuyết tổng quan kiến trúc)
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Khóa học bước sang Day 4 với trọng tâm xây dựng đường ống nạp dữ liệu vector (vector data ingestion pipeline) nhằm cung cấp bộ nhớ dài hạn về thông tin tài chính cho ứng dụng capstone Alex.
- S3 Vectors được giới thiệu là giải pháp lưu trữ vector bản địa (native vector storage) mới của AWS, giúp giảm cost (chi phí) vận hành tới 90% so với việc duy trì cụm OpenSearch Serverless đắt đỏ.
- Trình bày bức tranh kiến trúc RAG hoàn chỉnh của Researcher Agent: Scheduler Lambda thức dậy mỗi 2 giờ, kích hoạt Researcher Agent chạy dưới dạng container trên App Runner.
- Researcher Agent sử dụng Playwright MCP Server để duyệt web thu thập thông tin tài chính, dùng Bedrock (Nova Pro) để tóm tắt văn bản, sau đó chuyển kết quả cho Ingest Lambda.
- Ingest Lambda đóng vai trò trung gian nhận văn bản, gọi SageMaker Endpoint để tạo vector embedding và ghi trực tiếp vào S3 Vectors.
- Tác vụ trọng tâm của Day 4 được giới hạn ở việc xây dựng Ingest Lambda, cấu hình API Gateway bảo mật và tích hợp với S3 Vectors cùng SageMaker Endpoint.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Nắm rõ kiến trúc tổng thể của hệ thống nạp dữ liệu RAG (RAG Ingestion Pipeline) trong ứng dụng Alex.
  - Phân tích được sự khác biệt về chi phí vận hành và hạ tầng giữa S3 Vectors và OpenSearch Serverless.
  - Hiểu cách thức hoạt động của mô hình cộng tác giữa EventBridge, Lambda, App Runner, Bedrock và SageMaker.
- **Practical goals - mục tiêu thực hành**:
  - Hình dung rõ ràng luồng dữ liệu di chuyển từ internet (qua Researcher Agent) đến kho lưu trữ vector (S3 Vectors).
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao S3 Vectors lại mang lại hiệu quả kinh tế vượt trội (tiết kiệm 90% chi phí) so với OpenSearch Serverless.
  - Vai trò của SageMaker Endpoint trong vai trò là "bộ chuyển đổi ngữ nghĩa" (semantic converter) của đường ống.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này liên kết trực tiếp với Day 3, nơi học viên đã triển khai thành công SageMaker Serverless Endpoint chạy mô hình nhúng `all-MiniLM-L6-v2`. Day 4 sẽ sử dụng endpoint này để biến đổi văn bản thu thập được thành các vector số thực 384 chiều trước khi lưu trữ.

## 5. Core Theory - Lý thuyết cốt lõi
- **S3 Vectors - Lưu trữ vector S3**: Giải pháp lưu trữ dữ liệu vector trực tiếp trên nền tảng S3 của AWS, được thiết kế để tối ưu hóa cost (chi phí) cho các ứng dụng RAG quy mô nhỏ và vừa nhờ cơ chế scale-to-zero (co giãn về 0 khi không hoạt động) thực sự.
- **Ingestion pipeline - Đường ống nạp dữ liệu**: Quy trình tự động thu thập thông tin thô, trích xuất văn bản, chuyển đổi ngữ nghĩa sang vector số và lưu trữ vào cơ sở dữ liệu vector.
- **Semantic retrieval - Truy xuất theo ngữ nghĩa**: Kỹ thuật tìm kiếm và truy xuất thông tin dựa trên ý nghĩa ngữ cảnh của câu thay vì chỉ dựa vào khớp chính xác từ khóa (`exact keyword match`).

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng hoạt động tổng thể của RAG Ingestion Pipeline trong Alex:
1. **Input**: Sự kiện kích hoạt định kỳ từ EventBridge Scheduler (mỗi 2 giờ).
2. **Processing steps**:
   - EventBridge kích hoạt Lambda Scheduler.
   - Lambda Scheduler gọi API endpoint của Researcher Agent (chạy trên App Runner).
   - Researcher Agent khởi chạy container, kích hoạt Playwright MCP Server để duyệt web và crawl thông tin thị trường.
   - Researcher Agent gửi văn bản crawl được tới AWS Bedrock (Nova Pro) để thực hiện phân tích và tóm tắt.
   - Văn bản tóm tắt được gửi tới API Gateway của Ingest Lambda.
   - Ingest Lambda nhận văn bản, gọi SageMaker Endpoint để tạo vector embedding 384 chiều.
   - Ingest Lambda thực thi API ghi vector vào S3 Vectors bucket.
3. **Output**: Vector embedding cùng văn bản gốc và metadata được lập chỉ mục (indexed) trong S3 Vectors bucket.

## 7. Techniques - Kỹ thuật sử dụng
- **Cost-effective Vector Storage - Lưu trữ vector tối ưu chi phí**:
  - Purpose (mục đích): Giảm thiểu tối đa chi phí duy trì hạ tầng cơ sở dữ liệu vector trong môi trường đám mây.
  - When to use (dùng khi nào): Khi xây dựng các ứng dụng AI RAG trong giai đoạn phát triển, thử nghiệm (dev/test environment) hoặc các dự án startup có ngân sách hạn chế.
  - Trade-off (đánh đổi): Tốc độ truy vấn của S3 Vectors có thể chậm hơn một chút so với cụm OpenSearch always-on (luôn hoạt động) do phụ thuộc vào hạ tầng lưu trữ đối tượng S3.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Sử dụng OpenSearch Serverless**
  - Pros: Hiệu năng cao, độ trễ thấp, hỗ trợ nhiều thuật toán tìm kiếm nâng cao và tìm kiếm kết hợp (hybrid search).
  - Cons: Chi phí cố định rất cao (~$200-$300/tháng), không phù hợp cho môi trường học tập hoặc tải thấp.
  - When to choose: Các hệ thống doanh nghiệp lớn có lượng truy cập cao và yêu cầu thời gian phản hồi cực nhanh.
- **Option 2: Sử dụng S3 Vectors (Lựa chọn của dự án)**
  - Pros: Chi phí cực kỳ rẻ (~$20-$30/tháng), không phát sinh chi phí khi không có truy vấn, cấu hình đơn giản trực tiếp trên S3 Console.
  - Cons: Là dịch vụ mới (2025), các tính năng nâng cao về phân tích và tối ưu hóa index chưa phong phú như OpenSearch.
  - When to choose: (Recommended) Các dự án capstone, MVP, hoặc ứng dụng có lượng dữ liệu vừa phải cần tối ưu cost (chi phí).

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Phát sinh hóa đơn AWS ngoài ý muốn.
  - Root cause: Học viên sử dụng cấu trúc OpenSearch cũ hoặc để các dịch vụ always-on (như rds instances, app runner instances không cấu hình giới hạn) chạy liên tục mà không dọn dẹp.
  - Symptom: Chi phí AWS tăng vọt trong AWS Cost Explorer.
  - Fix / prevention: Ưu tiên sử dụng các dịch vụ serverless thực sự như S3 Vectors và thiết lập AWS Budgets để nhận cảnh báo sớm khi chi phí vượt ngưỡng.

## 11. Knowledge Extension - Kiến thức mở rộng
- S3 Vectors hoạt động tách biệt hoàn toàn với API S3 truyền thống bằng cách sử dụng endpoint và client SDK riêng (`s3vectors`). Điều này giúp AWS tối ưu hóa tài nguyên tính toán để xử lý các thuật toán tìm kiếm lân cận gần nhất (Nearest Neighbor) ngay trên tầng lưu trữ vật lý của S3 mà không cần tải dữ liệu về máy chủ trung gian.

## 12. Study Pack - Gói ôn tập
### Must remember
1. S3 Vectors là giải pháp native vector storage của AWS giúp giảm 90% chi phí so với OpenSearch.
2. Ingestion pipeline của Alex tự động hóa việc crawl dữ liệu, sinh vector và lưu trữ vào S3.
3. Researcher Agent chạy độc lập trên App Runner và được kích hoạt bởi EventBridge mỗi 2 giờ.
4. SageMaker Endpoint là thành phần thực hiện chuyển đổi văn bản sang định dạng vector số thực.

### Self-check questions
1. Hãy mô tả vai trò của từng thành phần AWS trong luồng nạp dữ liệu RAG của Alex.
2. Tại sao tác giả khóa học lại chuyển đổi từ OpenSearch sang S3 Vectors trong quá trình thử nghiệm dự án?

### Flashcards
- Q: S3 Vectors giúp tiết kiệm bao nhiêu chi phí so với OpenSearch Serverless?
  A: Khoảng 90% cost (chi phí).
- Q: Tần suất chạy mặc định của Researcher Agent trong Alex là bao nhiêu?
  A: Mỗi 2 giờ.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 80. Day 4 - Building Cost-Effective Vector Storage with S3 and Lambda Ingestion

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [80. Day 4 - Building Cost-Effective Vector Storage with S3 and Lambda Ingestion.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/80.%20Day%204%20-%20Building%20Cost-Effective%20Vector%20Storage%20with%20S3%20and%20Lambda%20Ingestion.txt) - Đã dùng
- Slide: [Production W3D4.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D4.pdf) - Đã dùng (đối chiếu nội dung qua transcript)
- Code:
  - [ingest_s3vectors.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/ingest_s3vectors.py) - Đã dùng và phân tích
  - [package.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/package.py) - Đã dùng và phân tích
  - [3_ingest.md](file:///G:/AIProduction_t6_2026/production/week3/alex/guides/3_ingest.md) - Đã dùng
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Học viên thực hiện tạo thủ công S3 Vector Bucket và Vector Index trên AWS Console. Việc tạo thủ công giúp dữ liệu vector tồn tại độc lập, không bị xóa nhầm khi chạy lệnh `terraform destroy` để dọn dẹp hạ tầng stateless.
- Quy định đặt tên Vector Bucket: `alex-vectors-{your-account-id}` để đảm bảo tính duy nhất trên toàn cầu (global namespace).
- Khởi tạo Vector Index tên là `financial-research` với cấu hình bắt buộc: `Dimension = 384` (khớp với mô hình `all-MiniLM-L6-v2`) và `Distance metric = Cosine` (đo độ tương đồng Cosine).
- Giới thiệu cấu trúc code Lambda trong thư mục `backend/ingest/`. Đây là một dự án Python độc lập sử dụng trình quản lý gói `uv`.
- File chính [ingest_s3vectors.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/ingest_s3vectors.py) chứa handler Lambda thực hiện nhận text, gọi SageMaker Endpoint để lấy embedding, và lưu trữ vào S3 Vectors.
- File [package.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/package.py) tự động hóa việc cài đặt dependencies và nén toàn bộ code thành tệp `lambda_function.zip` (dung lượng ~15MB) để sẵn sàng deploy.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu nguyên lý phân tách tài nguyên có trạng thái (stateful) và không có trạng thái (stateless) trong thiết kế hệ thống đám mây.
  - Hiểu ý nghĩa của các tham số cấu hình Vector Index: dimension (số chiều) và distance metric (khoảng cách đo lường).
  - Nắm được cách thức đóng gói mã nguồn Lambda kèm dependencies bằng Python script.
- **Practical goals - mục tiêu thực hành**:
  - Tạo thành công Vector Bucket và Index `financial-research` trên AWS S3 Console.
  - Thực thi lệnh `uv run package.py` tại local để đóng gói thành công file `lambda_function.zip`.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao số chiều của Vector Index bắt buộc phải cấu hình là 384 trong dự án này.
  - Tại sao không nên quản lý S3 Vector Bucket thông qua vòng đời của Terraform học tập.

## 4. Previous Context - Liên hệ với bài trước
- Bài học trực tiếp sử dụng kết quả đầu ra của Day 3 là SageMaker Serverless Endpoint chạy mô hình `sentence-transformers/all-MiniLM-L6-v2` để sinh ra các mảng số thực 384 chiều từ văn bản đầu vào.

## 5. Core Theory - Lý thuyết cốt lõi
- **Stateful vs Stateless Resources - Tài nguyên có trạng thái và không trạng thái**: Tài nguyên stateful (như cơ sở dữ liệu, S3 bucket) lưu trữ dữ liệu lâu dài và cần được bảo vệ nghiêm ngặt. Tài nguyên stateless (như Lambda compute, API Gateway cấu hình) có thể dễ dàng bị xóa và tái tạo mà không làm mất dữ liệu người dùng.
- **Cosine similarity - Độ tương đồng Cosine**: Chỉ số đo lường hướng của hai vector trong không gian đa chiều, dùng để đánh giá mức độ tương đồng ngữ nghĩa. Giá trị dao động từ -1 đến 1, trong đó giá trị càng gần 1 thể hiện ý nghĩa văn bản càng sát nhau.
- **Lambda Deployment Package - Gói triển khai Lambda**: Tệp nén (.zip) chứa mã nguồn Python cùng tất cả các gói thư viện phụ thuộc, giúp Lambda chạy độc lập trên môi trường AWS mà không cần tải thêm thư viện ngoài khi khởi chạy.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Quy trình đóng gói mã nguồn Lambda bằng package.py:
1. **Input**: File code chính `ingest_s3vectors.py`, cấu hình dependencies trong `pyproject.toml` và `uv.lock`.
2. **Processing steps**:
   - Khởi tạo một thư mục tạm thời tên là `build/` tại thư mục hiện hành.
   - Sao chép file `ingest_s3vectors.py` vào thư mục `build/`.
   - Sử dụng lệnh nén zip để đóng gói toàn bộ nội dung trong thư mục `build/` thành tệp tin `lambda_function.zip`.
   - Thực hiện dọn dẹp (xóa bỏ) thư mục tạm thời `build/` để giữ không gian làm việc sạch sẽ.
3. **Output**: File zip `lambda_function.zip` có dung lượng khoảng 15MB sẵn sàng phục vụ cho Terraform deploy.

## 7. Techniques - Kỹ thuật sử dụng
- **Stateful Resource Isolation - Cô lập tài nguyên có trạng thái**:
  - Purpose (mục đích): Đảm bảo an toàn dữ liệu, tránh việc vô tình xóa mất cơ sở dữ liệu hoặc kho chứa vector khi cập nhật cấu trúc hạ tầng stateless.
  - When to use (dùng khi nào): Khi xây dựng các dự án học tập hoặc phát triển có tần suất hủy/tạo hạ tầng cao bằng Terraform.
  - Trade-off (đánh đổi): Đòi hỏi nhà phát triển phải thực hiện tạo thủ công bằng tay hoặc duy trì một kịch bản Terraform riêng biệt chỉ dành cho stateful resources.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích file [ingest_s3vectors.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/ingest_s3vectors.py)

- **Hàm `get_embedding(text)`**:
  - *Purpose (mục đích)*: Gửi văn bản tới SageMaker Endpoint để lấy mảng vector số thực biểu diễn ngữ nghĩa.
  - *Logic chính*:
    - Gọi `sagemaker_runtime.invoke_endpoint` truyền body JSON `{"inputs": text}`.
    - Phản hồi từ Hugging Face PyTorch Container trả về mảng lồng nhau lên tới 3 lớp `[[[embedding]]]`.
    - Đoạn code kiểm tra kiểu dữ liệu `isinstance` để bóc tách chính xác mảng 1 chiều chứa 384 số thực:
      ```python
      result = json.loads(response['Body'].read().decode())
      if isinstance(result, list) and len(result) > 0:
          if isinstance(result[0], list) and len(result[0]) > 0:
              if isinstance(result[0][0], list):
                  return result[0][0]  # Trích xuất từ [[[embedding]]]
              return result[0]  # Trích xuất từ [[embedding]]
      return result
      ```

- **Hàm `lambda_handler(event, context)`**:
  - *Purpose (mục đích)*: Handler chính xử lý yêu cầu nạp tài liệu từ API Gateway.
  - *Logic chính*:
    - Thực hiện phân tích cú pháp (parse) `body` của sự kiện.
    - Lấy nội dung `text` và `metadata` đi kèm.
    - Gọi hàm `get_embedding` để lấy vector từ SageMaker.
    - Sinh mã UUID v4 ngẫu nhiên làm khóa định danh duy nhất (`vector_id`).
    - Gọi `s3_vectors.put_vectors` để đẩy dữ liệu vào S3 Vectors:
      ```python
      s3_vectors.put_vectors(
          vectorBucketName=VECTOR_BUCKET,
          indexName=INDEX_NAME,
          vectors=[{
              "key": vector_id,
              "data": {"float32": embedding},
              "metadata": {
                  "text": text,
                  "timestamp": datetime.datetime.utcnow().isoformat(),
                  **metadata
              }
          }]
      )
      ```

### Phân tích file [package.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/package.py)
- Sử dụng thư viện `shutil` và `zipfile` của Python để tạo thư mục `build/`, copy file `ingest_s3vectors.py`, cài đặt các dependencies cần thiết và nén thành `lambda_function.zip` nằm ngay tại thư mục hiện hành.

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Khai báo S3 Vector Bucket trực tiếp trong Terraform của Day 4**
  - Pros: Tự động hóa hoàn toàn luồng triển khai, không cần vào AWS Console thực hiện bằng tay.
  - Cons: Dữ liệu vector đã nạp sẽ bị xóa sạch hoàn toàn mỗi khi chạy lệnh `terraform destroy`.
  - When to choose: Các dự án thực tế chạy trên pipeline CI/CD ổn định, không có nhu cầu phá hủy hạ tầng thường xuyên.
- **Option 2: Tạo S3 Vector Bucket thủ công bằng tay (Lựa chọn của khóa học)**
  - Pros: Dữ liệu được bảo toàn vĩnh viễn, học viên có thể hủy và tạo lại phần hạ tầng API Gateway/Lambda thoải mái mà không lo mất dữ liệu.
  - Cons: Đòi hỏi học viên phải ghi nhớ cấu hình thủ công và copy chính xác tên bucket vào file biến.
  - When to choose: (Recommended) Môi trường thực hành học tập, thử nghiệm phát triển ứng dụng.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Lỗi ghi dữ liệu vào S3 Vectors do sai định dạng vector phản hồi.
  - Root cause: Hugging Face PyTorch Inference Container trả về mảng lồng nhau 3 lớp `[[[embedding]]]`, nếu truyền thẳng định dạng này vào trường `"data": {"float32": embedding}` của API `put_vectors`, S3 Vectors sẽ từ chối và báo lỗi API.
  - Symptom: Lambda trả về statusCode 500 kèm thông báo lỗi định dạng dữ liệu đầu vào.
  - Fix / prevention: Sử dụng các khối lệnh kiểm tra kiểu dữ liệu `isinstance(..., list)` trong mã nguồn Python để bóc tách mảng lồng nhau về mảng 1 chiều chuẩn trước khi ghi.

## 11. Knowledge Extension - Kiến thức mở rộng
- Kể từ năm 2025, AWS bổ sung client `s3vectors` vào bộ công cụ SDK Boto3. Điều này yêu cầu thư viện `boto3` trong môi trường Lambda phải đạt phiên bản tối thiểu tương thích. Việc sử dụng runtime `python3.12` mặc định trên Lambda đã tích hợp sẵn phiên bản Boto3 mới nhất hỗ trợ dịch vụ này.

## 12. Study Pack - Gói ôn tập
### Must remember
1. S3 Vector Bucket phải được tạo thủ công trong mục "Vector buckets" của S3 Console.
2. Index tìm kiếm `financial-research` được cấu hình 384 chiều, khoảng cách Cosine.
3. Kịch bản `package.py` chịu trách nhiệm đóng gói dependencies thành `lambda_function.zip`.
4. Lệnh chạy kịch bản đóng gói: `uv run package.py` trong thư mục `backend/ingest`.

### Self-check questions
1. Tại sao cấu hình số chiều của index S3 Vectors bắt buộc phải là 384 trong bài học này?
2. Hãy phân tích cấu trúc phản hồi mảng lồng nhau từ container Hugging Face và cách xử lý trong code Python.

### Flashcards
- Q: Tên tham số khoảng cách đo lường độ tương đồng vector được dùng là gì?
  A: Cosine.
- Q: Tệp zip đóng gói Lambda được tạo ra có tên là gì?
  A: `lambda_function.zip`.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 81. Day 4 - Setting Up Secure AI Ingestion Pipelines with Terraform and AWS

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [81. Day 4 - Setting Up Secure AI Ingestion Pipelines with Terraform and AWS.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/81.%20Day%204%20-%20Setting%20Up%20Secure%20AI%20Ingestion%20Pipelines%20with%20Terraform%20and%20AWS.txt) - Đã dùng
- Slide: [Production W3D4.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D4.pdf) - Đã dùng (đối chiếu nội dung qua transcript)
- Code:
  - [main.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/3_ingestion/main.tf) - Đã dùng và phân tích
  - [variables.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/3_ingestion/variables.tf) - Đã dùng
  - [outputs.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/3_ingestion/outputs.tf) - Đã dùng
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Xây dựng hạ tầng tự động hóa cho đường ống nạp dữ liệu bằng Terraform trong thư mục `terraform/3_ingestion`.
- Học viên copy file cấu hình biến `terraform.tfvars` từ file `.example` để khai báo vùng hoạt động (`aws_region`) và tên endpoint SageMaker (`sagemaker_endpoint_name = "alex-embedding-endpoint"`).
- Mã nguồn [main.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/3_ingestion/main.tf) thực hiện khởi tạo và cấu hình:
  - Một S3 bucket `alex-vectors-{account_id}` với tính năng versioning và mã hóa server-side AES256 được bật, đồng thời chặn hoàn toàn truy cập public.
  - IAM Role và IAM Policy cấp quyền tối thiểu (least privilege) cho Lambda, cho phép Lambda tương tác với CloudWatch logs, đọc/ghi S3 Vectors, invoke SageMaker Endpoint.
  - Lambda function `alex-ingest` trỏ trực tiếp tới zip package `lambda_function.zip` đã build ở bước trước với runtime `python3.12` và memory 512MB.
  - REST API Gateway `alex-api` tích hợp Lambda dưới dạng `AWS_PROXY`. Route `/ingest` với method POST yêu cầu xác thực bằng API Key (`api_key_required = true`).
  - Cấu hình Usage Plan để điều tiết lưu lượng: quota 10,000 requests/tháng, throttling rate 100 và burst 200.
- Sau khi chạy `terraform apply`, Terraform output ra các biến cấu hình. Học viên sử dụng CLI lấy API Key thực sự để lưu vào file `.env` ở root project.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu cách thức cấu hình bảo mật API Gateway sử dụng API Key, Usage Plan và cơ chế Throttling.
  - Nắm được cách thiết lập chính sách bảo mật IAM tối giản cho Lambda tương tác với SageMaker và S3 Vectors.
- **Practical goals - mục tiêu thực hành**:
  - Triển khai hạ tầng thành công bằng các lệnh `terraform init` và `terraform apply`.
  - Thực thi lệnh AWS CLI để lấy API Key và cập nhật đầy đủ các biến cấu hình vào file `.env`.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao cần thiết lập Usage Plan và Throttling cho một endpoint nạp dữ liệu (ingestion endpoint).
  - Tác dụng của biến môi trường trong cấu hình Lambda function.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này tích hợp trực tiếp với SageMaker Serverless Endpoint được tạo ở Day 3. Tên endpoint `alex-embedding-endpoint` được truyền qua tệp biến `terraform.tfvars` để cấp quyền cho Lambda thực hiện lệnh gọi invoke.

## 5. Core Theory - Lý thuyết cốt lõi
- **API Key - Khóa API**: Chuỗi ký tự bảo mật độc nhất do API Gateway sinh ra, đóng vai trò như định danh xác thực client trước khi cho phép kích hoạt dịch vụ backend.
- **Usage Plan - Kế hoạch sử dụng**: Định nghĩa trong API Gateway quy định cụ thể hạn ngạch truy cập (quota) theo tháng và tốc độ gọi (throttling) cho các client sử dụng API Key tương ứng.
- **Throttling and Burst - Điều tiết và Bùng nổ**: Cơ chế bảo vệ hệ thống khỏi quá tải. Throttling rate (tốc độ xử lý trung bình liên tục mỗi giây) và Burst (số lượng yêu cầu tối đa được phép xử lý ngay lập tức tại một thời điểm rất ngắn).

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng xử lý yêu cầu nạp dữ liệu qua API Gateway:
1. **Input**: Client gửi một yêu cầu HTTP POST chứa JSON payload đến endpoint URL `/ingest` kèm theo HTTP header `x-api-key`.
2. **Processing steps**:
   - API Gateway tiếp nhận yêu cầu, kiểm tra sự tồn tại và tính hợp lệ của key trong stage `prod`.
   - Nếu key không hợp lệ hoặc thiếu: API Gateway chặn ngay lập tức và trả về lỗi `403 Forbidden`.
   - Nếu key hợp lệ, API Gateway đối chiếu với Usage Plan để kiểm tra xem có vượt quá tốc độ gọi (throttling) hay hạn mức tháng (quota) hay không. Nếu vượt quá: Trả về lỗi `429 Too Many Requests`.
   - Nếu mọi điều kiện bảo mật được đáp ứng, API Gateway chuyển tiếp (proxy) toàn bộ yêu cầu tới Lambda function `alex-ingest`.
   - Lambda xử lý logic, trả về JSON response.
3. **Output**: API Gateway chuyển tiếp phản hồi thành công `200 OK` chứa ID của tài liệu vừa được nạp về client.

## 7. Techniques - Kỹ thuật sử dụng
- **API Rate Limiting - Giới hạn tần suất API**:
  - Purpose (mục đích): Ngăn chặn các cuộc tấn công từ chối dịch vụ (DoS), tránh việc vô tình gọi API vô hạn từ mã nguồn lỗi của client làm phát sinh chi phí khổng lồ từ các dịch vụ backend (Lambda, SageMaker).
  - When to use (dùng khi nào): Bắt buộc áp dụng cho mọi API public hướng ra ngoài internet trong các hệ thống sản xuất (production).
  - Trade-off (đánh đổi): Làm tăng độ phức tạp trong cấu hình hạ tầng và quản lý phân phối API Key cho các client.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích file cấu hình [main.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/3_ingestion/main.tf)

- **Khối IAM Policy `aws_iam_role_policy.lambda_policy`**:
  - Định nghĩa chi tiết các quyền hạn tối thiểu cho Lambda function:
    - Ghi log: `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`.
    - Đọc/ghi bucket: `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` trên bucket `aws_s3_bucket.vectors.arn`.
    - Gọi SageMaker: `sagemaker:InvokeEndpoint` trực tiếp đến ARN của endpoint embedding.
    - Quyền thao tác vector: `s3vectors:PutVectors`, `s3vectors:QueryVectors`, `s3vectors:GetVectors`, `s3vectors:DeleteVectors` trên ARN của S3 Vectors bucket.

- **Khối Lambda Function `aws_lambda_function.ingest`**:
  - Khai báo file zip nguồn: `${path.module}/../../backend/ingest/lambda_function.zip`.
  - Khai báo handler: `ingest_s3vectors.lambda_handler`.
  - Cấp phát RAM: `512MB`, timeout `60s`.
  - Cấu hình biến môi trường:
    ```hcl
    environment {
      variables = {
        VECTOR_BUCKET      = aws_s3_bucket.vectors.id
        SAGEMAKER_ENDPOINT = var.sagemaker_endpoint_name
      }
    }
    ```

- **Khối API Gateway Usage Plan `aws_api_gateway_usage_plan.plan`**:
  - Định cấu hình quota giới hạn 10,000 cuộc gọi mỗi tháng:
    ```hcl
    quota_settings {
      limit  = 10000
      period = "MONTH"
    }
    throttle_settings {
      rate_limit  = 100
      burst_limit = 200
    }
    ```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Public REST API không yêu cầu xác thực**
  - Pros: Thiết lập cực nhanh, client gọi trực tiếp không cần header cấu hình phức tạp.
  - Cons: Bất kỳ ai dò được URL đều có thể spam API gây cạn kiệt tài nguyên hệ thống và đẩy chi phí AWS lên cao.
  - When to choose: Chỉ dùng cho các buổi demo ngắn hạn hoặc môi trường mạng nội bộ hoàn toàn cô lập.
- **Option 2: REST API yêu cầu xác thực bằng API Key và có Usage Plan (Lựa chọn của dự án)**
  - Pros: Bảo mật vững chắc, ngăn chặn lạm dụng tài nguyên backend, kiểm soát được chi phí vận hành RAG.
  - Cons: Phải thực hiện các bước cấu hình CLI phức tạp để lấy key và phân phối key bảo mật.
  - When to choose: (Recommended) Các dịch vụ API thương mại, SaaS thương mại có thu phí người dùng.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: API trả về lỗi 500 hoặc 403 sau khi deploy hạ tầng thành công.
  - Root cause: Thiếu phân quyền cho API Gateway invoke Lambda (`aws_lambda_permission.api_gateway`), hoặc API Key chưa được gán chính xác vào Usage Plan bằng tài nguyên `aws_api_gateway_usage_plan_key`.
  - Symptom: Gọi API bằng curl/Postman nhận lỗi `Forbidden` hoặc `Internal server error`.
  - Fix / prevention: Kiểm tra kỹ sự hiện diện của khối tài nguyên `aws_lambda_permission` trong file `.tf` và chạy `terraform output` để xác minh key đã được gán vào Usage Plan stage `prod`.

## 11. Knowledge Extension - Kiến thức mở rộng
- Kịch bản Terraform sử dụng một trigger redeployment trong `aws_api_gateway_deployment.api` bằng hàm băm `sha1(jsonencode(...))`. Kỹ thuật này giúp Terraform tự động phát hiện mọi thay đổi cấu hình nhỏ nhất trong API Gateway (như sửa đổi route, method hoặc integration) để thực hiện tái triển khai stage ngay lập tức, tránh hiện tượng cấu hình lưu trên Terraform nhưng stage thực tế trên AWS chưa được cập nhật.

## 12. Study Pack - Gói ôn tập
### Must remember
1. API Gateway được thiết lập bắt buộc phải truyền API key qua header `x-api-key`.
2. Lambda function `alex-ingest` được cấu hình RAM 512MB, timeout 60 giây.
3. Usage Plan giới hạn 10,000 requests/tháng, throttling rate 100 và burst 200 để chống spam.
4. Lệnh lấy API Key qua CLI: `aws apigateway get-api-key --api-key YOUR_API_KEY_ID --include-value --query 'value' --output text`.

### Self-check questions
1. Tại sao trong môi trường thực tế, việc thiết lập rate limiting và burst limit lại quan trọng đối với các API gọi mô hình AI?
2. Hãy phân tích sự khác nhau giữa vai trò IAM và chính sách Usage Plan của API Gateway.

### Flashcards
- Q: Header nào được sử dụng để API Gateway kiểm tra khóa truy cập?
  A: `x-api-key`.
- Q: Quota mặc định cấu hình cho Usage Plan của Alex là bao nhiêu yêu cầu/tháng?
  A: 10,000.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 82. Day 4 - Testing Your AWS Lambda Vector Ingest Pipeline End-to-End

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [82. Day 4 - Testing Your AWS Lambda Vector Ingest Pipeline End-to-End.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/82.%20Day%204%20-%20Testing%20Your%20AWS%20Lambda%20Vector%20Ingest%20Pipeline%20End-to-End.txt) - Đã dùng
- Code:
  - [test_ingest_s3vectors.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/test_ingest_s3vectors.py) - Đã dùng và phân tích
  - [test_search_s3vectors.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/test_search_s3vectors.py) - Đã dùng và phân tích
  - [cleanup_s3vectors.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/cleanup_s3vectors.py) - Đã dùng
- Summary lịch sử: [day3_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day3_summary.md) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Thực hiện quy trình kiểm thử đầu-cuối (end-to-end testing) cho toàn bộ hệ thống nạp và tìm kiếm dữ liệu vector.
- Trước khi nạp dữ liệu, học viên chạy script `test_search_s3vectors.py` để chứng minh kho lưu trữ S3 Vectors ban đầu trống (không trả về kết quả).
- Chạy script `test_ingest_s3vectors.py` để nạp 3 tài liệu mẫu về Tesla (TSLA), Amazon (AMZN), và Nvidia (NVDA). Các văn bản này được gửi qua SageMaker để chuyển đổi sang vector 384 chiều và ghi vào S3 Vectors.
- Chạy lại script `test_search_s3vectors.py` để thực hiện tìm kiếm ngữ nghĩa (semantic search) bằng các câu hỏi khái niệm không trùng khớp từ khóa gốc như "electric vehicles", "cloud computing" hoặc "GPU computing".
- Kết quả tìm kiếm trả về đúng các tài liệu có liên quan ngữ nghĩa cao (ví dụ: truy vấn "electric vehicles" tìm thấy đúng tài liệu của Tesla) kèm theo điểm số tương đồng ngữ nghĩa chính xác.
- Giới thiệu tiện ích `cleanup_s3vectors.py` giúp xóa sạch dữ liệu trong index khi cần chạy lại bài test từ đầu.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu sự vượt trội của tìm kiếm ngữ nghĩa (semantic search) so với tìm kiếm từ khóa truyền thống.
  - Hiểu cách thức tính toán điểm số tương đồng (similarity score) từ khoảng cách Cosine (distance).
- **Practical goals - mục tiêu thực hành**:
  - Chạy thành công chuỗi lệnh kiểm thử: Search (empty) -> Ingest -> Search (matched).
  - Phân tích và giải thích được kết quả tìm kiếm ngữ nghĩa trên console.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao câu truy vấn "electric vehicles and sustainable transportation" lại khớp được với tài liệu Tesla dù văn bản gốc của Tesla chỉ chứa từ khóa số ít "electric vehicle".
  - Ý nghĩa của giá trị `1 - distance` trong tính toán điểm số tìm kiếm.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này là bước xác nhận chất lượng cuối cùng cho toàn bộ hạ tầng đã xây dựng xuyên suốt Day 3 (SageMaker) và Day 4 (S3 Vectors, Lambda, API Gateway).

## 5. Core Theory - Lý thuyết cốt lõi
- **Semantic Search - Tìm kiếm ngữ nghĩa**: Khả năng tìm kiếm thông tin dựa trên ý nghĩa ngữ cảnh và khái niệm ẩn sau câu chữ, giúp khớp các từ đồng nghĩa hoặc các câu diễn đạt khác nhau có cùng bản chất.
- **Similarity score - Điểm tương đồng**: Chỉ số định lượng mức độ gần gũi ngữ nghĩa giữa câu hỏi của người dùng và tài liệu được lưu trữ. Chỉ số này dao động trong khoảng `[0, 1]`, điểm càng cao thể hiện tài liệu càng liên quan mật thiết.
- **Direct ingestion - Nạp dữ liệu trực tiếp**: Kỹ thuật gọi trực tiếp API của dịch vụ AWS bằng SDK (`boto3`) tại local để ghi dữ liệu, bỏ qua API Gateway để kiểm tra nhanh phân quyền IAM thô và kết nối vật lý.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Quy trình thực hiện kiểm thử End-to-End:
1. **Kiểm tra trạng thái rỗng**: Chạy `uv run test_search_s3vectors.py` để xác nhận S3 Vectors index hiện chưa chứa bất kỳ vector nào.
2. **Nạp dữ liệu mẫu**: Chạy `uv run test_ingest_s3vectors.py`. Script này đọc file cấu hình `.env` để lấy thông tin bucket và endpoint, sau đó gửi 3 tài liệu của Tesla, Amazon, Nvidia tới SageMaker để lấy vector embedding, và gọi `s3_vectors.put_vectors` để lưu trữ dữ liệu vào S3 Vectors.
3. **Truy vấn ngữ nghĩa**: Chạy `uv run test_search_s3vectors.py`. Script lấy câu truy vấn của học viên, gọi SageMaker chuyển sang vector, sau đó gọi `s3_vectors.query_vectors` với `topK=3`.
4. **Xử lý kết quả**: Trình explorer nhận kết quả từ S3 Vectors, chuyển đổi khoảng cách sang điểm số tương đồng theo công thức `score = 1 - distance` và in thông tin kết quả kèm score lên console.

## 7. Techniques - Kỹ thuật sử dụng
- **Semantic Similarity Querying - Truy vấn tương đồng ngữ nghĩa**:
  - Purpose (mục đích): Trích xuất các tài liệu có độ liên quan ngữ nghĩa cao nhất để làm ngữ cảnh đầu vào (context) cho LLM trong các quy trình RAG.
  - When to use (dùng khi nào): Bắt buộc phải có trong mọi ứng dụng chatbot AI, trợ lý ảo tra cứu tài liệu doanh nghiệp.
  - Trade-off (đánh đổi): Yêu cầu hệ thống phải sinh vector embedding cho mọi câu hỏi đầu vào của người dùng, làm tăng thời gian xử lý (độ trễ) thêm một vài mili-giây.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích file [test_ingest_s3vectors.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/test_ingest_s3vectors.py)
- Sử dụng thư viện `dotenv` để tải các biến môi trường `VECTOR_BUCKET` và `SAGEMAKER_ENDPOINT` từ file `.env` ở thư mục gốc.
- **Hàm `ingest_document(text, metadata)`**:
  - Gọi `get_embedding(text)` để lấy mảng embeddings từ SageMaker.
  - Sinh mã UUID v4 làm khóa cho vector (`vector_id`).
  - Gọi `s3_vectors.put_vectors` để đẩy vector vào index `financial-research` trong S3 Vectors bucket.
- **Khối hàm `main()`**:
  - Khai báo danh sách `test_docs` gồm 3 tài liệu chứa thông tin mô tả chi tiết của Tesla (TSLA), Amazon (AMZN), và Nvidia (NVDA) kèm theo metadata chi tiết (ticker, company_name, sector, source).
  - Duyệt qua từng tài liệu và gọi hàm `ingest_document` để nạp vào cơ sở dữ liệu.

### Phân tích file [test_search_s3vectors.py](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/ingest/test_search_s3vectors.py)
- **Hàm `search_vectors(query_text, k)`**:
  - Gọi `get_embedding(query_text)` để lấy vector embedding của câu truy vấn.
  - Gọi `s3_vectors.query_vectors` với các tham số: `queryVector`, `topK=k`, `returnDistance=True`, và `returnMetadata=True`.
  - Duyệt qua danh sách kết quả trả về, thực hiện tính toán điểm số hiển thị:
    ```python
    distance = vector.get('distance', 0)
    print(f"Score: {1 - distance:.3f}")
    ```
- **Khối hàm `main()`**:
  - Gọi hàm `list_all_vectors` thực hiện một câu truy vấn tìm kiếm rộng với từ khóa "company" để liệt kê tối đa 10 vectors đang có trong database.
  - Chạy thử nghiệm 3 câu truy vấn ngữ nghĩa mẫu:
    - `"electric vehicles and sustainable transportation"` (kỳ vọng tìm thấy Tesla).
    - `"cloud computing and AWS services"` (kỳ vọng tìm thấy Amazon).
    - `"artificial intelligence and GPU computing"` (kỳ vọng tìm thấy Nvidia).

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Thực hiện kiểm thử tích hợp thông qua API Gateway endpoint**
  - Pros: Kiểm tra được toàn bộ luồng hoạt động thực tế bao gồm cả xác thực API Key, Usage Plan và cấu hình định tuyến của API Gateway Stage.
  - Cons: Nếu xảy ra lỗi, việc gỡ lỗi sẽ phức tạp hơn do phải kiểm tra logs ở nhiều nơi (CloudWatch API Gateway, CloudWatch Lambda, SageMaker Logs).
  - When to choose: Giai đoạn kiểm thử tích hợp hệ thống cuối cùng trước khi đưa lên môi trường staging/production.
- **Option 2: Kiểm thử trực tiếp qua AWS SDK (Lựa chọn của bài thực hành)**
  - Pros: Đơn giản, cô lập lỗi tốt, giúp xác minh nhanh chóng tính đúng đắn của quyền IAM cục bộ đối với S3 Vectors và SageMaker Endpoint.
  - Cons: Không kiểm tra được tầng bảo mật API Gateway.
  - When to choose: (Recommended) Giai đoạn phát triển ban đầu, dùng để unit test nhanh các dịch vụ dữ liệu cốt lõi.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Điểm số tương đồng ngữ nghĩa (Similarity Score) hiển thị bị âm hoặc không trực quan.
  - Root cause: Khoảng cách Cosine (`distance`) trả về từ S3 Vectors nằm trong khoảng `[0, 2]`. Nếu học viên không chuyển đổi đúng công thức mà sử dụng các công thức tính khoảng cách khác, giá trị hiển thị sẽ bị lệch.
  - Symptom: Điểm số hiển thị trên console có giá trị âm hoặc lớn hơn 1.
  - Fix / prevention: Bắt buộc sử dụng công thức `similarity = 1 - distance` để đưa điểm số về dải giá trị chuẩn trực quan từ 0 đến 1.

## 11. Knowledge Extension - Kiến thức mở rộng
- S3 Vectors sử dụng thuật toán Tìm kiếm lân cận gần nhất gần đúng (Approximate Nearest Neighbor - ANN) dựa trên cấu trúc phân cấp đồ thị (Hierarchical Navigable Small World - HNSW) được AWS tối ưu hóa đặc biệt. Thuật toán này giúp tìm kiếm các vector tương tự trong thời gian mili-giây mà không cần duyệt tuyến tính qua tất cả các file dữ liệu trên S3, đảm bảo hiệu năng cao khi kho dữ liệu phình to.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Chạy search trước khi ingest để đảm bảo database rỗng.
2. Ingest nạp 3 tài liệu mẫu của Tesla, Amazon và Nvidia.
3. Semantic search tìm kiếm dựa trên ý nghĩa khái niệm, không khớp từ khóa chính xác.
4. Công thức tính Similarity Score: `1 - Cosine Distance`.
5. Script `cleanup_s3vectors.py` dùng để xóa sạch index làm lại từ đầu.

### Self-check questions
1. Tại sao câu truy vấn "artificial intelligence and GPU computing" lại trả về Nvidia đầu tiên với điểm số cao nhất?
2. Sự khác nhau lớn nhất trong kết quả trả về của tìm kiếm ngữ nghĩa và tìm kiếm từ khóa thông thường là gì?

### Flashcards
- Q: Công thức đổi Cosine Distance sang Similarity Score là gì?
  A: `1 - Cosine Distance`.
- Q: Script nào được dùng để xóa dữ liệu index phục vụ test lại?
  A: `cleanup_s3vectors.py`.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.
