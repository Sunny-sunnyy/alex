# Day 4 Summary - Enterprise-Grade AI: Monitoring, Security & Observability at Scale

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

---

# 107. Day 4 - Enterprise-Grade AI - Monitoring, Security & Observability at Scale

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: đã dùng
- Slide: đã dùng (Production W4D4.pdf - trang 1-5)
- Code: không có code trực tiếp cho lesson này
- Summary lịch sử: đã dùng (day3_summary.md)
- Ghi chú về độ tin cậy hoặc mâu thuẫn giữa nguồn: Các nguồn nhất quán về mặt kiến trúc tổng thể.

## 2. Executive Summary - Tóm tắt cốt lõi
- Buổi học mở đầu cho ngày thứ tư của tuần 4, tập trung vào việc nâng cấp hệ thống multi-agent Alex lên tiêu chuẩn vận hành doanh nghiệp.
- Nhấn mạnh triết lý không tin tưởng mù quáng vào giao diện người dùng (UI) hay các hành vi mang tính "kỳ diệu" (magic) của agent mà phải giám sát và kiểm chứng thực tế ở backend.
- Giới thiệu 6 trụ cột chính của Enterprise-Grade AI: Scalability (khả năng mở rộng), Security (bảo mật), Monitoring (giám sát), Guardrails (hàng rào bảo vệ), Explainability (khả năng giải thích), và Observability (khả năng quan sát).
- Điều chỉnh sơ đồ kiến trúc tổng thể bằng cách tách biệt API Gateway như một thành phần độc lập cực kỳ quan trọng để bảo vệ Lambda backend.
- Nhắc nhở người học coi LLM là mô hình thống kê (statistical model) chuyên dự báo token chứ không phải thực thể suy luận hoàn hảo, từ đó cần lập trình kiểm chứng nghiêm ngặt.

## 3. Lesson Goals - Mục tiêu bài học
- Concept goals - mục tiêu kiến thức: Hiểu rõ 6 trụ cột đưa hệ thống AI vào môi trường sản xuất quy mô lớn. Nhận thức đúng đắn bản chất thống kê của LLM để lập trình phòng thủ.
- Practical goals - mục tiêu thực hành: Nhận diện cấu trúc hạ tầng phân tán trên AWS phục vụ cho MLOps/LLMOps của dự án Alex.
- What learner should be able to explain - người học cần giải thích được: Tại sao không nên tin tưởng tuyệt đối vào output của LLM và cách tiếp cận đúng khi thiết kế kiểm soát (controls) đầu ra.

## 4. Previous Context - Liên hệ với bài trước
Bài học này trực tiếp tiếp nối từ Day 3 sau khi đã hoàn thành việc deploy frontend NextJS và Lambda API Gateway. Bài học mở ra pha cuối cùng của Capstone để hoàn thiện các cơ chế vận hành chuyên nghiệp (enterprise readiness).

## 5. Core Theory - Lý thuyết cốt lõi
- Term - thuật ngữ: Enterprise-Grade AI - Trạng thái sẵn sàng cho doanh nghiệp của hệ thống AI
  - Meaning - nghĩa: Các tiêu chuẩn về bảo mật, độ tin cậy, hiệu năng và khả năng mở rộng để phục vụ khách hàng thực tế với SLA (Service Level Agreement) cam kết.
  - Why it matters - vì sao quan trọng: Giúp hệ thống sống sót trước tải trọng lớn, các cuộc tấn công mạng, và kiểm soát được chi phí vận hành.
  - Relationship - liên hệ với khái niệm khác: Được cấu thành từ sự kết hợp của cả 6 trụ cột kỹ thuật.
- Term - thuật ngữ: Statistical Model - Mô hình thống kê
  - Meaning - nghĩa: Bản chất của LLM là dự đoán token tiếp theo có khả năng xảy ra cao nhất dựa trên xác suất, thay vì thực hiện lập luận logic thực sự.
  - Why it matters - vì sao quan trọng: Nhắc nhở nhà phát triển rằng LLM có thể bị sai lệch (hallucination) bất cứ lúc nào, đòi hỏi phải thiết kế code để validate kết quả.
  - Relationship - liên hệ với khái niệm khác: Là nguyên nhân cốt lõi dẫn đến nhu cầu triển khai Guardrails.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
Không có pipeline kỹ thuật cụ thể cho bài học này. Dưới đây là luồng tư duy tiếp cận:
- 1. Phân tích hiện trạng (chỉ nhìn thấy UI chạy) -> 2. Nhận diện rủi ro (hành vi agent bị ẩn) -> 3. Áp dụng 6 trụ cột Enterprise -> 4. Tách biệt và bảo vệ API Gateway -> 5. Kiểm chứng hoạt động thực tế ở backend.

## 7. Techniques - Kỹ thuật sử dụng
- Technique - kỹ thuật: 6 Pillars of Production AI - 6 trụ cột đưa AI vào sản xuất
  - Purpose - mục đích: Thiết lập các kiểm soát toàn diện cho ứng dụng AI cấp doanh nghiệp.
  - When to use - dùng khi nào: Khi chuyển đổi dự án từ nguyên mẫu (prototype) sang chạy thực tế cho người dùng (production).
  - Trade-off - đánh đổi: Tăng thời gian phát triển và đòi hỏi kỹ năng quản trị hệ thống phức tạp hơn.
  - Common mistake - lỗi dễ gặp: Bỏ qua việc viết code xác thực đầu ra, chỉ dựa vào prompt chỉ thị để ép buộc định dạng.

## 8. Code Walkthrough - Phân tích code nếu có
Buổi học này không có code được cung cấp.

## 9. Options / Trade-offs - Bản đồ lựa chọn
Bài học tổng quan chưa đưa ra các tùy chọn công nghệ cụ thể.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- Failure mode: Tin tưởng hoàn toàn vào sự tự trị của agent (agent autonomy) mà không có cơ chế giám sát.
  - Root cause: Nhân cách hóa AI (anthropomorphizing), coi chúng là các thực thể tư duy thông minh thực sự thay vì mô hình thống kê.
  - Symptom: Agent sinh ra thông tin sai lệch gây lỗi ứng dụng hoặc sai số tài chính nhưng hệ thống không ghi nhận hoặc cảnh báo.
  - Fix / prevention: Thiết lập logging chi tiết và viết code kiểm tra điều kiện đầu ra nghiêm ngặt.

## 11. Knowledge Extension - Kiến thức mở rộng
- MLOps vs LLMOps: MLOps truyền thống tập trung vào giám sát độ lệch dữ liệu (data drift) và huấn luyện lại mô hình (retraining). LLMOps mở rộng thêm việc quản lý Prompt, giám sát token cost, quản trị cơ sở dữ liệu vector, tích hợp MCP servers và tracing luồng đi của agent.

## 12. Study Pack - Gói ôn tập
### Must remember
- 6 trụ cột Enterprise-grade AI: Scalability, Security, Monitoring, Guardrails, Explainability, Observability.
- Bản chất của LLM là mô hình thống kê dự đoán token, không phải máy lập luận hoàn hảo.
- Không bao giờ tin tưởng tuyệt đối vào output của LLM, luôn validate bằng code.
- API Gateway là chốt chặn bảo mật quan trọng để thiết lập throttling.
- Tránh nhân cách hóa AI khi lập trình hệ thống sản xuất.

### Self-check questions
- 6 trụ cột đưa AI vào sản xuất là gì?
- Tại sao coi LLM là "mô hình thống kê" lại thay đổi cách chúng ta viết code cho agent?

### Flashcards
- Q: Trụ cột nào giúp ta biết chính xác đường đi của dữ liệu giữa các agent và chi phí token?
  A: Observability (Khả năng quan sát).

### Interview Q&A nếu phù hợp
- Q: Tại sao bạn không nên để AI Agent trực tiếp hiển thị kết quả phân tích tài chính lên UI mà không qua bước validate?
  A: Vì LLM có thể bị ảo giác (hallucination) tạo ra các số liệu tài chính sai lệch. Việc validate bằng code ở backend giúp ngăn chặn các kết quả không hợp lệ tiếp cận khách hàng.

## 13. Missing Inputs - Còn thiếu gì
Không có.

---

# 108. Day 4 - Enterprise-Grade AI - Scaling, Security, and Monitoring for Production

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: đã dùng
- Slide: đã dùng (Production W4D4.pdf - trang 5)
- Code: không có code trực tiếp cho lesson này
- Summary lịch sử: đã dùng (day3_summary.md)
- Ghi chú về độ tin cậy hoặc mâu thuẫn giữa nguồn: Các nguồn nhất quán về các tham số hạ tầng.

## 2. Executive Summary - Tóm tắt cốt lõi
- Bài học đi sâu vào 2 trụ cột đầu tiên: Scalability (Khả năng mở rộng) và Security (Bảo mật).
- Khả năng mở rộng của hệ thống Alex được thừa hưởng trực tiếp từ kiến trúc serverless trên AWS: Lambda tự động scale (mặc định 1,000 concurrent executions), Aurora Serverless v2 tự động scale từ 0.5 đến 128 ACUs, API Gateway chịu tải 10,000 rps, SQS cung cấp throughput gần như không giới hạn.
- Về bảo mật, ứng dụng áp dụng nguyên tắc IAM Least Privilege (quyền hạn tối thiểu), xác thực JWT với Clerk (xoay vòng khóa tự động qua JWKS), CORS và CSP chống XSS.
- Giới thiệu các dịch vụ bảo mật cao cấp (có tính phí): AWS WAF (Web Application Firewall), VPC Endpoints bảo mật mạng nội bộ và GuardDuty phát hiện đe dọa bằng ML.

## 3. Lesson Goals - Mục tiêu bài học
- Concept goals - mục tiêu kiến thức: Hiểu cách thức co giãn tự động của các dịch vụ serverless. Nắm vững các lớp bảo mật cần thiết từ tầng biên (CloudFront/WAF) đến cơ sở dữ liệu (Aurora).
- Practical goals - mục tiêu thực hành: Biết cách điều chỉnh các tham số mở rộng và bảo mật trong các cấu hình Terraform (`main.tf`, `variables.tf`).
- What learner should be able to explain - người học cần giải thích được: Tại sao IAM Least Privilege và JWKS key rotation lại quan trọng đối với bảo mật ứng dụng.

## 4. Previous Context - Liên hệ với bài trước
Bài học hướng dẫn tinh chỉnh các cấu hình hạ tầng Terraform đã được triển khai từ Day 1, Day 2 và Day 3 để phục vụ cho lượng tải lớn và tăng cường an toàn thông tin.

## 5. Core Theory - Lý thuyết cốt lõi
- Term - thuật ngữ: Horizontal Scaling - Mở rộng hàng ngang
  - Meaning - nghĩa: Việc tăng cường số lượng thực thể tính toán (ví dụ: Lambda instances) để cùng xử lý tải, thay vì nâng cấp tài nguyên phần cứng của một máy đơn lẻ (Vertical Scaling).
  - Why it matters - vì sao quan trọng: Giúp hệ thống xử lý lượng request tăng đột biến mà không bị quá tải hay dừng hoạt động.
  - Relationship - liên hệ với khái niệm khác: Tự động hóa bởi AWS Lambda và API Gateway.
- Term - thuật ngữ: IAM Least Privilege - Quyền hạn tối thiểu trong IAM
  - Meaning - nghĩa: Nguyên tắc thiết kế chỉ cấp các quyền tối thiểu cần thiết cho một dịch vụ/người dùng để thực thi công việc của họ.
  - Why it matters - vì sao quan trọng: Giảm thiểu thiệt hại tối đa nếu một hàm Lambda hoặc tài khoản bị hacker chiếm quyền điều khiển.
  - Relationship - liên hệ với khái niệm khác: Được khai báo qua các tệp `aws_iam_role_policy` trong Terraform.
- Term - thuật ngữ: JWKS (JSON Web Key Set) - Tập hợp khóa web JSON
  - Meaning - nghĩa: Một tập hợp các khóa mã hóa công khai (public keys) được sử dụng để xác thực tính hợp lệ của các token JWT.
  - Why it matters - vì sao quan trọng: Cho phép tự động xoay vòng khóa ký JWT (key rotation) mà không cần cấu hình lại code ở backend.
  - Relationship - liên hệ với khái niệm khác: Được cung cấp bởi Clerk và được Lambda API sử dụng để giải mã JWT.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
Không có pipeline kỹ thuật cụ thể cho bài học này. Dưới đây là luồng bảo mật của hệ thống:
- Client (Front-end) -> CloudFront CDN (CSP headers) -> API Gateway (Throttling check) -> Lambda API (JWT validation via Clerk JWKS) -> Secrets Manager (Retrieve DB credentials) -> Aurora DB (Execute statement).

## 7. Techniques - Kỹ thuật sử dụng
- Technique - kỹ thuật: AWS WAF Rate Limiting - Giới hạn tần suất qua WAF
  - Purpose - mục đích: Chặn các cuộc tấn công DDoS ở mức IP trước khi yêu cầu tiếp cận API Gateway.
  - When to use - dùng khi nào: Khi vận hành ứng dụng thực tế trên môi trường public internet.
  - Trade-off - đánh đổi: Tăng chi phí hóa đơn AWS.
  - Common mistake - lỗi dễ gặp: Đặt ngưỡng rate limit quá thấp làm chặn nhầm người dùng hợp lệ.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`. (Học viên chỉ cần đọc và phân tích cấu hình lý thuyết của WAF và VPC Endpoint trong Guide 8).

## 9. Options / Trade-offs - Bản đồ lựa chọn
- Option: Sử dụng AWS WAF
  - Pros: Bảo vệ chống SQL Injection, XSS, DDoS tự động từ tầng biên AWS.
  - Cons: Chi phí cao (~$5/web ACL/month + phí xử lý request).
  - When to choose: Ứng dụng production thương mại thực tế.
- Option: VPC Endpoints (PrivateLink)
  - Pros: Lưu lượng mạng đi hoàn toàn trong AWS nội bộ, bảo mật tuyệt đối, giảm độ trễ.
  - Cons: Phí xử lý dữ liệu tính theo dung lượng (GB).
  - When to choose: Các dự án enterprise có yêu cầu khắt khe về truyền dẫn dữ liệu.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- Failure mode: Lộ mật khẩu cơ sở dữ liệu trên mã nguồn Git hoặc logs.
  - Root cause: Hardcode mật khẩu hoặc token trực tiếp vào file code hoặc biến môi trường không được bảo vệ.
  - Symptom: Cơ sở dữ liệu bị truy cập trái phép hoặc bị hacker mã hóa tống tiền.
  - Fix / prevention: Sử dụng AWS Secrets Manager kết hợp KMS để mã hóa và lấy thông tin đăng nhập động vào lúc runtime.

## 11. Knowledge Extension - Kiến thức mở rộng
- CORS vs CSP: CORS bảo vệ server bằng cách hạn chế các website khác gửi request đến API của mình. CSP bảo vệ trình duyệt của user bằng cách hạn chế trình duyệt tải các script hoặc style từ những nguồn không tin cậy.

## 12. Study Pack - Gói ôn tập
### Must remember
- Lambda scale tự động tới 1,000 concurrent executions mặc định.
- Clerk JWT tokens hết hạn sau 1 giờ.
- Secrets Manager mã hóa credentials tĩnh thông qua KMS.
- VPC Endpoints ngăn chặn dữ liệu đi qua internet công cộng.
- IAM Least Privilege hạn chế rò rỉ quyền hạn chéo giữa các agent.

### Self-check questions
- Làm thế nào JWKS giúp ích cho việc bảo vệ API người dùng?
- Phân biệt CORS và Content Security Policy (CSP)?

### Flashcards
- Q: Dịch vụ nào bảo vệ API Gateway khỏi SQL Injection và DDoS tự động?
  A: AWS WAF (Web Application Firewall).

### Interview Q&A nếu phù hợp
- Q: Làm thế nào để ngăn chặn một Lambda function chiếm dụng toàn bộ tài nguyên concurrent của tài khoản AWS?
  A: Thiết lập tham số `reserved_concurrent_executions` trong cấu hình Terraform cho từng Lambda cụ thể để giới hạn băng thông chạy đồng thời.

## 13. Missing Inputs - Còn thiếu gì
Không có.

---

# 109. Day 4 - Monitoring AI Agents in Production with CloudWatch and Dashboards

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: đã dùng
- Slide: đã dùng (Production W4D4.pdf - trang 5)
- Code: đã dùng (main.tf trong [terraform/8_enterprise](file:///G:/AIProduction_t6_2026/production/week4/alex/terraform/8_enterprise/main.tf))
- Summary lịch sử: đã dùng (day3_summary.md)
- Ghi chú về độ tin cậy hoặc mâu thuẫn giữa nguồn: Các nguồn đồng bộ về cấu hình CloudWatch Dashboard.

## 2. Executive Summary - Tóm tắt cốt lõi
- Hướng dẫn thực hành triển khai hệ thống CloudWatch Dashboards để giám sát tài nguyên AI và Lambda agents của Alex.
- Sử dụng Terraform để định nghĩa IaC (Infrastructure as Code) cho dashboard, tránh cấu hình tay trên Console.
- Xây dựng 2 bảng điều khiển chính:
  1. `alex-ai-model-usage`: Giám sát Bedrock Invocations, Token Count, Response Latency; SageMaker Invocations và Latency.
  2. `alex-agent-performance`: Giám sát Lambda Duration (thời gian chạy), Errors (lỗi), Invocations (số lượt gọi), Concurrency và Throttles cho cả 5 agents.
- Hướng dẫn cách phân tích log streams của Planner và Reporter trong CloudWatch Log Groups để kiểm chứng quá trình cập nhật giá từ Polygon API.

## 3. Lesson Goals - Mục tiêu bài học
- Concept goals - mục tiêu kiến thức: Hiểu cách ánh xạ các thông số vận hành của AWS Lambda, Bedrock và SageMaker sang CloudWatch metrics.
- Practical goals - mục tiêu thực hành: Triển khai thành công CloudWatch Dashboards qua Terraform và theo dõi biểu đồ hoạt động thời gian thực.
- What learner should be able to explain - người học cần giải thích được: Ý nghĩa của việc theo dõi latency và token count của Bedrock trong vận hành MLOps.

## 4. Previous Context - Liên hệ với bài trước
Bài học sử dụng hạ tầng Lambda của Day 2 và database của Day 1 để hiển thị dữ liệu log và đo lường thời gian thực thi của từng Lambda agent.

## 5. Core Theory - Lý thuyết cốt lõi
- Term - thuật ngữ: CloudWatch Dashboard - Bảng điều khiển CloudWatch
  - Meaning - nghĩa: Một giao diện hiển thị trực quan các biểu đồ chỉ số (metrics) của tài nguyên AWS.
  - Why it matters - vì sao quan trọng: Giúp kỹ sư MLOps theo dõi sức khỏe hệ thống thời gian thực mà không cần đọc log thủ công.
  - Relationship - liên hệ với khái niệm khác: Định nghĩa qua thuộc tính `dashboard_body` dưới dạng JSON trong Terraform.
- Term - thuật ngữ: Metric Period - Chu kỳ chỉ số
  - Meaning - nghĩa: Khoảng thời gian (tính bằng giây) dùng để gom nhóm dữ liệu thô phục vụ việc tính toán các thống kê (Sum, Average, Max, Min).
  - Why it matters - vì sao quan trọng: Quyết định độ mịn của biểu đồ giám sát.
  - Relationship - liên hệ với khái niệm khác: Tham số `period` trong cấu hình widget.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
Quy trình triển khai giám sát:
- 1. Tạo file `terraform.tfvars` trong thư mục `8_enterprise` -> 2. Thực hiện `terraform init` và `terraform apply` -> 3. Truy cập CloudWatch Console -> 4. Mở menu Dashboards -> 5. Kiểm tra biểu đồ khi click "Start New Analysis" từ frontend.

## 7. Techniques - Kỹ thuật sử dụng
- Technique - kỹ thuật: Search Expressions in Dashboards - Biểu thức tìm kiếm chỉ số
  - Purpose - mục đích: Động quét và gom nhóm metrics từ nhiều variants/endpoints của SageMaker mà không cần chỉ định cứng.
  - When to use - dùng khi nào: Giám sát SageMaker serverless endpoints có Variant Name hoặc Endpoint Name thay đổi động.
  - Trade-off - đánh đổi: Cú pháp viết trong file cấu hình JSON tương đối phức tạp.

## 8. Code Walkthrough - Phân tích code nếu có
- File / block: `G:\AIProduction_t6_2026\production\week4\alex\terraform\8_enterprise\main.tf`
- Purpose - mục đích: Tạo các AWS CloudWatch dashboards để giám sát tài nguyên AI và hiệu năng Lambda.
- Key logic - logic chính: Sử dụng hàm `jsonencode` của Terraform để xây dựng cấu trúc `widgets` JSON. Dùng hàm `SEARCH` để quét động metrics của SageMaker.
- Important lines / functions:
  - Dòng 35-36: Khai báo `aws_cloudwatch_dashboard` `ai_model_usage`.
  - Dòng 47-49: Theo dõi các metrics Bedrock gồm `Invocations`, `InvocationClientErrors`, `InvocationServerErrors`.
  - Dòng 72-73: Theo dõi `InputTokenCount` và `OutputTokenCount` của Bedrock.
  - Dòng 120-122: Hàm `SEARCH` động tìm kiếm metric `Invocations` trên SageMaker endpoint `alex-embedding-endpoint`.
  - Dòng 182-186: Giám sát `Duration` (thời gian chạy) của 5 Lambda function: planner, reporter, charter, retirement, tagger.
- Vietnamese inline notes:
  ```hcl
  # main.tf: Cấu hình dashboard cho Lambda Duration
  # Sử dụng namespace "AWS/Lambda" và MetricName "Duration" để lấy thời gian chạy trung bình (Average)
  metrics = [
    ["AWS/Lambda", "Duration", "FunctionName", "alex-planner", { stat = "Average", label = "Planner" }],
    [".", ".", ".", "alex-reporter", { stat = "Average", label = "Reporter" }],
    [".", ".", ".", "alex-charter", { stat = "Average", label = "Charter" }],
    [".", ".", ".", "alex-retirement", { stat = "Average", label = "Retirement" }],
    [".", ".", ".", "alex-tagger", { stat = "Average", label = "Tagger" }]
  ]
  ```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- Option: Định nghĩa Dashboard bằng Terraform (IaC)
  - Pros: Nhất quán, có thể lưu trữ trong Git, dễ dàng nhân bản sang các môi trường Dev/Staging/Prod.
  - Cons: Code JSON lồng trong HCL dài và dễ lỗi cú pháp khi chỉnh sửa thủ công.
  - When to choose: Khuyên dùng cho tất cả dự án thực tế.
- Option: Tạo Dashboard thủ công trên Console
  - Pros: Giao diện kéo thả trực quan, nhanh chóng.
  - Cons: Không thể tự động hóa, dễ lỗi cấu hình khi triển khai quy mô lớn.
  - When to choose: Thử nghiệm nhanh (Proof of Concept - PoC).

## 10. Pitfalls - Lỗi / bẫy thường gặp
- Failure mode: Widget biểu đồ không hiển thị dữ liệu (No data).
  - Root cause: Chỉ định sai Region của Bedrock model trong cấu hình dashboard (Bedrock model thường chỉ khả dụng ở us-west-2 hoặc us-east-1).
  - Symptom: Biểu đồ trống trơn mặc dù hệ thống vẫn chạy bình thường.
  - Fix / prevention: Đảm bảo biến `bedrock_region` trong `terraform.tfvars` khớp chính xác với region nơi đăng ký model access.

## 11. Knowledge Extension - Kiến thức mở rộng
- SageMaker Latency Metrics: Chỉ số `ModelLatency` của SageMaker đo lường thời gian xử lý thực tế của mô hình bên trong container (tính bằng micro-giây - μs), loại bỏ thời gian trễ mạng truyền tải (overhead), khác với `OverheadLatency`.

## 12. Study Pack - Gói ôn tập
### Must remember
- Dashboard `ai-model-usage` giúp giám sát Bedrock & SageMaker.
- Dashboard `agent-performance` giám sát 5 Lambda agents.
- SageMaker latency được đo bằng micro-giây (μs), Bedrock latency được đo bằng mili-giây (ms).
- Cấu hình dashboard IaC giúp tối ưu hóa quy trình DevOps/MLOps.

### Self-check questions
- Đơn vị đo latency của SageMaker và Bedrock khác nhau thế nào trong CloudWatch?
- Mục đích của hàm SEARCH trong cấu hình dashboard của SageMaker là gì?

### Flashcards
- Q: Metric nào của Bedrock dùng để giám sát lượng dữ liệu token đầu vào?
  A: InputTokenCount.

### Interview Q&A nếu phù hợp
- Q: Làm thế nào để phát hiện một Lambda function đang bị quá tải hoặc bị AWS bóp băng thông (throttling)?
  A: Giám sát metric `Throttles` và `ConcurrentExecutions` của hàm đó trên Dashboard. Nếu Throttles > 0, cần nâng hạn mức concurrency.

## 13. Missing Inputs - Còn thiếu gì
Không có.

---

# 110. Day 4 - Monitoring AI Systems and Building Guardrails for Production Agents

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: đã dùng
- Slide: đã dùng (Production W4D4.pdf - trang 5, 7)
- Code: không có code trực tiếp cho lesson này
- Summary lịch sử: đã dùng (day3_summary.md)
- Ghi chú về độ tin cậy hoặc mâu thuẫn giữa nguồn: Các nguồn nhất quán về triết lý thiết kế guardrails.

## 2. Executive Summary - Tóm tắt cốt lõi
- Hướng dẫn giám sát hàng đợi tin nhắn SQS (Messages in flight, Dead Letter Queue - DLQ) để kiểm tra luồng phân tích bất đồng bộ.
- Hướng dẫn thiết lập CloudWatch Alarms để tự động gửi thông báo email (qua SNS) khi Lambda gặp lỗi hoặc DLQ có tin nhắn.
- Trình bày triết lý thiết kế Guardrails: Khuyên khích lập trình viên bắt đầu bằng code Python đơn giản (Simple Python Guardrails) thay vì tích hợp các framework phức tạp ngay từ đầu.
- Giới thiệu 4 kỹ thuật Guardrails quan trọng:
  1. Output Structure Validation (đảm bảo định dạng JSON hợp lệ).
  2. Input Sanitization (phát hiện từ khóa prompt injection).
  3. Response Truncation (giới hạn kích thước token đầu ra).
  4. Tenacity Retry with Exponential Backoff (tự động thử lại khi gặp lỗi rate limit).

## 3. Lesson Goals - Mục tiêu bài học
- Concept goals - mục tiêu kiến thức: Hiểu vai trò của DLQ trong kiến trúc hướng sự kiện (event-driven architecture). Nắm vững nguyên lý của retry logic lùi thời gian.
- Practical goals - mục tiêu thực hành: Biết cách viết mã Python thực thi input sanitization chống prompt injection và validate cấu trúc JSON.
- What learner should be able to explain - người học cần giải thích được: Tại sao retry lùi thời gian theo cấp số nhân lại tăng độ bền vững cho ứng dụng AI.

## 4. Previous Context - Liên hệ với bài trước
Nối tiếp từ phần xây dựng hàng đợi SQS và Lambda Planner ở Day 2 để thiết lập các cảnh báo và chốt chặn an toàn cho luồng xử lý phân tích.

## 5. Core Theory - Lý thuyết cốt lõi
- Term - thuật ngữ: Dead Letter Queue (DLQ) - Hàng đợi thư chết
  - Meaning - nghĩa: Một hàng đợi phụ chứa các tin nhắn SQS bị lỗi sau khi đã thử lại quá số lần quy định.
  - Why it matters - vì sao quan trọng: Ngăn chặn các request lỗi làm nghẽn hàng đợi chính, hỗ trợ kỹ sư tìm lỗi hệ thống dễ dàng.
  - Relationship - liên hệ với khái niệm khác: Liên kết trực tiếp với hàng đợi chính `alex-analysis-jobs`.
- Term - thuật ngữ: Prompt Injection - Tấn công tiêm prompt
  - Meaning - nghĩa: Việc người dùng cố tình nhập mã chỉ thị (ví dụ: "ignore previous instructions") để ghi đè prompt hệ thống của Agent.
  - Why it matters - vì sao quan trọng: Bảo vệ Agent khỏi nguy cơ thực thi lệnh sai trái, lộ dữ liệu hoặc phá hoại hệ thống.
  - Relationship - liên hệ với khái niệm khác: Được ngăn chặn bằng Input Guardrails.
- Term - thuật ngữ: Exponential Backoff - Thử lại lùi thời gian theo cấp số nhân
  - Meaning - nghĩa: Thuật toán tự động tăng thời gian chờ giữa các lần retry (ví dụ: chờ 2s, 4s, 8s, 16s) khi API đích báo lỗi tạm thời.
  - Why it matters - vì sao quan trọng: Tránh việc gửi dồn dập request làm nghẽn hệ thống đích khi nó đang bị quá tải (rate limit).
  - Relationship - liên hệ với khái niệm khác: Sử dụng thư viện `tenacity` trong Python.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
Quy trình kiểm soát của Guardrail:
- 1. Người dùng nhập đầu vào -> 2. Sanitize Input (Lọc prompt injection) -> 3. Gửi đến Agent -> 4. Gọi LLM (Retry qua Tenacity nếu rate limit) -> 5. Nhận kết quả -> 6. Validate Output (Parse JSON kiểm tra cấu trúc) -> 7. Trả về cho frontend (Fallback nếu lỗi).

## 7. Techniques - Kỹ thuật sử dụng
- Technique - kỹ thuật: Input Sanitization - Làm sạch đầu vào
  - Purpose - mục đích: Phát hiện sớm các từ khóa tiêm prompt để từ chối xử lý ngay lập tức.
  - When to use: Áp dụng cho bất kỳ trường dữ liệu tự do nào do người dùng nhập từ giao diện.
  - Trade-off - đánh đổi: Có thể chặn nhầm các cụm từ hợp lệ nếu bộ lọc quá nhạy.
  - Common mistake - lỗi dễ gặp: Chỉ lọc các từ khóa viết thường mà quên kiểm tra chữ hoa.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`. (Học viên tham khảo các snippet code Python mẫu được cung cấp trong Guide 8 về validate chart JSON và sanitize input).

## 9. Options / Trade-offs - Bản đồ lựa chọn
- Option: Viết Guardrails bằng code Python thuần
  - Pros: Tốc độ xử lý cực nhanh (gần như 0ms), không tốn chi phí token, dễ kiểm soát logic.
  - Cons: Khó phát hiện các kiểu tiêm prompt biến tướng tinh vi về mặt ngữ nghĩa.
  - When to choose: Lớp phòng vệ cơ bản đầu tiên bắt buộc phải có.
- Option: Sử dụng LLM độc lập để validate (LLM Guardrails)
  - Pros: Hiểu ngữ cảnh ngữ nghĩa sâu sắc, phát hiện được các lỗi tinh vi.
  - Cons: Tăng chi phí token và làm tăng độ trễ (latency) của API Gateway.
  - When to choose: Các ứng dụng tài chính/pháp lý có yêu cầu bảo mật cực cao.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- Failure mode: Racking up massive Bedrock bill due to infinite retry loops.
  - Root cause: Sử dụng thư viện tenacity retry vô hạn mà không giới hạn số lần thử (`stop=stop_after_attempt`).
  - Symptom: Hóa đơn AWS tăng vọt đột ngột khi mô hình ngôn ngữ hoặc API Gateway gặp lỗi hệ thống kéo dài.
  - Fix / prevention: Luôn giới hạn số lần thử lại tối đa từ 3 đến 5 lần trong decorator `@retry`.

## 11. Knowledge Extension - Kiến thức mở rộng
- Lỗi ảo giác (Hallucination): Guardrails không thể sửa hoàn toàn ảo giác của LLM, nhưng chúng hoạt động như một lưới an toàn (failsafe) để đảm bảo lỗi của LLM không tiếp cận được người dùng cuối (ví dụ: trả về thông báo lỗi thân thiện thay vì hiển thị dữ liệu lỗi).

## 12. Study Pack - Gói ôn tập
### Must remember
- DLQ dùng để chứa các message xử lý thất bại.
- Nên bắt đầu viết Guardrails bằng code Python đơn giản.
- Tenacity giúp tự động retry các lỗi tạm thời (RateLimitError, TimeoutError).
- Prompt injection là nguy cơ bảo mật hàng đầu cho Agent.
- Truncate response giúp hạn chế runaway token costs.

### Self-check questions
- Nêu 4 kỹ thuật Guardrails cơ bản bằng code Python?
- DLQ có vai trò gì trong kiến trúc hướng sự kiện của Agent?

### Flashcards
- Q: Thư viện Python phổ biến nào được Ed Donner khuyên dùng để viết retry logic?
  A: Tenacity.

### Interview Q&A nếu phù hợp
- Q: Làm cách nào để bạn validate xem kết quả trả về từ một agent có cấu trúc JSON hợp lệ trước khi render lên UI?
  A: Sử dụng khối lệnh `try/except` bao quanh lệnh `json.loads(response)`. Nếu xảy ra lỗi `JSONDecodeError`, trả về kết quả fallback an toàn và ghi nhận log lỗi.

## 13. Missing Inputs - Còn thiếu gì
Không có.

---

# 111. Day 4 - Advanced LLM Observability with Langfuse and Production Guardrails

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: đã dùng
- Slide: đã dùng (Production W4D4.pdf - trang 5)
- Code: đã dùng (observability.py trong [backend/reporter](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/reporter/observability.py))
- Summary lịch sử: đã dùng (day3_summary.md)
- Ghi chú về độ tin cậy hoặc mâu thuẫn giữa nguồn: Các nguồn nhất quán về cơ chế hoạt động của Langfuse.

## 2. Executive Summary - Tóm tắt cốt lõi
- Giới thiệu Langfuse như một nền tảng chuyên dụng mã nguồn mở để theo dõi chi tiết (observability) hoạt động của LLM.
- Hướng dẫn thiết lập tài khoản Langfuse Cloud, tạo project, và lấy bộ 3 khóa: Public Key, Secret Key, và Host URL.
- Giải thích cơ chế liên kết thông qua Logfire (thư viện của Pydantic AI) để tự động giám sát và xuất log từ OpenAI Agents SDK sang Langfuse.
- Phân tích mã nguồn tệp helper `observability.py` cung cấp context manager `@contextmanager def observe()` giúp tích hợp Langfuse mượt mà vào Lambda.
- Giải thích sự cần thiết của việc cấu hình khóa `OPENAI_API_KEY` (dù hệ thống chạy Bedrock/Nova Pro) để kích hoạt luồng xuất dữ liệu OpenTelemetry.

## 3. Lesson Goals - Mục tiêu bài học
- Concept goals - mục tiêu kiến thức: Hiểu khái niệm Observability và sự khác biệt với Monitoring truyền thống. Nắm vững cơ chế thu thập trace của OpenTelemetry.
- Practical goals - mục tiêu thực hành: Khai báo thành công các biến môi trường Langfuse trong Terraform và import helper `observe` vào handler.
- What learner should be able to explain - người học cần giải thích được: Tại sao phải sử dụng lệnh `time.sleep(10)` ở cuối khối handler khi chạy trên AWS Lambda.

## 4. Previous Context - Liên hệ với bài trước
Bài học liên kết trực tiếp với các cấu hình Terraform biến môi trường Lambda của Day 2 để truyền tải credentials của Langfuse lên môi trường AWS.

## 5. Core Theory - Lý thuyết cốt lõi
- Term - thuật ngữ: Observability - Khả năng quan sát
  - Meaning - nghĩa: Khả năng đo lường trạng thái nội tại của một hệ thống dựa trên các dữ liệu đầu ra như log, trace, và span.
  - Why it matters - vì sao quan trọng: Giúp kỹ sư hiểu rõ đường đi của dữ liệu giữa các agent và phát hiện chính xác agent nào bị lỗi hoặc chậm.
  - Relationship - liên hệ với khái niệm khác: Cao cấp hơn giám sát (Monitoring) truyền thống nhờ khả năng truy vết ngữ nghĩa (semantic tracing).
- Term - thuật ngữ: Trace and Span - Trace và Span
  - Meaning - nghĩa: Trace đại diện cho toàn bộ hành trình của một request (ví dụ: cả quá trình chạy Planner). Span đại diện cho một đơn vị công việc nhỏ nằm trong Trace (ví dụ: Tagger running).
  - Why it matters - vì sao quan trọng: Giúp phân rã cấu trúc thực thi của multi-agent để dễ phân tích hiệu năng.
  - Relationship - liên hệ với khái niệm khác: Một Trace chứa nhiều Spans phân cấp.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
Quy trình tích hợp và ghi log:
- 1. Tạo project trên Langfuse -> 2. Cấu hình biến môi trường `LANGFUSE_*` trong Terraform tfvars -> 3. Terraform apply để đẩy biến lên Lambda -> 4. Lambda handler chạy code trong khối `with observe():` -> 5. Traces được sinh ra qua Logfire -> 6. Gọi `flush()` và sleep 10 giây trước khi Lambda kết thúc.

## 7. Techniques - Kỹ thuật sử dụng
- Technique - kỹ thuật: Lambda Trace Flushing Workaround - Giải pháp flush trace trên Lambda
  - Purpose - mục đích: Đảm bảo luồng log chạy nền kịp gửi dữ liệu đi trước khi AWS Lambda đóng băng (freeze) container thực thi.
  - When to use - dùng khi nào: Mọi trường hợp sử dụng thư viện logging/tracing dạng bất đồng bộ chạy nền trên môi trường Serverless Lambda.
  - Trade-off - đánh đổi: Làm tăng thời gian chạy của Lambda thêm 10 giây (tốn thêm một chút chi phí thực thi Lambda).
  - Common mistake - lỗi dễ gặp: Quên không sleep làm cho log bị mất hoặc bị dồn sang lần invocation tiếp theo.

## 8. Code Walkthrough - Phân tích code nếu có
- File / block: `G:\AIProduction_t6_2026\production\week4\alex\backend\reporter\observability.py`
- Purpose - mục đích: Cung cấp Context Manager `observe` để tự động hóa việc kết nối và dọn dẹp kết nối Langfuse.
- Key logic - logic chính: Kiểm tra xem `LANGFUSE_SECRET_KEY` có cấu hình hay không để quyết định kích hoạt. Khởi tạo `logfire` để instrument OpenAI Agents SDK.
- Important lines / functions:
  - Dòng 33-34: Đọc biến môi trường kiểm tra cấu hình.
  - Dòng 58-61: Gọi `logfire.configure(service_name="alex_reporter_agent", send_to_logfire=False)`.
  - Dòng 65: Gọi `logfire.instrument_openai_agents()` để liên kết SDK.
  - Dòng 98-99: Gọi `langfuse_client.flush()` và `langfuse_client.shutdown()`.
  - Dòng 105-106: Gọi `time.sleep(10)` để trì hoãn đóng container.
- Vietnamese inline notes:
  ```python
  # observability.py: Khối finally thực hiện dọn dẹp luồng gửi trace
  finally:
      if langfuse_client:
          try:
              logger.info("Flushing traces...")
              langfuse_client.flush()
              langfuse_client.shutdown()
              # Bắt buộc sleep 10 giây vì Lambda sẽ lập tức bị đóng băng (frozen) sau khi return.
              # Việc sleep giúp luồng background thread kịp gửi các gói tin HTTP gửi trace lên Langfuse Cloud.
              import time
              time.sleep(10)
          except Exception as e:
              logger.error(f"Failed to flush: {e}")
  ```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- Option: Thêm delay `time.sleep(10)` ở cuối Lambda
  - Pros: Traces được gửi lên Langfuse đầy đủ, ổn định, không bị mất mát.
  - Cons: Tăng thời gian thực thi của Lambda lên 10 giây cho mỗi request, gây tốn thêm phí Lambda.
  - When to choose: Cần thiết cho môi trường Lambda khi chưa có proxy hay sidecar xử lý log riêng.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- Failure mode: Không thấy trace xuất hiện trên Langfuse mặc dù log Lambda báo thành công.
  - Root cause: Biến `OPENAI_API_KEY` không được thiết lập trong môi trường Lambda.
  - Symptom: Không có trace nào được ghi nhận, hoặc Langfuse báo lỗi OpenTelemetry export.
  - Fix / prevention: Đảm bảo luôn khai báo `OPENAI_API_KEY` trong `terraform.tfvars` và truyền nó vào biến môi trường của Lambda.

## 11. Knowledge Extension - Kiến thức mở rộng
- Logfire: Là nền tảng observability mới phát triển bởi nhóm Pydantic, sử dụng OpenTelemetry làm nền tảng cốt lõi, tích hợp rất tốt với các thư viện Python hiện đại.

## 12. Study Pack - Gói ôn tập
### Must remember
- Langfuse là công cụ observability mã nguồn mở cho LLM.
- Logfire giúp instrument OpenAI Agents SDK sang định dạng OpenTelemetry.
- Cần `OPENAI_API_KEY` để kích hoạt OpenTelemetry exporter của SDK.
- Bắt buộc sleep 10s trên Lambda để flush trace thành công.

### Self-check questions
- Tại sao Logfire lại cần thiết trong chuỗi tích hợp từ OpenAI Agents SDK đến Langfuse?
- Hiện tượng Lambda "freeze" ảnh hưởng thế nào đến việc ghi trace và cách khắc phục?

### Flashcards
- Q: Tên hàm dùng để kết nối và tự động bắt log của OpenAI Agents SDK trong Logfire là gì?
  A: logfire.instrument_openai_agents().

### Interview Q&A nếu phù hợp
- Q: Làm thế nào để bảo mật các khóa API Langfuse khi phân phối mã nguồn Lambda cho nhiều nhà phát triển?
  A: Lưu trữ các khóa trong AWS Secrets Manager hoặc truyền vào qua biến môi trường Terraform đã được mã hóa, không commit trực tiếp vào repository.

## 13. Missing Inputs - Còn thiếu gì
Không có.

---

# 112. Day 4 - LLM-as-a-Judge Pattern with Langfuse Observability in Production

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: đã dùng
- Slide: đã dùng (Production W4D4.pdf - trang 5, 7)
- Code: đã dùng ([judge.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/reporter/judge.py) và [lambda_handler.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/reporter/lambda_handler.py) trong [backend/reporter](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/reporter/))
- Summary lịch sử: đã dùng (day3_summary.md)
- Ghi chú về độ tin cậy hoặc mâu thuẫn giữa nguồn: Các nguồn nhất quán về logic code của Judge.

## 2. Executive Summary - Tóm tắt cốt lõi
- Thực hành triển khai thiết kế mẫu LLM-as-a-Judge (sử dụng mô hình ngôn ngữ làm trọng tài) để đánh giá chất lượng sản phẩm đầu ra của agent.
- Xây dựng Pydantic model `Evaluation` với 2 trường: `feedback` (nhận xét lý do) và `score` (điểm số từ 0 đến 100).
- Áp dụng nguyên tắc vàng của Prompt Engineering: Đặt trường lý luận (`feedback`) lên trước điểm số (`score`) trong cấu hình Pydantic để bắt buộc mô hình phải suy nghĩ lập luận trước khi đưa ra điểm số (Explainable AI), tránh hiện tượng ngụy biện sau khi chấm điểm.
- Tích hợp kết quả của Judge vào Langfuse dưới dạng điểm số (`span.score`) và sự kiện (`observability.create_event`).
- Thiết lập chốt chặn bảo vệ (Guardrail): Nếu score dưới 30% (0.3), hệ thống sẽ từ chối trả về kết quả lỗi của LLM và thay bằng một thông báo fallback an toàn cho người dùng.

## 3. Lesson Goals - Mục tiêu bài học
- Concept goals - mục tiêu kiến thức: Hiểu thiết kế mẫu LLM-as-a-Judge và cách nó giúp tự động hóa kiểm định chất lượng AI.
- Practical goals - mục tiêu thực hành: Viết chương trình đánh giá chất lượng báo cáo tài chính bằng một agent chấm điểm độc lập. Đăng ký điểm số trực tiếp lên Langfuse dashboard.
- What learner should be able to explain - người học cần giải thích được: Tại sao việc đặt trường lý giải (rationale) trước kết quả (classification/score) lại giúp tăng độ chính xác của mô hình.

## 4. Previous Context - Liên hệ với bài trước
Bài học liên kết trực tiếp với Langfuse context manager ở bài 111 để đẩy thông tin đánh giá của Judge lên giao diện Langfuse.

## 5. Core Theory - Lý thuyết cốt lõi
- Term - thuật ngữ: LLM-as-a-Judge - LLM đóng vai trò trọng tài
  - Meaning - nghĩa: Việc sử dụng một mô hình ngôn ngữ độc lập để chấm điểm hoặc đánh giá đầu ra của một mô hình ngôn ngữ khác dựa trên bộ tiêu chí xác định.
  - Why it matters - vì sao quan trọng: Giải quyết bài toán đánh giá các văn bản tự do (unstructured text) mà các chương trình so khớp chuỗi truyền thống không làm được.
  - Relationship - liên hệ với khái niệm khác: Đầu ra của Judge được dùng để kích hoạt Guardrail.
- Term - thuật ngữ: Rationale-First Pattern - Thiết kế ưu tiên lập luận
  - Meaning - nghĩa: Yêu cầu LLM tạo ra lời giải thích chi tiết trước khi đưa ra quyết định cuối cùng (điểm số, nhãn phân loại).
  - Why it matters - vì sao quan trọng: Giúp LLM xây dựng chuỗi suy nghĩ logic chính xác (Chain of Thought), tránh việc đưa ra quyết định sai rồi cố tình giải thích ngụy biện cho khớp với quyết định đó.
  - Relationship - liên hệ với khái niệm khác: Được cấu trúc thông qua thứ tự các thuộc tính trong Pydantic Class.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
Quy trình hoạt động chi tiết đầu-cuối:
- 1. Reporter Agent tạo báo cáo tài chính.
- 2. Giao diện Lambda của Reporter chuyển báo cáo, chỉ thị gốc và task gốc sang `judge.py`.
- 3. Hàm `evaluate()` khởi tạo Judge Agent với model Bedrock/Nova Pro.
- 4. Judge Agent phân tích, điền Rationale (`feedback`) trước, sau đó chấm điểm (`score`).
- 5. Trả kết quả về `lambda_handler.py`.
- 6. Đăng ký điểm số lên Langfuse bằng `span.score(name="Judge", value=score/100, comment=comment)`.
- 7. Nếu `score < 0.3`, Lambda thay thế toàn bộ báo cáo bằng văn bản fallback lỗi, ngược lại lưu báo cáo thành công vào Database.

## 7. Techniques - Kỹ thuật sử dụng
- Technique - kỹ thuật: Pydantic Schema Order - Thứ tự thuộc tính trong Pydantic
  - Purpose - mục đích: Ép buộc mô hình sinh ra rationale trước score trong định dạng JSON đầu ra.
  - When to use - dùng khi nào: Mọi trường hợp sử dụng Structured Outputs yêu cầu lập luận logic.
  - Trade-off - đánh đổi: Tăng thời gian và chi phí token cho phần văn bản giải thích.
  - Common mistake - lỗi dễ gặp: Để trường score trước feedback trong định nghĩa Pydantic class.

## 8. Code Walkthrough - Phân tích code nếu có
- File / block 1: `G:\AIProduction_t6_2026\production\week4\alex\backend\reporter\judge.py`
  - Purpose - mục đích: Định nghĩa class `Evaluation` và hàm `evaluate` để chấm điểm báo cáo.
  - Key logic - logic chính: Tạo class Pydantic Evaluation với thuộc tính feedback khai báo trước score để ép LLM lập luận trước.
  - Important lines / functions:
    - Dòng 10-16: Khai báo class `Evaluation` với `feedback` đứng trước `score`.
    - Dòng 54-58: Khởi tạo Agent và chạy bằng `Runner.run`.
- File / block 2: `G:\AIProduction_t6_2026\production\week4\alex\backend\reporter\lambda_handler.py`
  - Purpose - mục đích: Gọi logic chấm điểm của Judge và thực thi guardrail.
  - Key logic - logic chính: Chạy evaluate trong span `judge` của Langfuse, đẩy score thu được lên hệ thống Langfuse, chặn kết quả nếu score quá thấp.
  - Important lines / functions:
    - Dòng 73-79: Khởi động span `judge` và gọi `evaluate(...)`, đăng ký điểm số bằng `span.score(...)`.
    - Dòng 80-82: So sánh score với `GUARD_AGAINST_SCORE` (0.3) để thực hiện fallback.
  - Vietnamese inline notes:
    ```python
    # lambda_handler.py: Logic kiểm soát chất lượng bằng LLM-as-a-Judge
    if observability:
        with observability.start_as_current_span(name="judge") as span:
            # Gọi hàm evaluate từ judge.py để lấy kết quả chấm điểm
            evaluation = await evaluate(REPORTER_INSTRUCTIONS, task, response)
            score = evaluation.score / 100 # Quy đổi điểm về khoảng [0, 1]
            comment = evaluation.feedback
            
            # Ghi nhận điểm số này lên Langfuse trace để theo dõi trên dashboard
            span.score(name="Judge", value=score, data_type="NUMERIC", comment=comment)
            
            # Kích hoạt chốt chặn Guardrail nếu chất lượng báo cáo quá kém
            if score < GUARD_AGAINST_SCORE:
                logger.error(f"Reporter score is too low: {score}")
                # Thay thế báo cáo lỗi bằng thông báo an toàn cho khách hàng
                response = "I'm sorry, I'm not able to generate a report for you. Please try again later."
    ```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- Option: Chạy Judge trực tiếp trong luồng xử lý đồng bộ (Synchronous) của Lambda
  - Pros: Chặn ngay lập tức kết quả xấu trước khi lưu vào DB hoặc trả về cho khách hàng.
  - Cons: Tăng độ trễ (latency) của API thêm 10-15 giây do phải chạy thêm một lượt gọi LLM chấm điểm.
  - When to choose: Các ứng dụng yêu cầu kiểm soát chất lượng nghiêm ngặt ngay lập tức.
- Option: Chạy Judge bất đồng bộ (Asynchronous) thông qua SQS hoặc EventBridge
  - Pros: API phản hồi cực nhanh, không làm tăng latency của người dùng.
  - Cons: Khách hàng có thể nhìn thấy báo cáo lỗi trước khi Judge kịp chạy để ẩn hoặc thay thế nó.
  - When to choose: Hệ thống phân tích phi thời gian thực, xử lý hàng loạt (batch).

## 10. Pitfalls - Lỗi / bẫy thường gặp
- Failure mode: Điểm số của Judge không ổn định hoặc luôn chấm quá cao/quá thấp.
  - Root cause: Prompt chỉ thị cho Judge quá mơ hồ, thiếu các tiêu chuẩn chấm điểm cụ thể.
  - Symptom: Nhiều báo cáo tốt bị chặn nhầm, hoặc báo cáo rác vẫn vượt qua bộ lọc.
  - Fix / prevention: Cung cấp rubrics (thang chấm điểm) chi tiết trong prompt chỉ thị của Judge Agent, nêu rõ thế nào là báo cáo đạt điểm tối đa hoặc bị điểm tối thiểu.

## 11. Knowledge Extension - Kiến thức mở rộng
- G-Eval: Framework chấm điểm LLM-as-a-Judge hiện đại, định nghĩa các bước đánh giá chi tiết thông qua Chain of Thought và tính toán xác suất trung bình của các token điểm số để cho ra kết quả ổn định hơn chấm điểm đơn thuần.

## 12. Study Pack - Gói ôn tập
### Must remember
- Rationale-First: Đặt feedback trước score trong Pydantic class.
- LLM-as-a-judge sử dụng mô hình độc lập chấm điểm chất lượng.
- Cấu hình `GUARD_AGAINST_SCORE` mặc định là 30% (0.3).
- `span.score(...)` là API của Langfuse để ghi nhận điểm số đánh giá.

### Self-check questions
- Hãy giải thích cơ chế hoạt động của chốt chặn Guardrail trong `lambda_handler.py` khi điểm số của Judge dưới 0.3?
- Tại sao chúng ta cần chia score cho 100 trước khi đẩy lên Langfuse?

### Flashcards
- Q: Tên phương thức của span Langfuse dùng để ghi nhận điểm số đánh giá lên hệ thống là gì?
  A: span.score().

### Interview Q&A nếu phù hợp
- Q: Làm sao để kiểm chứng xem LLM-as-a-Judge có đang hoạt động chuẩn xác trong môi trường production?
  A: Theo dõi mục "Scores" trên Langfuse dashboard, đọc ngẫu nhiên (sampling check) các feedback và score để so sánh với đánh giá thủ công của con người (Human-in-the-loop).

## 13. Missing Inputs - Còn thiếu gì
Không có.

---

# 113. Day 4 - Real-Time Agent Monitoring and the Security Risks of Production AI

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: đã dùng
- Slide: đã dùng (Production W4D4.pdf - trang 5, 6)
- Code: đã dùng (watch_agents.py trong [backend/](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/watch_agents.py))
- Summary lịch sử: đã dùng (day3_summary.md)
- Ghi chú về độ tin cậy hoặc mâu thuẫn giữa nguồn: Các nguồn đồng nhất về cơ chế hoạt động của watch_agents script.

## 2. Executive Summary - Tóm tắt cốt lõi
- Hướng dẫn thực hành sử dụng script giám sát log thời gian thực `watch_agents.py` thông qua AWS CLI để theo dõi đồng thời log hoạt động của cả 5 agents.
- Sử dụng các mã màu ANSI khác nhau để phân biệt dòng log của từng agent (ví dụ: Planner màu xanh dương, Reporter màu xanh lá, các log Langfuse màu tím).
- Giới thiệu khái niệm bảo mật đặc thù của Agentic AI: **Lethal Trifecta - Tam giác hiểm họa**.
- Phân tích nguyên lý của Lethal Trifecta: Một hệ thống AI Agent sẽ cực kỳ nguy hiểm nếu sở hữu đồng thời cả 3 khả năng:
  1. Access to private data (Truy cập dữ liệu nhạy cảm/riêng tư).
  2. Access to untrusted content (Đọc nội dung không đáng tin cậy bên ngoài).
  3. Ability to communicate externally (Khả năng truyền thông tin ra bên ngoài).

## 3. Lesson Goals - Mục tiêu bài học
- Concept goals - mục tiêu kiến thức: Hiểu cơ chế hoạt động giám sát log thời gian thực thông qua AWS CloudWatch Logs API. Nắm được định nghĩa và các góc cạnh của mô hình bảo mật Lethal Trifecta.
- Practical goals - mục tiêu thực hành: Chạy thành công tiện ích `watch_agents.py` và theo dõi quá trình chạy thực tế của các agent.
- What learner should be able to explain - người học cần giải thích được: Tại sao việc sở hữu đồng thời cả 3 yếu tố của Lethal Trifecta lại tạo ra lỗ hổng bảo mật nghiêm trọng cho Agent.

## 4. Previous Context - Liên hệ với bài trước
Bài học sử dụng hạ tầng Lambda của Day 2 và các thiết lập API của các bài học trước để làm bối cảnh phân tích.

## 5. Core Theory - Lý thuyết cốt lõi
- Term - thuật ngữ: Lethal Trifecta - Tam giác hiểm họa bảo mật
  - Meaning - nghĩa: Mô hình bảo mật chỉ ra nguy cơ rò rỉ hoặc phá hoại dữ liệu khi một AI Agent có cả quyền đọc dữ liệu riêng tư, nhận dữ liệu đầu vào không kiểm soát từ công chúng, và gửi dữ liệu ra internet.
  - Why it matters - vì sao quan trọng: Giúp các kiến trúc sư bảo mật đánh giá rủi ro và thiết lập các chốt chặn cô lập (isolation) cho hệ thống agent.
  - Relationship - liên hệ với khái niệm khác: Bất kỳ góc nào của tam giác bị bẻ gãy (ví dụ: cấm gọi internet) sẽ vô hiệu hóa mối đe dọa này.
- Term - thuật ngữ: Real-Time Log Tailing - Theo dõi log thời gian thực
  - Meaning - nghĩa: Cơ chế liên tục đọc và in ra các dòng log mới nhất được đẩy lên máy chủ CloudWatch từ các container Lambda đang thực thi.
  - Why it matters - vì sao quan trọng: Tiết kiệm thời gian debug cho lập trình viên, không cần click tay load lại trang CloudWatch Console.
  - Relationship - liên hệ với khái niệm khác: Được hiện thực hóa qua lệnh `aws logs tail` chạy nền trong Python script.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
Quy trình hoạt động chi tiết của Watch Agents:
- 1. Lập trình viên chạy lệnh `uv run watch_agents.py`.
- 2. Script thiết lập kết nối AWS SDK và gọi lệnh `aws logs tail` cho 5 log groups tương ứng.
- 3. Khi người dùng click phân tích trên UI, Planner Lambda kích hoạt.
- 4. Log của Planner lập tức xuất hiện trên terminal dưới dạng chữ màu xanh dương.
- 5. Planner gọi song song các agent khác, log của các agent xuất hiện đồng thời với các màu tương ứng (Reporter màu xanh lá, Charter màu vàng, Retirement màu đỏ).
- 6. Cuối cùng, log Langfuse (màu tím) xuất hiện thông báo trace đã flush hoàn tất.

## 7. Techniques - Kỹ thuật sử dụng
- Technique - kỹ thuật: ANSI Color Log Separation - Phân tách log bằng mã màu ANSI
  - Purpose - mục đích: Tăng khả năng quét thông tin bằng mắt thường của lập trình viên khi giám sát nhiều tiến trình đồng thời.
  - When to use - dùng khi nào: Giám sát log trong môi trường phân tán (multi-agent, microservices).
  - Trade-off - đánh đổi: Terminal phải hỗ trợ hiển thị màu ANSI.
  - Common mistake - lỗi dễ gặp: Quên không reset màu bằng mã `\033[0m`, khiến toàn bộ log phía sau bị đổi màu hàng loạt.

## 8. Code Walkthrough - Phân tích code nếu có
- File / block: `G:\AIProduction_t6_2026\production\week4\alex\backend\watch_agents.py`
- Purpose - mục đích: Script tiện ích giám sát đồng thời nhiều log group của Lambda agent trên CloudWatch.
- Key logic - logic chính: Sử dụng subprocess gọi lệnh `aws logs tail` cho các log groups `/aws/lambda/alex-planner`, v.v. Áp dụng bảng màu `ansi_colors` để in ra màn hình dòng log tương ứng.
- Important lines / functions:
  - Khai báo danh sách các Log Groups của 5 agents Lambda.
  - Áp dụng các màu sắc ANSI (ví dụ: `\033[94m` cho Planner, `\033[92m` cho Reporter) để phân biệt output.
- Vietnamese inline notes:
  ```python
  # watch_agents.py: Cú pháp in log có màu sắc phân biệt
  # \033[94m thiết lập màu xanh dương cho log của Planner orchestrator
  # \033[0m reset màu sắc về mặc định sau khi in dòng log
  print(f"\033[94m[PLANNER] {log_message}\033[0m")
  ```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- Option: Giám sát log qua CLI Tool `watch_agents.py`
  - Pros: Nhanh, nhẹ, hiển thị màu sắc rõ ràng, cập nhật thời gian thực ngay trên terminal phát triển.
  - Cons: Khó lưu trữ lịch sử lâu dài, không hỗ trợ tìm kiếm phức tạp như giao diện web.
  - When to choose: Trong quá trình phát triển (development) và debug trực tiếp.
- Option: Giám sát log qua CloudWatch Logs Insights / OpenSearch
  - Pros: Hỗ trợ truy vấn SQL/KQL mạnh mẽ, lưu trữ lâu dài, phân tích biểu đồ.
  - Cons: Độ trễ cao hơn một chút, giao diện nặng hơn.
  - When to choose: Giám sát vận hành trong môi trường production thực tế.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- Failure mode: Script watch_agents.py báo lỗi lệnh `aws` hoặc `aws logs tail` không tồn tại.
  - Root cause: Lập trình viên chưa cài đặt AWS CLI trên máy hoặc chưa thiết lập AWS credentials.
  - Symptom: Script báo lỗi thực thi dòng lệnh hệ thống.
  - Fix / prevention: Cài đặt AWS CLI và chạy `aws configure` để đăng nhập bằng IAM user `aiengineer`.

## 11. Knowledge Extension - Kiến thức mở rộng
- ANSI Escape Codes: Là một tiêu chuẩn truyền tín hiệu điều khiển bằng chuỗi ký tự đặc biệt được gửi kèm văn bản vào terminal để thay đổi màu sắc, vị trí con trỏ hoặc font chữ của terminal hiển thị.

## 12. Study Pack - Gói ôn tập
### Must remember
- Script `watch_agents.py` tail log CloudWatch từ cả 5 agents Lambda.
- ANSI escape codes được dùng để tô màu log dòng lệnh.
- Lethal Trifecta gồm: Private Data + Untrusted Content + External Communication.
- Phá vỡ bất kỳ đỉnh nào của Lethal Trifecta sẽ ngăn chặn được lỗ hổng bảo mật nghiêm trọng.

### Self-check questions
- Trình bày 3 yếu tố cấu thành nên mô hình bảo mật Lethal Trifecta?
- Làm thế nào để script watch_agents phân biệt log từ các nguồn Lambda khác nhau?

### Flashcards
- Q: Ba đỉnh của tam giác hiểm họa bảo mật "Lethal Trifecta" là gì?
  A: Đọc dữ liệu riêng tư, Nhận dữ liệu không tin cậy, Giao tiếp ra ngoài.

### Interview Q&A nếu phù hợp
- Q: Làm thế nào để bẻ gãy mô hình Lethal Trifecta trong một ứng dụng AI Agent bắt buộc phải đọc dữ liệu riêng tư của người dùng?
  A: Cô lập mạng lưới (Network Isolation): Chặn hoàn toàn khả năng gọi internet ra bên ngoài của Agent Lambda (không cấp NAT Gateway trong VPC), hoặc chỉ cho phép kết nối tới các tên miền whitelist được kiểm duyệt chặt chẽ.

## 13. Missing Inputs - Còn thiếu gì
Không có.

---

# 114. Day 4 - Securing AI Agents Against Prompt Injection in Production Systems

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: đã dùng
- Slide: đã dùng (Production W4D4.pdf - trang 6)
- Code: không có code trực tiếp cho lesson này
- Summary lịch sử: đã dùng (day3_summary.md)
- Ghi chú về độ tin cậy hoặc mâu thuẫn giữa nguồn: Các nguồn nhất quán về lỗ hổng bảo mật của GitHub MCP Server.

## 2. Executive Summary - Tóm tắt cốt lõi
- Nghiên cứu sâu về lỗ hổng Prompt Injection thông qua trường hợp thực tế (case study) của GitHub MCP Server.
- Giải thích kịch bản tấn công rò rỉ dữ liệu (data exfiltration): Kẻ tấn công gửi prompt injection qua một issue công khai trên GitHub public repo -> Agent đọc issue này và bị jailbreak -> Agent được lệnh đọc file nhạy cảm ở private repo -> Agent viết nội dung file đó vào một issue công khai khác để rò rỉ thông tin ra ngoài.
- Phân tích và đánh giá ứng dụng Alex đối với mô hình Lethal Trifecta:
  - 1. Private Data: Có (Alex đọc portfolio của người dùng).
  - 2. Untrusted Content: Có (Ticker symbols hoặc cash balance do người dùng nhập vào hệ thống).
  - 3. External Communication: Có (trả báo cáo về cho client).
- Kết luận mức độ an toàn của Alex: Alex an toàn vì luồng giao tiếp ngoài chỉ trả về cho chính user đang đăng nhập và hệ thống kiểm soát cơ sở dữ liệu cứng bằng code (luôn truy vấn theo `clerk_user_id`), không cho phép Agent tự do truy vấn chéo dữ liệu của các user khác.

## 3. Lesson Goals - Mục tiêu bài học
- Concept goals - mục tiêu kiến thức: Hiểu cơ chế tấn công gián tiếp qua Prompt Injection (Indirect Prompt Injection). Nắm được cách thiết kế cơ sở dữ liệu và API phân quyền để bảo vệ agent.
- Practical goals - mục tiêu thực hành: Biết cách phân tích và đánh giá lỗ hổng bảo mật của một dự án Agent thực tế dựa trên mô hình Lethal Trifecta.
- What learner should be able to explain - người học cần giải thích được: Tại sao phân quyền ở cấp cơ sở dữ liệu (Database-level authorization) lại là lớp phòng thủ tối hậu cho AI Agent.

## 4. Previous Context - Liên hệ với bài trước
Tiếp nối phần lý thuyết về bảo mật và Lethal Trifecta ở bài 113 để thực hành phân tích trực tiếp trên kiến trúc của Alex.

## 5. Core Theory - Lý thuyết cốt lõi
- Term - thuật ngữ: Indirect Prompt Injection - Tấn công tiêm prompt gián tiếp
  - Meaning - nghĩa: Cuộc tấn công xảy ra khi AI Agent đọc một tài liệu từ nguồn bên ngoài (như email, trang web, GitHub issue) có chứa mã lệnh độc hại do kẻ tấn công cài cắm sẵn, chứ không phải do người dùng trực tiếp nhập lệnh vào chatbox.
  - Why it matters - vì sao quan trọng: Đây là lỗ hổng rất khó phát hiện vì Agent tự động đi lấy dữ liệu từ các nguồn tưởng chừng như vô hại.
  - Relationship - liên hệ với khái niệm khác: Là cơ chế chính trong vụ tấn công lỗ hổng GitHub MCP Server.
- Term - thuật ngữ: Data Exfiltration - Rò rỉ dữ liệu ra ngoài trái phép
  - Meaning - nghĩa: Hành vi chuyển dữ liệu nhạy cảm từ mạng nội bộ hoặc hệ thống bảo mật ra môi trường internet công cộng mà không được phép.
  - Why it matters - vì sao quan trọng: Mục tiêu tối hậu của các cuộc tấn công đánh cắp thông tin bí mật doanh nghiệp hoặc người dùng.
  - Relationship - liên hệ với khái niệm khác: Bước thứ 3 trong kịch bản tấn công của tam giác hiểm họa.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
Kịch bản tấn công Indirect Prompt Injection trên GitHub MCP:
- 1. Kẻ tấn công ghi prompt injection độc hại vào Public Issue -> 2. Scheduled task của Agent quét qua Public Issues -> 3. Lệnh injection ghi đè prompt hệ thống -> 4. Agent gọi API của GitHub để đọc Private codebase -> 5. Agent viết nội dung file nhạy cảm vào một Public Issue mới -> 6. Dữ liệu nhạy cảm bị rò rỉ ra thế giới bên ngoài.

## 7. Techniques - Kỹ thuật sử dụng
- Technique - kỹ thuật: Database-Level Isolation - Cô lập ở cấp cơ sở dữ liệu
  - Purpose - mục đích: Đảm bảo một phiên làm việc của Agent chỉ có thể truy cập dữ liệu của chính người dùng hiện tại thông qua các ràng buộc khóa ngoại cứng.
  - When to use - dùng khi nào: Áp dụng cho mọi ứng dụng đa người dùng (SaaS multi-tenant).
  - Trade-off - đánh đổi: Giảm bớt tính linh hoạt khi Agent cần thực hiện các phân tích tổng hợp dữ liệu lớn.

## 8. Code Walkthrough - Phân tích code nếu có
`Buổi học này không có code được cung cấp`. (Bài học tập trung vào phân tích kiến trúc bảo mật lý thuyết).

## 9. Options / Trade-offs - Bản đồ lựa chọn
Bài học bảo mật này không đưa ra các lựa chọn công nghệ so sánh trực tiếp.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- Failure mode: Kẻ tấn công thực hiện SQL Injection kết hợp Prompt Injection để đọc trộm dữ liệu toàn hệ thống.
  - Root cause: Agent được cấp quyền truy cập cơ sở dữ liệu quá rộng (ví dụ: dùng chung tài khoản DB admin) và các câu lệnh SQL được xây dựng bằng cách nối chuỗi văn bản tự do (string concatenation) thay vì parameterized queries.
  - Symptom: Lộ dữ liệu của các tài khoản người dùng khác.
  - Fix / prevention: Luôn truyền tham số truy vấn (`clerk_user_id`) cứng từ API gateway vào Lambda của Agent, cấm Agent tự do sinh câu lệnh SQL tùy biến không qua kiểm duyệt tham số.

## 11. Knowledge Extension - Kiến thức mở rộng
- OAuth 2.0 cho MCP: Các giao thức kết nối MCP hiện đại đang tích hợp OAuth 2.0 để xác thực quyền hạn của người dùng đối với từng dịch vụ cụ thể (như Jira, Github), giúp hạn chế việc một token dev duy nhất có quyền hạn quá lớn gây rủi ro bảo mật.

## 12. Study Pack - Gói ôn tập
### Must remember
- GitHub MCP vulnerability là ví dụ điển hình của Indirect Prompt Injection.
- Alex an toàn vì kiểm soát phân quyền dữ liệu bằng code cứng ở backend API theo `clerk_user_id`.
- Phải luôn thiết kế tách biệt quyền hạn truy cập của token (Principle of Least Privilege).
- Dữ liệu do người dùng nhập (như ETF tickers) có thể là nguồn tiêm prompt.

### Self-check questions
- Tại sao vụ tấn công GitHub MCP lại cần đến cả 3 yếu tố của Lethal Trifecta?
- Làm thế nào Alex ngăn chặn việc Agent đọc dữ liệu của người dùng khác?

### Flashcards
- Q: Kiểu tấn công prompt injection xảy ra khi agent đọc dữ liệu từ nguồn bên ngoài (ví dụ: web, email) gọi là gì?
  A: Indirect Prompt Injection (Tiêm prompt gián tiếp).

### Interview Q&A nếu phù hợp
- Q: Bạn sẽ thiết kế hệ thống thế nào để chống lại lỗ hổng bảo mật khi tích hợp một MCP server bên thứ ba vào hệ thống của mình?
  A: Thực hiện kiểm duyệt mã nguồn MCP server, chạy server trong sandbox/container riêng lẻ, giới hạn quyền của API token gắn với MCP server đó và chặn kết nối internet không cần thiết.

## 13. Missing Inputs - Còn thiếu gì
Không có.

---

# 115. Day 4 - Capstone Assignment - Taking Your AI Financial Agent to Market

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: đã dùng
- Slide: đã dùng (Production W4D4.pdf - trang 7, 8, 9)
- Code: không có code trực tiếp cho lesson này
- Summary lịch sử: đã dùng (day3_summary.md)
- Ghi chú về độ tin cậy hoặc mâu thuẫn giữa nguồn: Các nguồn nhất quán về định hướng phát triển bài tập lớn Capstone.

## 2. Executive Summary - Tóm tắt cốt lõi
- Bài học kết thúc ngày thứ tư, đồng thời giao bài tập lớn Capstone Assignment để học viên tự do phát triển hệ thống Alex theo 3 hướng chuyên sâu.
- Nhánh 1 - Data Engineering: Kết nối dữ liệu ingestion của tuần trước với danh mục đầu tư thực tế của tuần này. Giúp Researcher Agent chỉ tìm kiếm tin tức liên quan đến các ETF/cổ phiếu thực tế có trong tài khoản của user thay vì tìm kiếm chung chung.
- Nhánh 2 - MLOps: Cài đặt nâng cao các bộ giám sát CloudWatch Alarms, tích hợp sâu Langfuse để theo dõi độ lệch mô hình (model drift) và thiết kế thêm các chốt chặn LLM-as-a-Judge.
- Nhánh 3 - Agentic AI: Nâng cao chất lượng tư vấn tài chính của Agent bằng cách tối ưu Prompt/Context Engineering, tạo ra sự phụ thuộc và trao đổi thông tin sâu sắc giữa 5 agent (ví dụ: Retirement Agent đọc dữ liệu của Reporter Agent thay vì chạy độc lập).
- Hướng dẫn học viên đóng góp bài làm của mình vào thư mục `production/community_contributions` của khóa học để chia sẻ với cộng đồng.

## 3. Lesson Goals - Mục tiêu bài học
- Concept goals - mục tiêu kiến thức: Hiểu cách phát triển một sản phẩm AI Agent từ nguyên mẫu thử nghiệm (seed/kernel) thành một sản phẩm thương mại có khả năng tạo doanh thu.
- Practical goals - mục tiêu thực hành: Lập kế hoạch phát triển Capstone Project theo một trong ba định hướng nghề nghiệp (Data Engineer, MLOps Engineer, AI Agent Engineer).
- What learner should be able to explain - người học cần giải thích được: Cách kết nối các thành phần Agent độc lập thành một quy trình cộng tác có chiều sâu (agent collaboration dependencies).

## 4. Previous Context - Liên hệ với bài trước
Tổng kết lại toàn bộ kiến thức của Tuần 3 (Data/SageMaker/S3 Vectors) và Tuần 4 (Database/Agents/Frontend/Enterprise).

## 5. Core Theory - Lý thuyết cốt lõi
- Term - thuật ngữ: Agent Collaboration Dependency - Sự phụ thuộc cộng tác giữa các Agent
  - Meaning - nghĩa: Mô hình hoạt động trong đó đầu ra của một Agent này (ví dụ: Reporter) được sử dụng làm thông tin ngữ cảnh đầu vào cho một Agent khác (ví dụ: Retirement), tạo thành chuỗi liên kết thông tin.
  - Why it matters - vì sao quan trọng: Giúp các agent phối hợp đồng bộ, đưa ra kết quả phân tích thống nhất thay vì đưa ra các kết quả rời rạc, mâu thuẫn nhau.
  - Relationship - liên hệ với khái niệm khác: Cải tiến từ kiến trúc chạy song song độc lập (parallel processing) hiện tại của Day 2.
- Term - thuật ngữ: Model Drift Tracking - Theo dõi độ lệch mô hình
  - Meaning - nghĩa: Quá trình theo dõi và giám sát xem chất lượng hoặc hành vi của mô hình ngôn ngữ có bị thay đổi hoặc suy giảm theo thời gian hay không.
  - Why it matters - vì sao quan trọng: Phát hiện sớm lỗi khi nhà cung cấp cập nhật mô hình hoặc thói quen nhập liệu của người dùng thay đổi.
  - Relationship - liên hệ với khái niệm khác: Được thực hiện bằng cách lưu trữ và thống kê điểm số chấm điểm của Judge trong Langfuse.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
Quy trình phát triển Capstone (luồng tư duy):
- 1. Lựa chọn nhánh chuyên sâu phù hợp -> 2. Tối ưu hóa code và cấu hình hạ tầng AWS -> 3. Thực hiện kiểm thử tích hợp hệ thống -> 4. Đóng góp PR hoặc deploy thương mại hóa thực tế.

## 7. Techniques - Kỹ thuật sử dụng
- Technique - kỹ thuật: Context Engineering for Finance - Thiết kế ngữ cảnh cho tài chính
  - Purpose - mục đích: Cung cấp cho LLM các kiến thức chuyên môn, công thức tính toán tài chính chuẩn xác (ví dụ: Monte Carlo, quy tắc 4% rút tiền).
  - When to use - dùng khi nào: Khi xây dựng các agent tư vấn tài chính chuyên nghiệp.
  - Trade-off - đánh đổi: Đòi hỏi kiến thức chuyên ngành sâu sắc và tăng độ dài của prompt.
  - Common mistake - lỗi dễ gặp: Viết prompt chung chung không có các chỉ dẫn ràng buộc về số liệu toán học.

## 8. Code Walkthrough - Phân tích code nếu có
`Buổi học này không có code được cung cấp`. (Bài học hướng dẫn thực hiện bài tập lớn kết khóa).

## 9. Options / Trade-offs - Bản đồ lựa chọn
- Option: Nhánh Data Engineering
  - Pros: Rất tốt cho người muốn làm về data pipelines, web scraping, vector indexing quy mô lớn.
  - Cons: Ít tập trung vào logic Agentic AI và UI.
  - When to choose: Phù hợp định hướng Data Engineer.
- Option: Nhánh MLOps
  - Pros: Phù hợp với người muốn vận hành, bảo mật và tối ưu chi phí Cloud/AI ở quy mô doanh nghiệp.
  - Cons: Không tạo ra thêm các tính năng thông minh mới cho người dùng cuối.
  - When to choose: Phù hợp định hướng MLOps / Platform Engineer.
- Option: Nhánh Agentic AI (Ed Donner khuyến nghị)
  - Pros: Tạo ra sản phẩm có giá trị thương mại cao, cải tiến trực tiếp trải nghiệm và chất lượng tư vấn của Alex để có thể monetized (kiếm tiền).
  - Cons: Logic prompt phức tạp, dễ xảy ra lỗi hallucination nếu không kiểm soát tốt.
  - When to choose: Phù hợp định hướng AI Engineer.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- Failure mode: Sản phẩm Capstone hoạt động tốt ở local nhưng lỗi 500 khi chạy trên AWS Lambda.
  - Root cause: Quên không chạy `package_docker.py` hoặc `deploy_all_lambdas.py` để đóng gói và cập nhật mã nguồn mới lên AWS.
  - Symptom: UI báo lỗi phân tích, CloudWatch ghi nhận lỗi import hoặc thiếu file/thư viện.
  - Fix / prevention: Luôn tuân thủ quy trình đóng gói bằng Docker và deploy Lambda mỗi khi thay đổi code backend.

## 11. Knowledge Extension - Kiến thức mở rộng
- Clerk Subscription Tiers: Clerk cung cấp các tính năng quản lý metadata của người dùng (publicMetadata) giúp nhà phát triển lưu trữ phân hạng tài khoản (Free, Pro, Premium) để giới hạn số lượt gọi phân tích tài chính của Agent tùy theo cấp độ thanh toán.

## 12. Study Pack - Gói ôn tập
### Must remember
- Capstone Assignment có 3 nhánh: Data Engineering, MLOps, Agentic AI.
- Ed Donner khuyến khích cải thiện chất lượng AI của Alex để thương mại hóa sản phẩm.
- Cần kết nối dữ liệu Research của tuần trước với ETF tickers thực tế của user.
- Các agent hiện tại đang chạy song song cô lập, cần thiết kế sự phụ thuộc (dependency) giữa chúng.

### Self-check questions
- Hãy trình bày ý tưởng kết nối Data Ingestion pipeline của Tuần 3 với Portfolio của Tuần 4?
- Làm thế nào để cải thiện tính liên kết dữ liệu giữa Reporter Agent và Retirement Agent?

### Flashcards
- Q: Nhánh Capstone nào tập trung vào việc theo dõi model drift và cấu hình CloudWatch Alarms nâng cao?
  A: MLOps.

### Interview Q&A nếu phù hợp
- Q: Làm sao để tích hợp thanh toán gói cước thành viên (SaaS) cho Alex?
  A: Sử dụng Clerk metadata để gắn phân hạng tài khoản và Stripe API để xử lý thanh toán, sau đó kiểm tra quyền hạn của user trong backend Lambda API trước khi gửi phân tích.

## 13. Missing Inputs - Còn thiếu gì
Không có.
