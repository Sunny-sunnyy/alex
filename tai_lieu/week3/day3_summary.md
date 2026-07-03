# 74. Day 3 - Building ALEX - Multi-Agent Financial AI System on AWS Infrastructure

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [74. Day 3 - Building ALEX - Multi-Agent Financial AI System on AWS Infrastructure.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/74.%20Day%203%20-%20Building%20ALEX%20-%20Multi-Agent%20Financial%20AI%20System%20on%20AWS%20Infrastructure.txt) - Đã dùng
- Slide: [Production W3D3.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D3.pdf) - Đã dùng
- Code: [gameplan.md](file:///G:/AIProduction_t6_2026/production/week3/alex/gameplan.md) - Đã dùng
- Summary lịch sử: Không có (Đây là ngày học đầu tiên của dự án Alex).

## 2. Executive Summary - Tóm tắt cốt lõi
- Khóa học quay trở lại với AWS để bắt đầu xây dựng dự án lớn nhất khóa học: **Alex** (Agentic Learning Equities eXplainer) - một nền tảng SaaS lập kế hoạch tài chính cá nhân sử dụng hệ thống AI đa tác tử.
- Alex phân tích danh mục đầu tư (equity portfolio), đánh giá mức độ đa dạng hóa, đưa ra dự báo tài chính nghỉ hưu và đề xuất các hành động cụ thể để tối ưu hóa tài sản.
- Cấu trúc thư mục của Alex bao gồm: `backend/` (các service Python và Lambda cho tác tử), `frontend/` (mã nguồn ứng dụng NextJS React), `guides/` (tài liệu hướng dẫn từng bước), `terraform/` (quản lý hạ tầng độc lập) và `scripts/` (các kịch bản triển khai).
- Thay vì sử dụng một cấu hình Terraform lớn duy nhất, dự án chia thành các thư mục Terraform độc lập tương ứng với từng ngày học. Mỗi thư mục có file trạng thái cục bộ (`terraform.tfstate`) riêng để cô lập rủi ro và dễ dàng triển khai/dọn dẹp hạ tầng.
- Nhắc nhở kiểm tra chi phí AWS thường xuyên trong trang **Billing & Cost Management** của tài khoản root để tránh phát sinh chi phí ngoài ý muốn từ các dịch vụ chạy ẩn.
- Giới thiệu file `gameplan.md` ở thư mục gốc của Alex, đóng vai trò như một tài liệu briefing (cung cấp ngữ cảnh) hoàn chỉnh cho AI coding assistants (như Claude Code hoặc Cursor Agents) để hỗ trợ quá trình sửa lỗi nhanh chóng.
- Hệ thống Alex được cấu hình triển khai thẳng lên một môi trường sản phẩm (production environment) duy nhất và không tích hợp sẵn CI/CD qua GitHub Actions để tập trung tối đa vào kiến trúc AI đa tác tử và hạ tầng serverless của AWS.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu ý nghĩa tên gọi và mục tiêu thương mại của ứng dụng SaaS tài chính Alex.
  - Hiểu sơ bộ về cấu trúc mã nguồn và hạ tầng độc lập của dự án Alex.
  - Hiểu lý do tại sao khóa học chọn phương án phân tách các thư mục Terraform và lưu trữ state cục bộ.
- **Practical goals - mục tiêu thực hành**:
  - Thực hành kiểm tra chi phí và đóng các tài nguyên dư thừa trên AWS, Azure và GCP.
  - Clone dự án Alex từ repository và mở dự án trong IDE Cursor.
  - Khám phá các thư mục chính và khởi động thử công cụ Claude Code (nếu có cài đặt).
- **What learner should be able to explain - người học cần giải thích được**:
  - Alex viết tắt của từ gì và nó giải quyết bài toán gì cho người dùng.
  - Ưu và nhược điểm của việc chia nhỏ cấu hình hạ tầng Terraform thành từng thư mục độc lập.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này mở đầu cho dự án capstone kéo dài một tuần rưỡi. Nó liên kết trực tiếp các kiến thức hạ tầng AWS đã học ở hai tuần trước:
  - Tuần 1: Sử dụng App Runner cho các dịch vụ web dạng container (giống App Runner của Research Agent).
  - Tuần 2: Sử dụng AWS Lambda và kiến trúc không máy chủ (giống mô hình các tác tử phân tích).

## 5. Core Theory - Lý thuyết cốt lõi
- **Multi-agent collaboration (cộng tác đa tác tử)**: Mô hình thiết kế hệ thống AI sử dụng nhiều tác tử thông minh chuyên biệt (Planner, Tagger, Reporter, Charter, Retirement) phối hợp với nhau thông qua hàng đợi tin nhắn (SQS) và cơ sở dữ liệu chung để giải quyết các tác vụ phức tạp.
- **Serverless architecture (kiến trúc không máy chủ)**: Mô hình vận hành ứng dụng trong đó nhà cung cấp đám mây tự động quản lý việc cấp phát tài nguyên tính toán (như AWS Lambda, App Runner). Người dùng chỉ trả tiền cho thời gian chạy thực tế của mã nguồn và hệ thống tự động co giãn về 0 khi không có yêu cầu.
- **Independent Terraform state (trạng thái Terraform độc lập)**: Cơ chế cô lập tệp tin `.tfstate` của từng phần hạ tầng. Mỗi thư mục chứa một file state riêng, giúp tránh ảnh hưởng chéo khi xảy ra lỗi cấu hình trong một thành phần cụ thể.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
`Không có pipeline rõ ràng trong tài liệu nguồn`
Thay vào đó, bài học mô tả luồng thiết lập ban đầu của lập trình viên:
1. Đăng nhập tài khoản AWS root để kiểm tra chi phí Billing.
2. Di chuyển ra ngoài thư mục `production` để vào thư mục chứa các dự án (`projects`).
3. Thực hiện lệnh Git Clone để tải mã nguồn dự án Alex về máy.
4. Sử dụng Cursor để mở thư mục dự án Alex vừa clone.
5. Kiểm tra cấu trúc thư mục của dự án và khởi chạy thử AI Assistant để đọc hiểu cấu cảnh thông qua tệp tin `gameplan.md`.

## 7. Techniques - Kỹ thuật sử dụng
- **Infrastructure Modularization (Mô-đun hóa hạ tầng)**:
  - Purpose (mục đích): Chia tách các tài nguyên AWS thành các khối nhỏ độc lập.
  - When to use (dùng khi nào): Khi xây dựng các hệ thống lớn có các thành phần ít liên kết chặt chẽ hoặc trong quá trình giảng dạy/học tập để triển khai từng bước.
  - Trade-off (đánh đổi): Không tự động đồng bộ hóa các biến đầu ra (outputs) giữa các khối hạ tầng; nhà phát triển phải cấu hình thủ công các biến liên kết.
  - Common mistake (lỗi dễ gặp): Chạy lệnh apply sai thư mục làm lệch pha trạng thái tài nguyên thực tế trên AWS.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`
(Các tệp tin cấu hình và mã nguồn nghiệp vụ sẽ được phân tích chi tiết trong các bài học sau khi bắt đầu triển khai).

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Triển khai hạ tầng Alex bằng một tệp cấu hình Terraform duy nhất**
  - Pros: Liên kết biến tự động, triển khai toàn bộ hệ thống chỉ bằng một câu lệnh `terraform apply`.
  - Cons: Rất khó gỡ lỗi khi có lỗi phát sinh, khó kiểm soát chi phí trong quá trình học do phải khởi tạo đồng loạt nhiều tài nguyên đắt đỏ.
  - When to choose: Các dự án thực tế đã hoàn thiện kiến trúc hạ tầng và cần triển khai nhanh lên môi trường staging/production.
- **Option 2: Triển khai bằng nhiều thư mục độc lập (Lựa chọn của khóa học)**
  - Pros: Giúp người học làm quen từng dịch vụ một, cô lập lỗi tốt, có thể phá hủy (destroy) tài nguyên của từng ngày học để tiết kiệm chi phí.
  - Cons: Cần cấu hình lặp lại các biến dùng chung (như AWS region, Account ID) trong tệp tin cấu hình của mỗi thư mục.
  - When to choose: (Recommended) Các khóa học thực hành, môi trường thử nghiệm nâng cấp hạ tầng từng phần.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Lệch trạng thái hạ tầng (Terraform State Out-of-sync).
  - Root cause: Ngắt đột ngột (Ctrl+C) hoặc mất mạng khi Terraform đang triển khai một tài nguyên tốn thời gian như SageMaker (mất 3-5 phút).
  - Symptom: Lần apply tiếp theo sẽ báo lỗi tài nguyên đã tồn tại trong AWS nhưng Terraform không quản lý nó trong tệp `.tfstate`.
  - Fix / prevention: Không ngắt lệnh Terraform giữa chừng. Nếu gặp lỗi, chạy lệnh `terraform import` để kéo tài nguyên đó vào tệp state cục bộ hoặc xóa thủ công tài nguyên trên AWS Console trước khi chạy lại.

## 11. Knowledge Extension - Kiến thức mở rộng
- **Remote Backend trong môi trường thực tế**: Trong thực tế doanh nghiệp, file `terraform.tfstate` không bao giờ được lưu trữ cục bộ (local). Nó được lưu trên các dịch vụ lưu trữ đám mây như AWS S3 kết hợp với DynamoDB để khóa trạng thái (state locking). Điều này ngăn chặn việc hai lập trình viên cùng áp dụng hạ tầng một lúc dẫn đến hỏng trạng thái hạ tầng, đồng thời bảo mật các thông tin nhạy cảm của hệ thống.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Alex viết tắt của **Agentic Learning Equities eXplainer**.
2. Dự án Alex được tổ chức hạ tầng Terraform thành nhiều thư mục độc lập để hỗ trợ triển khai từng bước.
3. Tệp tin trạng thái hạ tầng `terraform.tfstate` được lưu cục bộ và cấu hình gitignored để bảo mật.
4. Lập trình viên nên kiểm tra chi phí AWS thường xuyên trong trang Billing của root user.
5. Dự án Alex triển khai trực tiếp lên môi trường sản phẩm mà không qua các môi trường trung gian.

### Self-check questions
1. Alex là ứng dụng gì và nó hỗ trợ những tính năng chính nào?
2. Tại sao khóa học lại sử dụng cấu trúc thư mục Terraform độc lập thay vì một tập lệnh lớn duy nhất?
3. File `gameplan.md` ở thư mục gốc của dự án dùng để làm gì?
4. Những thành phần chính trong thư mục `backend/` của Alex là gì?
5. Việc thiếu các môi trường phát triển (development/test environment) trong dự án Alex mang lại lợi ích và hạn chế gì?

### Flashcards
- Q: Alex hoạt động như một loại ứng dụng nào?
  A: Ứng dụng SaaS thương mại cung cấp dịch vụ lập kế hoạch tài chính cá nhân sử dụng AI đa tác tử.
- Q: Tệp tin `terraform.tfstate` cục bộ chứa thông tin gì?
  A: Chứa bản ghi chi tiết các tài nguyên hạ tầng đã được tạo trên AWS, bao gồm cả các thông tin cấu hình nhạy cảm.

### Interview Q&A nếu phù hợp
- Q: Làm thế nào để giải quyết vấn đề chia sẻ biến đầu ra (outputs) giữa các thư mục Terraform độc lập khi xây dựng hạ tầng dự án Alex?
  A: Có hai cách giải quyết chính: Cách đơn giản nhất (được dùng trong khóa học) là sao chép thủ công các giá trị đầu ra (như ARN, endpoint name) vào file biến `terraform.tfvars` của thư mục tiếp theo. Trong thực tế sản xuất, lập trình viên sẽ sử dụng dữ liệu nguồn `terraform_remote_state` để đọc trạng thái trực tiếp từ bucket S3 của mô-đun hạ tầng khác.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 75. Day 3 - Setting Up AWS Permissions and SageMaker for Production AI Agents

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [75. Day 3 - Setting Up AWS Permissions and SageMaker for Production AI Agents.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/75.%20Day%203%20-%20Setting%20Up%20AWS%20Permissions%20and%20SageMaker%20for%20Production%20AI%20Agents.txt) - Đã dùng
- Slide: [Production W3D3.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D3.pdf) - Đã dùng
- Code: 
  - [1_permissions.md](file:///G:/AIProduction_t6_2026/production/week3/alex/guides/1_permissions.md) - Đã dùng
  - [.env.example](file:///G:/AIProduction_t6_2026/production/week3/alex/.env.example) - Đã dùng
- Summary lịch sử: Đã dùng nội dung tổng hợp từ bài 74.

## 2. Executive Summary - Tóm tắt cốt lõi
- Bài học tập trung vào việc thiết lập quyền truy cập AWS IAM để phục vụ cho toàn bộ dự án Alex, đảm bảo tuân thủ nguyên tắc phân quyền tối thiểu (least privilege).
- Do dịch vụ **S3 Vectors** là một dịch vụ lưu trữ vector mới của AWS tại thời điểm xây dựng khóa học, AWS chưa cung cấp các chính sách quản lý sẵn (managed policies). Lập trình viên phải tạo một chính sách tùy chỉnh (custom policy) có tên `AlexS3VectorsAccess` để cấp quyền `s3vectors:*`.
- Tạo một nhóm người dùng (user group) trên IAM tên là `AlexAccess` và đính kèm 4 chính sách bảo mật quan trọng: `AmazonSageMakerFullAccess`, `AmazonBedrockFullAccess`, `CloudWatchEventsFullAccess`, và chính sách tự định nghĩa `AlexS3VectorsAccess`.
- Gán nhóm `AlexAccess` cho tài khoản IAM của kỹ sư phát triển `aiengineer`. Việc này giúp kỹ sư có đầy đủ quyền thao tác với các dịch vụ AI trong khi tài khoản root có thể đăng xuất để đảm bảo an toàn.
- Thiết lập tệp tin môi trường cục bộ `.env` bằng cách sao chép từ `.env.example` và điền hai tham số cơ bản ban đầu là `AWS_ACCOUNT_ID` và `DEFAULT_AWS_REGION`.
- Làm rõ sự khác biệt giữa hai loại tệp tin lưu trữ biến trong dự án: `.env` dùng cho mã nguồn Python cục bộ và ứng dụng backend, trong khi các file `.tfvars` dùng để cấu hình tham số cho Terraform.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu tầm quan trọng của việc sử dụng tài khoản IAM có quyền hạn giới hạn (`aiengineer`) thay vì dùng tài khoản root cho các hoạt động phát triển hàng ngày.
  - Hiểu cơ chế hoạt động của chính sách IAM tùy chỉnh (custom policy) đối với dịch vụ mới như S3 Vectors.
- **Practical goals - mục tiêu thực hành**:
  - Tạo thành công chính sách `AlexS3VectorsAccess` bằng JSON trên AWS Console.
  - Tạo nhóm `AlexAccess`, gán các chính sách cần thiết và gán nhóm này cho người dùng `aiengineer`.
  - Khởi tạo tệp tin `.env` trong dự án Alex, điền thông tin AWS Account ID và Default Region.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao cần tạo một chính sách tùy chỉnh riêng cho dịch vụ S3 Vectors.
  - Sự khác biệt về mục đích sử dụng giữa tệp `.env` và tệp `terraform.tfvars`.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này triển khai chi tiết bước thiết lập quyền (Day 3 - Foundations) đã được phác thảo sơ bộ trong hướng dẫn tổng quan ở bài 74.

## 5. Core Theory - Lý thuyết cốt lõi
- **Least Privilege Principle (nguyên tắc đặc quyền tối thiểu)**: Nguyên tắc bảo mật trong đó một người dùng hoặc tiến trình chỉ được cấp đúng những quyền hạn tối thiểu cần thiết để hoàn thành công việc, giảm thiểu thiệt hại nếu tài khoản bị xâm nhập.
- **IAM Policy (chính sách IAM)**: Tài liệu JSON xác định quyền hạn của các thực thể trong AWS, quy định rõ Ai (Principal) được thực hiện Hành động gì (Action) trên Tài nguyên nào (Resource) dưới điều kiện nào.
- **S3 Vectors (lưu trữ vector S3)**: Dịch vụ lưu trữ dữ liệu dạng vector trực tiếp trên S3 để phục vụ cho các bài toán tìm kiếm ngữ nghĩa (semantic search) và RAG với chi phí cực kỳ tối ưu.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Quy trình thiết lập quyền AWS IAM cho dự án Alex:
1. **Đăng nhập root user**: Truy cập AWS Console bằng tài khoản root.
2. **Tạo Custom Policy**: Vào IAM -> Policies -> Create Policy -> Chọn JSON và dán cấu hình cấp quyền `s3vectors:*` -> Lưu tên là `AlexS3VectorsAccess`.
3. **Tạo User Group**: Vào IAM -> User Groups -> Create Group -> Đặt tên là `AlexAccess` -> Đính kèm 4 chính sách (SageMaker, Bedrock, CloudWatch Events, và AlexS3VectorsAccess).
4. **Gán nhóm cho người dùng**: Chọn người dùng `aiengineer` và thêm vào nhóm `AlexAccess`.
5. **Đăng xuất root user**: Thoát tài khoản root để đảm bảo an toàn bảo mật.
6. **Đăng nhập IAM user**: Đăng nhập lại AWS Console bằng tài khoản `aiengineer`.
7. **Kiểm tra quyền lực bằng CLI**: Chạy lệnh `aws sts get-caller-identity` và `aws sagemaker list-endpoints` trên Cursor để xác nhận quyền đã hoạt động bình thường.

## 7. Techniques - Kỹ thuật sử dụng
- **Custom IAM Policy Design (Thiết kế chính sách IAM tùy chỉnh)**:
  - Purpose (mục đích): Cấp quyền cho các dịch vụ mới chưa có chính sách mặc định của AWS.
  - When to use (dùng khi nào): Khi tích hợp dịch vụ S3 Vectors hoặc các tài nguyên chuyên biệt trong tổ chức.
  - Trade-off (đánh đổi): Đòi hỏi viết mã JSON thủ công và tự chịu trách nhiệm về phạm vi cấp quyền (sử dụng tài nguyên `*`).
  - Common mistake (lỗi dễ gặp): Gõ sai tên hành động hoặc cấu trúc JSON dẫn đến lỗi cú pháp khi lưu chính sách.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích cấu trúc file môi trường khởi tạo [.env](file:///G:/AIProduction_t6_2026/production/week3/alex/.env.example)

```bash
# G:\AIProduction_t6_2026\production\week3\alex\.env

# Kỹ sư điền thông tin ID tài khoản AWS của mình tại đây
AWS_ACCOUNT_ID=123456789012  # Cần thay thế bằng mã số tài khoản AWS thực tế

# Vùng triển khai hạ tầng mặc định của dự án
DEFAULT_AWS_REGION=us-east-1 # Vùng khuyên dùng có hỗ trợ đầy đủ các dịch vụ AI như Bedrock Nova
```

*Ghi chú giải thích:*
- Lập trình viên phải copy tệp `.env.example` thành `.env` để sử dụng cục bộ.
- File `.env` chứa thông tin nhạy cảm của cá nhân nên đã được định nghĩa trong `.gitignore` để không bị đẩy lên GitHub công khai.

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Đính kèm trực tiếp quyền AdministratorAccess cho tài khoản aiengineer**
  - Pros: Nhanh gọn, lập trình viên không bao giờ gặp lỗi thiếu quyền truy cập (Permission Denied) trong suốt dự án.
  - Cons: Vi phạm nghiêm trọng nguyên tắc bảo mật. Nếu lộ access key của tài khoản này, kẻ tấn công có quyền xóa sạch tài nguyên trong tài khoản AWS.
  - When to choose: Không khuyến khích, ngoại trừ trong các tài khoản sandbox biệt lập không chứa dữ liệu thực.
- **Option 2: Tạo nhóm quyền hạn chế AlexAccess (Lựa chọn của khóa học)**
  - Pros: Đảm bảo an toàn bảo mật thông tin, chỉ mở các cổng dịch vụ cần thiết (SageMaker, Bedrock, S3 Vectors, CloudWatch).
  - Cons: Đôi khi phải cập nhật thêm quyền thủ công khi tích hợp các dịch vụ phát sinh ở các bước sau.
  - When to choose: (Recommended) Môi trường phát triển dự án thực tế trong doanh nghiệp.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Thiếu quyền khi chạy ứng dụng (Access Denied).
  - Root cause: Lập trình viên quên đính kèm nhóm `AlexAccess` cho tài khoản người dùng `aiengineer`, hoặc quên đăng xuất tài khoản root dẫn đến chạy CLI dưới quyền root nhưng chưa cấu hình key.
  - Symptom: Lệnh CLI hoặc mã nguồn Python ném ra ngoại lệ `ClientError: An error occurred (AccessDenied) when calling the ListEndpoints operation`.
  - Fix / prevention: Đăng nhập tài khoản root để kiểm tra lại thành viên của nhóm `AlexAccess`, đảm bảo người dùng `aiengineer` đã nằm trong nhóm. Chạy lệnh `aws sts get-caller-identity` để xác nhận ARN đang chạy trùng khớp với người dùng đã phân quyền.

## 11. Knowledge Extension - Kiến thức mở rộng
- **IAM Policy Simulator (Trình giả lập chính sách IAM)**: AWS cung cấp một công cụ miễn phí trực tuyến gọi là IAM Policy Simulator. Công cụ này cho phép lập trình viên thử nghiệm các chính sách JSON vừa viết đối với các hành động dịch vụ khác nhau mà không cần thực sự thực hiện lệnh trên tài nguyên thật, giúp kiểm tra tính chính xác của các phân quyền phức tạp.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Dịch vụ S3 Vectors yêu cầu tạo một chính sách IAM tùy chỉnh (`AlexS3VectorsAccess`) do chưa có chính sách mặc định sẵn của AWS.
2. Nhóm quyền `AlexAccess` tập hợp các quyền truy cập SageMaker, Bedrock, CloudWatch Events và S3 Vectors.
3. Không bao giờ sử dụng tài khoản AWS root để thực hiện các thao tác lập trình hạ tầng hàng ngày.
4. Lệnh `aws sts get-caller-identity` được dùng để kiểm tra tài khoản đang được cấu hình trên AWS CLI cục bộ.
5. Tệp `.env` quản lý cấu hình các biến môi trường cho ứng dụng Python, còn `terraform.tfvars` dành cho Terraform.

### Self-check questions
1. Tại sao AWS chưa có sẵn chính sách quản lý cho dịch vụ S3 Vectors?
2. Hãy liệt kê 4 chính sách cần đính kèm vào nhóm `AlexAccess` để dự án Alex hoạt động.
3. Lệnh CLI nào giúp bạn xác minh người dùng IAM đang chạy trên máy tính của mình?
4. Điều gì xảy ra nếu bạn không đăng xuất tài khoản root sau khi cấu hình xong IAM?
5. Điểm khác nhau lớn nhất giữa tệp `.env` và `terraform.tfvars` là gì?

### Flashcards
- Q: Lệnh kiểm tra danh sách endpoint của SageMaker để xác nhận quyền hoạt động là gì?
  A: `aws sagemaker list-endpoints`
- Q: Tại sao chính sách tùy chỉnh cho S3 Vectors lại sử dụng tài nguyên `"Resource": "*"`?
  A: Do ở bước thiết lập ban đầu, chúng ta chưa khởi tạo bucket lưu trữ cụ thể cho các vector nên cần cấp quyền trên toàn vùng trước khi chỉ định chi tiết.

### Interview Q&A nếu phù hợp
- Q: Tại sao lại cần gộp các chính sách IAM vào một Group (`AlexAccess`) thay vì gán trực tiếp chính sách đó cho người dùng `aiengineer`?
  A: Gán chính sách qua Group (nhóm) là một thực hành chuẩn trong quản trị hệ thống (role-based access control). Nó giúp dễ dàng quản lý quyền khi dự án có thêm thành viên mới tham gia; ta chỉ cần thêm người dùng đó vào nhóm `AlexAccess` thay vì phải cấu hình lặp lại các chính sách cho từng người, giảm thiểu sai sót bảo mật.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 76. Day 3 - SageMaker vs Bedrock - Deploying Custom AI Models in Production

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [76. Day 3 - SageMaker vs Bedrock - Deploying Custom AI Models in Production.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/76.%20Day%203%20-%20SageMaker%20vs%20Bedrock%20-%20Deploying%20Custom%20AI%20Models%20in%20Production.txt) - Đã dùng
- Slide: [Production W3D3.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D3.pdf) - Đã dùng
- Code: Không có code trực tiếp cho lesson lý thuyết này.
- Summary lịch sử: Đã dùng nội dung tổng hợp từ các bài 74, 75.

## 2. Executive Summary - Tóm tắt cốt lõi
- Giới thiệu **Amazon SageMaker** (sau này được tái cấu trúc thương hiệu thành **SageMaker AI**) là nền tảng quản lý toàn bộ vòng đời của các dự án máy học (Machine Learning - ML) từ xây dựng, huấn luyện, tinh chỉnh đến triển khai mô hình lên môi trường sản xuất.
- Đặt lên bàn cân so sánh giữa hai dịch vụ AI cốt lõi của AWS: **AWS Bedrock** và **Amazon SageMaker**. Bedrock tập trung vào tính đơn giản khi truy cập các mô hình nền tảng lớn (Frontier/Foundation Models) thông qua API dùng chung, trong khi SageMaker cung cấp khả năng can thiệp sâu, tự huấn luyện và triển khai các mô hình tùy chỉnh hoặc nguồn mở từ Hugging Face.
- Giải thích khái niệm **MLOps** (Machine Learning Operations): Tập hợp các thực hành nhằm tự động hóa và chuẩn hóa quy trình triển khai, giám sát và quản lý các mô hình ML trong sản xuất (tương tự như DevOps cho phần mềm truyền thống).
- Làm rõ hiện tượng **Model drift (trôi lệch mô hình)**: Hiệu năng của mô hình suy giảm theo thời gian do dữ liệu thực tế ngoài đời thực thay đổi so với dữ liệu huấn luyện ban đầu (ví dụ: các biến động lớn của thị trường tài chính hoặc sự xuất hiện của các từ vựng mới như dịch bệnh Covid).
- Giới thiệu giải pháp lưu trữ vector **S3 Vectors** trong tuần này của dự án Alex, giúp giảm chi phí lưu trữ vector tới 90% so với việc duy trì một cụm OpenSearch đắt đỏ (tiết kiệm từ $300/tháng xuống còn ~$30/tháng).
- Kế hoạch triển khai tuần này tập trung vào phần dữ liệu (data side) của Alex: Xây dựng các đường ống dữ liệu (data pipelines) để thu thập thông tin tài chính liên tục, chuyển hóa thành vector bằng SageMaker endpoint và lưu trữ vào S3 Vectors.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Phân biệt được sự khác nhau về kiến trúc, chi phí và kịch bản sử dụng giữa Amazon SageMaker và AWS Bedrock.
  - Hiểu khái niệm MLOps và các tính năng hỗ trợ MLOps của SageMaker (Model Registry, Model Monitor).
  - Hiểu nguyên nhân gây ra hiện tượng model drift và cách phòng tránh.
- **Practical goals - mục tiêu thực hành**:
  - Có khả năng đưa ra quyết định kiến trúc lựa chọn Bedrock hay SageMaker cho một bài toán AI cụ thể trong thực tế.
- **What learner should be able to explain - người học cần giải thích được**:
  - Sự khác nhau cơ bản giữa Bedrock và SageMaker.
  - Định nghĩa hiện tượng model drift và đưa ra một ví dụ thực tế.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này cung cấp nền tảng lý thuyết sâu sắc để người học hiểu lý do tại sao ở bài học tiếp theo (bài 77), chúng ta lại chọn triển khai mô hình nhúng (embeddings) trên SageMaker thay vì gọi các mô hình nhúng có sẵn trên Bedrock.

## 5. Core Theory - Lý thuyết cốt lõi
- **Amazon SageMaker AI**: Dịch vụ máy học đám mây toàn diện của AWS, hỗ trợ từ việc gán nhãn dữ liệu (Ground Truth), chạy thử nghiệm (Jupyter Notebooks), huấn luyện phân tán đến triển khai hạ tầng serverless/always-on cho suy luận (inference).
- **MLOps (Machine Learning Operations)**: Quy trình quản lý vòng đời mô hình máy học, bao gồm việc phiên bản hóa dữ liệu/mô hình (data/model versioning), tự động hóa việc huấn luyện lại (automated retraining) và giám sát hiệu năng thực tế.
- **Model Drift (trôi lệch mô hình)**: Sự thay đổi thuộc tính thống kê của dữ liệu thực tế theo thời gian, khiến cho các dự đoán của mô hình được huấn luyện trên dữ liệu cũ không còn chính xác.
- **Semantic Vector Embedding (Nhúng vector ngữ nghĩa)**: Quá trình biểu diễn ý nghĩa của một đoạn văn bản dưới dạng một mảng số thực có kích thước cố định (ví dụ: 384 chiều) để máy tính có thể tính toán khoảng cách ngữ nghĩa giữa các văn bản.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
`Không có pipeline rõ ràng trong tài liệu nguồn`
Bài học chủ yếu tập trung so sánh mặt lý thuyết giữa Bedrock và SageMaker. Dưới đây là bảng so sánh luồng hoạt động của hai dịch vụ:

### Luồng Bedrock (Managed API Flow):
```
Mã nguồn ứng dụng -> Gọi Bedrock API dùng chung -> Trả về kết quả (Trả tiền theo số lượng token tiêu thụ)
```

### Luồng SageMaker (Custom Endpoint Flow):
```
Chuẩn bị mô hình (Hugging Face/Custom) -> Cấu hình Endpoint -> Triển khai hạ tầng -> Gọi Endpoint riêng của bạn -> Trả về kết quả (Trả tiền theo thời gian chạy hoặc cấu hình tài nguyên của Endpoint)
```

## 7. Techniques - Kỹ thuật sử dụng
- **Model Drift Detection (Phát hiện trôi lệch mô hình)**:
  - Purpose (mục đích): Phát hiện kịp thời khi hiệu năng của mô hình AI bị suy giảm trong sản xuất.
  - When to use (dùng khi nào): Áp dụng cho các hệ thống AI chạy liên tục trong môi trường biến động cao (tài chính, dự báo thời tiết, hành vi người tiêu dùng).
  - Trade-off (đánh đổi): Tốn chi phí lưu trữ dữ liệu đầu vào thực tế (data capture) và tài nguyên tính toán để phân tích thống kê.
  - Common mistake (lỗi dễ gặp): Thiết lập ngưỡng cảnh báo quá nhạy dẫn đến cảnh báo giả liên tục (alert fatigue).

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`
(Bài học lý thuyết thuần túy so sánh công nghệ).

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Sử dụng AWS Bedrock để gọi mô hình nhúng (Embeddings)**
  - Pros: Rất đơn giản, không cần quản lý hạ tầng hay cấu hình Terraform, chỉ trả tiền trên số token thực tế.
  - Cons: Không thể tùy chỉnh kiến trúc mô hình nhúng, bị giới hạn bởi các dòng mô hình lớn có sẵn của AWS/đối tác, độ trễ và giới hạn băng thông (rate limits) phụ thuộc vào nhà cung cấp.
  - When to choose: Các ứng dụng chung cần triển khai cực nhanh, không có yêu cầu đặc thù về mô hình nhúng.
- **Option 2: Sử dụng SageMaker Serverless Endpoint để tự host mô hình nhúng (Lựa chọn của khóa học)**
  - Pros: Tự do chọn bất kỳ mô hình mã nguồn mở nào trên Hugging Face, kiểm soát hoàn toàn phiên bản và chi phí hạ tầng (có thể co giãn về 0), độ trễ ổn định.
  - Cons: Cấu hình phức tạp hơn (phải viết Terraform), tốn thời gian khởi động lạnh (cold start) ở yêu cầu đầu tiên.
  - When to choose: (Recommended) Các dự án sản xuất yêu cầu tối ưu chi phí lưu trữ vector lâu dài và cần sử dụng các dòng mô hình nhúng đặc thù siêu nhẹ (như all-MiniLM-L6-v2).

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Hiệu năng mô hình giảm dần mà không có cảnh báo (Silent Model Degradation).
  - Root cause: Lập trình viên triển khai mô hình lên SageMaker nhưng không thiết lập công cụ giám sát trôi lệch dữ liệu (SageMaker Model Monitor), khiến dữ liệu môi trường thay chỉnh mà mô hình vẫn chạy bình thường với kết quả sai lệch ngữ nghĩa.
  - Symptom: Người dùng nhận được các câu trả lời RAG không liên quan hoặc danh mục tài chính phân tích sai lệch, mặc dù hệ thống không báo bất kỳ lỗi logic nào.
  - Fix / prevention: Tích hợp SageMaker Model Monitor và cấu hình lưu trữ dữ liệu thực tế (Data Capture) để so sánh định kỳ với bộ dữ liệu huấn luyện chuẩn.

## 11. Knowledge Extension - Kiến thức mở rộng
- **SageMaker Studio và các IDE máy học**: SageMaker Studio là một môi trường phát triển tích hợp (IDE) dựa trên nền tảng Jupyter Lab. Nó được tích hợp sâu các công cụ theo dõi thí nghiệm (SageMaker Experiments), giúp các nhà khoa học dữ liệu trực quan hóa biểu đồ suy giảm hàm mất mát (loss function), so sánh độ chính xác giữa các lần huấn luyện (epochs) khác nhau và đăng ký mô hình trực tiếp vào kho lưu trữ (Model Registry) chỉ bằng vài cú click chuột.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Amazon SageMaker là nền tảng máy học end-to-end dùng để xây dựng, huấn luyện và triển khai các mô hình riêng hoặc nguồn mở.
2. AWS Bedrock là dịch vụ truy cập mô hình nền tảng (Foundation Models) lớn thông qua API dùng chung có sẵn.
3. MLOps là viết tắt của Machine Learning Operations, tương đương với DevOps áp dụng cho mô hình máy học.
4. Model drift là hiện tượng mô hình bị giảm độ chính xác do dữ liệu thực tế lệch pha với dữ liệu huấn luyện.
5. Giải pháp S3 Vectors giúp tối ưu chi phí lưu trữ vector lên tới 90% so với OpenSearch.

### Self-check questions
1. Điểm khác biệt lớn nhất về mặt quản lý hạ tầng giữa Bedrock và SageMaker là gì?
2. Tại sao hiện tượng model drift lại xảy ra sau các biến động xã hội lớn (ví dụ dịch bệnh Covid)?
3. MLOps giải quyết bài toán gì trong quy trình phát triển phần mềm AI?
4. Khi nào bạn nên chọn SageMaker thay vì Bedrock cho dự án của mình?
5. S3 Vectors giúp tiết kiệm chi phí như thế nào?

### Flashcards
- Q: Nền tảng nào cho phép bạn sử dụng trực tiếp bất kỳ mô hình nào từ Hugging Face Hub?
  A: Amazon SageMaker (thông qua container tích hợp Hugging Face).
- Q: Hiện tượng hiệu năng mô hình giảm do sự thay đổi của ngữ cảnh xã hội theo thời gian gọi là gì?
  A: Model drift (trôi lệch mô hình).

### Interview Q&A nếu phù hợp
- Q: Hãy so sánh cấu trúc chi phí (cost structure) giữa việc triển khai mô hình nhúng trên SageMaker Serverless Endpoint và Bedrock Cohere Embeddings?
  A: Trên Bedrock, bạn trả phí dựa trên số lượng token (tính trên 1 triệu tokens) gửi đi và nhận về, cực kỳ phù hợp khi lượng truy cập thấp hoặc không đều. Trên SageMaker Serverless, bạn trả phí dựa trên thời gian compute thực tế (tính bằng mili giây chạy mô hình nhúng), không tính phí khi idle (không hoạt động). Nếu lượng truy cập lớn và xử lý tài liệu đồng loạt, tự host mô hình nhúng nhẹ trên SageMaker Serverless sẽ rẻ hơn rất nhiều so với Bedrock.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 77. Day 3 - Deploying SageMaker Embedding Models for Production RAG Systems

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [77. Day 3 - Deploying SageMaker Embedding Models for Production RAG Systems.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/77.%20Day%203%20-%20Deploying%20SageMaker%20Embedding%20Models%20for%20Production%20RAG%20Systems.txt) - Đã dùng
- Slide: [Production W3D3.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D3.pdf) - Đã dùng
- Code: 
  - [main.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/2_sagemaker/main.tf) - Đã dùng và phân tích
  - [variables.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/2_sagemaker/variables.tf) - Đã dùng và phân tích
  - [outputs.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/2_sagemaker/outputs.tf) - Đã dùng và phân tích
  - [vectorize_me.json](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/vectorize_me.json) - Đã dùng và phân tích
- Summary lịch sử: Đã dùng nội dung tổng hợp từ các bài trước (74, 75, 76).

## 2. Executive Summary - Tóm tắt cốt lõi
- Bài học hướng dẫn triển khai thực tế một **SageMaker Serverless Endpoint** để chạy mô hình nhúng mã nguồn mở `all-MiniLM-L6-v2` từ Hugging Face Hub bằng Terraform.
- Điểm đặc biệt của giải pháp: Lập trình viên không cần đóng gói hay tải trước file mô hình (model artifacts). Container tích hợp sẵn của SageMaker Hugging Face sẽ tự động tải mô hình trực tiếp từ Hub dựa trên biến môi trường.
- Triển khai cấu hình suy luận không máy chủ (Serverless inference configuration) với lượng bộ nhớ cấp phát là 3GB (mức tối đa mặc định cho serverless) và giới hạn concurrency là 2 để tránh vượt quá hạn mức (quota limit) của tài khoản AWS cá nhân.
- Tích hợp một tài nguyên chờ `time_sleep` với thời lượng 15 giây vào mã nguồn Terraform để đảm bảo vai trò IAM (SageMaker execution role) đã được đồng bộ hóa hoàn toàn trên hệ thống AWS trước khi khởi tạo endpoint.
- Sau khi Terraform triển khai thành công, tên endpoint mặc định sẽ là `alex-embedding-endpoint` và giá trị này được cập nhật vào biến `SAGEMAKER_ENDPOINT` trong tệp `.env`.
- Thực hiện kiểm tra chất lượng endpoint bằng lệnh AWS CLI thông qua dịch vụ `sagemaker-runtime invoke-endpoint`, gửi payload text và nhận về mảng số thực vector nhúng 384 chiều biểu diễn ngữ nghĩa.
- Phân tích chi phí: Cấu hình Serverless giúp hệ thống tự động co giãn về 0 khi không sử dụng, chi phí ước tính cực rẻ chỉ khoảng $1-2/tháng cho nhu cầu phát triển thông thường (~1000 requests/ngày).

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu cách cấu hình một Serverless Endpoint trên SageMaker bằng Terraform.
  - Hiểu tầm quan trọng của việc cấp phát bộ nhớ (memory size) và giới hạn concurrency đối với tài khoản AWS.
  - Hiểu kỹ thuật giải quyết lỗi IAM propagation delay bằng tài nguyên sleep trong Terraform.
- **Practical goals - mục tiêu thực hành**:
  - Viết và hoàn thiện tệp cấu hình `terraform.tfvars` trong thư mục `terraform/2_sagemaker`.
  - Triển khai thành công hạ tầng SageMaker bằng lệnh `terraform init` và `terraform apply`.
  - Sử dụng lệnh `aws sagemaker-runtime invoke-endpoint` để gọi mô hình nhúng và kiểm tra định dạng dữ liệu đầu ra.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao mô hình nhúng lại tự động được tải về mà không cần upload thủ công file `.bin` hay `.safetensors`.
  - Tác dụng của tài nguyên `time_sleep` trong tệp cấu hình Terraform.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này thực hiện triển khai hạ tầng SageMaker đã được giới thiệu lý thuyết ở bài 75 và 76, đóng vai trò là "nhà máy sản xuất vector" cho hệ thống lưu trữ RAG sẽ triển khai ở Day 4 (S3 Vectors và Lambda Ingestion).

## 5. Core Theory - Lý thuyết cốt lõi
- **Serverless Endpoint (Điểm cuối không máy chủ)**: Loại endpoint của SageMaker tự động quản lý tài nguyên tính toán bên dưới, tự động tắt khi không có traffic (scale-to-zero) để tối ưu chi phí vận hành cho các ứng dụng có lưu lượng không liên tục.
- **IAM Propagation Delay (Độ trễ lan truyền IAM)**: Hiện tượng mất từ 5 đến 15 giây để một chính sách bảo mật hoặc vai trò (role) IAM mới tạo có hiệu lực trên toàn bộ các phân vùng vật lý của AWS, dễ gây lỗi nếu tài nguyên khác cố gắng sử dụng role này ngay lập tức.
- **Cold Start (Khởi động lạnh)**: Độ trễ (thường từ 10 đến 60 giây) ở yêu cầu đầu tiên gửi đến một serverless endpoint sau một thời gian không hoạt động, do AWS phải khởi tạo container và tải mô hình vào bộ nhớ.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng hoạt động của đường ống triển khai và kiểm tra SageMaker Embedding Model:
1. **Thiết lập biến**: Tạo tệp `terraform.tfvars` từ `terraform.tfvars.example` và điền vùng AWS hoạt động (ví dụ: `us-east-1`).
2. **Khởi tạo Terraform**: Chạy lệnh `terraform init` để tải provider AWS.
3. **Triển khai hạ tầng**: Chạy lệnh `terraform apply` để tạo IAM Role -> Cấu hình SageMaker Model -> Chờ 15 giây -> Tạo Endpoint Configuration -> Tạo Endpoint thực tế.
4. **Cập nhật biến môi trường**: Lấy tên endpoint `alex-embedding-endpoint` điền vào tệp `.env` của thư mục backend.
5. **Gửi dữ liệu kiểm tra**: Chạy lệnh AWS CLI truyền file payload `vectorize_me.json` chứa chuỗi ký tự cần nhúng ngữ nghĩa.
6. **Xử lý tại Endpoint**: SageMaker container tiếp nhận JSON -> Tải mô hình `all-MiniLM-L6-v2` từ Hugging Face Hub (ở lần chạy đầu tiên) -> Thực hiện suy luận (inference) trích xuất đặc trưng -> Trả về mảng số thực 384 chiều.
7. **Lưu kết quả**: Ghi kết quả vector ra file `output.json` cục bộ để lập trình viên kiểm tra.

## 7. Techniques - Kỹ thuật sử dụng
- **IAM Propagation Sleep (Chờ lan truyền IAM)**:
  - Purpose (mục đích): Tránh lỗi "role invalid" do độ trễ đồng bộ hóa quyền của AWS.
  - When to use (dùng khi nào): Khi tạo mới một IAM role và ngay lập tức sử dụng role đó cho một dịch vụ phức tạp như SageMaker hay Lambda trong cùng một tập lệnh Terraform.
  - Trade-off (đánh đổi): Làm tăng thời gian chạy của lệnh `terraform apply` thêm 15 giây.
  - Common mistake (lỗi dễ gặp): Thiết lập thời gian sleep quá ngắn (dưới 5 giây) khiến lỗi vẫn thỉnh thoảng xảy ra một cách ngẫu nhiên.
- **Hugging Face Model Direct Integration (Tích hợp trực tiếp mô hình Hugging Face)**:
  - Purpose (mục đích): Loại bỏ bước đóng gói model thủ công giúp tinh gọn tệp cấu hình hạ tầng.
  - When to use (dùng khi nào): Triển khai các mô hình nguồn mở tiêu chuẩn có sẵn trên Hugging Face Hub sang SageMaker để suy luận nhanh.
  - Trade-off (đánh đổi): Bị phụ thuộc vào tính sẵn sàng của Hugging Face Hub ở lần khởi động lạnh đầu tiên của container.
  - Common mistake (lỗi dễ gặp): Gõ sai tên biến môi trường `HF_MODEL_ID` hoặc tên tác vụ `HF_TASK` khiến container khởi động thất bại mà không báo rõ lỗi.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích chi tiết file cấu hình hạ tầng [main.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/2_sagemaker/main.tf)

```hcl
# G:\AIProduction_t6_2026\production\week3\alex\terraform\2_sagemaker\main.tf

terraform {
  required_version = ">= 1.5"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Lấy thông tin tài khoản AWS hiện tại đang thực thi lệnh
data "aws_caller_identity" "current" {}

# Khởi tạo IAM Role cho dịch vụ SageMaker
resource "aws_iam_role" "sagemaker_role" {
  name = "alex-sagemaker-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com" # Chỉ cho phép SageMaker giả lập role này
        }
      }
    ]
  })
}

# Đính kèm quyền quản trị SageMaker đầy đủ cho role vừa tạo
resource "aws_iam_role_policy_attachment" "sagemaker_full_access" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# Khai báo Model định cấu hình mô hình nhúng
resource "aws_sagemaker_model" "embedding_model" {
  name               = "alex-embedding-model"
  execution_role_arn = aws_iam_role.sagemaker_role.arn

  primary_container {
    image = var.sagemaker_image_uri # URI của container PyTorch chuyên suy luận
    environment = {
      HF_MODEL_ID = var.embedding_model_name # Tên mô hình trên HuggingFace Hub
      HF_TASK     = "feature-extraction"     # Nhiệm vụ trích xuất đặc trưng (embedding)
    }
  }

  depends_on = [aws_iam_role_policy_attachment.sagemaker_full_access]
}

# Cấu hình Endpoint ở chế độ Serverless (Không máy chủ)
resource "aws_sagemaker_endpoint_configuration" "serverless_config" {
  name = "alex-embedding-serverless-config"

  production_variants {
    model_name = aws_sagemaker_model.embedding_model.name
    
    serverless_config {
      memory_size_in_mb = 3072 # Bộ nhớ đệm cấp phát 3GB
      max_concurrency   = 2    # Giới hạn 2 yêu cầu đồng thời để tránh lỗi quota tài khoản cá nhân
    }
  }
}

# Kỹ thuật sleep 15 giây chờ IAM role đồng bộ trên AWS toàn cầu
resource "time_sleep" "wait_for_iam_propagation" {
  depends_on = [
    aws_iam_role_policy_attachment.sagemaker_full_access
  ]
  
  create_duration = "15s"
}

# Khởi tạo Endpoint thực tế chạy mô hình nhúng
resource "aws_sagemaker_endpoint" "embedding_endpoint" {
  name                 = "alex-embedding-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.serverless_config.name
  
  depends_on = [
    time_sleep.wait_for_iam_propagation # Chỉ tạo sau khi đã hoàn thành việc sleep chờ IAM
  ]
}
```

### Phân tích file định nghĩa biến [variables.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/2_sagemaker/variables.tf)

```hcl
# G:\AIProduction_t6_2026\production\week3\alex\terraform\2_sagemaker\variables.tf

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
}

# URI container PyTorch được lưu trên ECR của AWS, hỗ trợ HuggingFace và suy luận CPU
variable "sagemaker_image_uri" {
  description = "URI of the SageMaker container image"
  type        = string
  default     = "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
}

# Khai báo mô hình nhúng mặc định của dự án Alex
variable "embedding_model_name" {
  description = "Name of the HuggingFace model to use"
  type        = string
  default     = "sentence-transformers/all-MiniLM-L6-v2"
}
```

### Phân tích file đầu ra [outputs.tf](file:///G:/AIProduction_t6_2026/production/week3/alex/terraform/2_sagemaker/outputs.tf)

```hcl
# G:\AIProduction_t6_2026\production\week3\alex\terraform\2_sagemaker\outputs.tf

output "sagemaker_endpoint_name" {
  description = "Name of the SageMaker endpoint"
  value       = aws_sagemaker_endpoint.embedding_endpoint.name
}

output "sagemaker_endpoint_arn" {
  description = "ARN of the SageMaker endpoint"
  value       = aws_sagemaker_endpoint.embedding_endpoint.arn
}

output "setup_instructions" {
  description = "Instructions for setting up environment variables"
  value = <<-EOT
    
    ✅ SageMaker endpoint deployed successfully!
    Follow the instructions in the guide to update your .env file and test the endpoint.
  EOT
}
```

### Phân tích file payload dữ liệu kiểm tra [vectorize_me.json](file:///G:/AIProduction_t6_2026/production/week3/alex/backend/vectorize_me.json)

```json
{
  "inputs": "vectorize me"
}
```

*Ghi chú giải thích:*
- Cấu trúc JSON chỉ chứa một trường duy nhất `inputs` truyền vào đoạn text cần nhúng. Đây là cấu trúc dữ liệu bắt buộc của container Hugging Face PyTorch Inference cho tác vụ `feature-extraction`.

### Lệnh CLI thực hiện kiểm tra suy luận nhúng (dùng cho Windows):
```powershell
aws sagemaker-runtime invoke-endpoint --endpoint-name "alex-embedding-endpoint" --content-type "application/json" --body "fileb://vectorize_me.json" --output json output.json
```
- `--endpoint-name`: Chỉ định chính xác endpoint vừa được Terraform tạo ra.
- `--content-type`: Khai báo kiểu dữ liệu gửi đi là JSON.
- `--body "fileb://vectorize_me.json"`: Tải file dữ liệu cục bộ dưới dạng nhị phân (binary payload). Ký hiệu `fileb://` là bắt buộc đối với CLI để truyền tệp nhị phân chính xác.
- `output.json`: File kết quả trả về sẽ được lưu tại đây. Chứa mảng số thực 384 chiều của mô hình `all-MiniLM-L6-v2`.

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Thiết lập cấu hình Endpoint Serverless với max_concurrency = 10**
  - Pros: Khả năng đáp ứng tải cao, cho phép xử lý song song 10 luồng yêu cầu nhúng cùng lúc mà không bị nghẽn.
  - Cons: Dễ chạm ngưỡng giới hạn (quota limits) của tài khoản AWS cá nhân mới lập, dẫn đến lỗi khởi tạo endpoint thất bại giữa chừng.
  - When to choose: Các dự án tài khoản doanh nghiệp đã nâng hạn mức dịch vụ.
- **Option 2: Giới hạn cấu hình max_concurrency = 2 (Lựa chọn của khóa học)**
  - Pros: An toàn tuyệt đối cho tài khoản học viên, tránh lỗi vượt quá quota tài nguyên của AWS.
  - Cons: Khi có nhiều hơn 2 tác vụ nhúng chạy song song, các yêu cầu tiếp theo sẽ phải xếp hàng chờ đợi.
  - When to choose: (Recommended) Môi trường học tập và phát triển thử nghiệm ứng dụng.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Lỗi `Role invalid or cannot be assumed` khi tạo Endpoint.
  - Root cause: AWS cố gắng tạo endpoint ngay lập tức khi vai trò IAM mới được tạo xong trong Terraform, nhưng vai trò đó chưa kịp lan truyền (propagate) trên toàn hệ thống AWS toàn cầu.
  - Symptom: Lệnh `terraform apply` ném lỗi thất bại khi đang khởi tạo tài nguyên `aws_sagemaker_endpoint`.
  - Fix / prevention: Đảm bảo sử dụng tài nguyên `time_sleep` với giá trị ít nhất là 15 giây đặt trước khối tài nguyên endpoint để bắt buộc Terraform dừng lại chờ đợi sự đồng bộ hóa IAM.

## 11. Knowledge Extension - Kiến thức mở rộng
- **all-MiniLM-L6-v2 Dimension and Model Size**: Mô hình nhúng `all-MiniLM-L6-v2` chỉ nặng khoảng 90MB, xuất ra vector nhúng có kích thước 384 chiều. Đây là một mô hình cực kỳ tối ưu cho các tác vụ nhúng tốc độ cao trên thiết bị cấu hình yếu hoặc CPU. So với các mô hình nhúng lớn hơn (như Cohere hay OpenAI text-embedding-3-large có số chiều lên tới 1536 hoặc 3072), mô hình này giúp giảm dung lượng cơ sở dữ liệu lưu trữ vector đi 4 đến 8 lần mà vẫn giữ được độ chính xác ngữ nghĩa tương đối tốt cho các văn bản ngắn.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Tên endpoint được tạo mặc định là `alex-embedding-endpoint`.
2. Sử dụng mô hình `sentence-transformers/all-MiniLM-L6-v2` cho dự án Alex.
3. Kích thước chiều vector đầu ra của mô hình nhúng là 384 chiều.
4. Lệnh AWS CLI truyền file nhị phân bắt buộc phải sử dụng tiền tố `fileb://`.
5. Cấu hình bộ nhớ mặc định cho Serverless Endpoint trong Terraform là 3072 MB (3GB).

### Self-check questions
1. Tại sao container SageMaker lại biết cách tải mô hình từ HuggingFace Hub về chạy?
2. Ý nghĩa của tham số `max_concurrency` trong cấu hình serverless của SageMaker là gì?
3. Tại sao yêu cầu nhúng đầu tiên sau một thời gian dài lại mất nhiều thời gian phản hồi hơn?
4. Ký hiệu `fileb://` trong CLI khác gì so với `file://` thông thường?
5. Bộ nhớ RAM tối đa cấp phát cho SageMaker Serverless Endpoint trong bài thực hành là bao nhiêu?

### Flashcards
- Q: Lệnh để lấy thông tin chi tiết trạng thái của endpoint từ CLI là gì?
  A: `aws sagemaker describe-endpoint --endpoint-name alex-embedding-endpoint`
- Q: Biến môi trường nào định nghĩa mã mô hình trên HuggingFace trong cấu hình container?
  A: `HF_MODEL_ID`

### Interview Q&A nếu phù hợp
- Q: Tại sao lại chọn cấu hình Serverless Endpoint có bộ nhớ 3GB cho một mô hình nhúng siêu nhẹ chỉ nặng 90MB như `all-MiniLM-L6-v2`?
  A: Trên SageMaker Serverless, dung lượng RAM tỷ lệ thuận với sức mạnh CPU được cấp phát bên dưới. Cấu hình RAM 3GB giúp mô hình nhúng chạy nhanh hơn, giảm độ trễ xử lý (latency) xuống mức thấp nhất và hạn chế lỗi hết bộ nhớ khi container PyTorch khởi động các tiến trình phụ trợ. Do tính phí theo thời gian compute thực tế, việc RAM lớn giúp chạy nhanh hơn đôi khi lại tiết kiệm chi phí hơn so với RAM nhỏ chạy chậm.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 78. Day 3 - Exploring SageMaker AI's Full Platform for Production ML Workflows

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [78. Day 3 - Exploring SageMaker AI's Full Platform for Production ML Workflows.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/78.%20Day%203%20-%20Exploring%20SageMaker%20AI%27s%20Full%20Platform%20for%20Production%20ML%20Workflows.txt) - Đã dùng
- Slide: [Production W3D3.pdf](file:///G:/AIProduction_t6_2026/production/slide/week3/Production%20W3D3.pdf) - Đã dùng
- Code: Không có code trực tiếp cho lesson lý thuyết này.
- Summary lịch sử: Đã dùng nội dung tổng hợp từ các bài trước (74 đến 77).

## 2. Executive Summary - Tóm tắt cốt lõi
- Khảo sát giao diện điều khiển (AWS Console) của dịch vụ **SageMaker AI** (tên thương hiệu mới được AWS cập nhật cho SageMaker) để hiểu bức tranh toàn cảnh về các công cụ hỗ trợ một kỹ sư dữ liệu / nhà khoa học dữ liệu chuyên nghiệp.
- Giới thiệu **SageMaker Studio**: Môi trường phát triển tích hợp (IDE) chuyên dụng trên nền tảng đám mây để huấn luyện, gỡ lỗi, kiểm tra mô hình và quản lý các lượt chạy thí nghiệm máy học.
- Giới thiệu thành phần **Notebooks**: Giải pháp chạy các máy chủ Jupyter Lab trên đám mây của AWS, tương tự như Google Colab nhưng tích hợp sâu hơn trong hệ sinh thái hạ tầng bảo mật của AWS.
- Giới thiệu các chức năng khác trên menu SageMaker AI: **JumpStart** (thư viện duyệt nhanh các mô hình nền tảng nguồn mở sẵn có), **Ground Truth** (dịch vụ dán nhãn dữ liệu huấn luyện thủ công hoặc tự động) và các công cụ quản lý huấn luyện (Training Jobs).
- Chỉ ra vị trí của tài nguyên đã tạo ở bài 77: Nằm sâu trong menu `Inference` -> `Endpoints` với tên gọi `alex-embedding-endpoint`. Đây là một cấu hình triển khai endpoint suy luận rất phổ biến trong thực tế.
- Khép lại ngày học Day 3 và hé lộ lộ trình tiếp theo của Day 4: Tích hợp endpoint nhúng này vào một đường ống dẫn dữ liệu hoàn chỉnh (data ingestion pipeline) sử dụng AWS Lambda để xử lý và ghi kết quả vào S3 Vectors.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Nắm được các thành phần chính trong hệ sinh thái công cụ của SageMaker AI.
  - Hiểu cách truy cập và quản trị các endpoint suy luận trên giao diện AWS Console.
  - Hiểu vai trò của Notebooks đám mây so với các giải pháp chạy code cục bộ hoặc Google Colab.
- **Practical goals - mục tiêu thực hành**:
  - Đăng nhập AWS Console bằng tài khoản `aiengineer` và điều hướng đến màn hình quản trị SageMaker AI.
  - Tìm kiếm và kiểm tra trạng thái hoạt động trực quan của endpoint `alex-embedding-endpoint`.
- **What learner should be able to explain - người học cần giải thích được**:
  - SageMaker Studio và Notebooks dùng để làm gì.
  - Vị trí quản lý Endpoint nằm trong mục nào của menu SageMaker AI.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này tổng kết các hoạt động thực tế triển khai ở bài 77 bằng cách đối chiếu mã nguồn Terraform với các tài nguyên trực quan được tạo ra trên giao diện AWS Console.

## 5. Core Theory - Lý thuyết cốt lõi
- **SageMaker Studio**: IDE máy học hợp nhất, cung cấp giao diện trực quan cho phép theo dõi toàn bộ quá trình phát triển mô hình từ chuẩn bị dữ liệu, xây dựng thuật toán đến triển khai endpoint.
- **Jupyter Lab in Cloud (Notebooks)**: Các phiên bản Jupyter Notebook chạy trên hạ tầng đám mây của AWS, được liên kết trực tiếp với các tài nguyên lưu trữ như S3 hay cơ sở dữ liệu để phục vụ phân tích dữ liệu lớn.
- **JumpStart**: Kho lưu trữ các giải pháp máy học mẫu và các mô hình nền tảng nguồn mở đã được cấu hình sẵn, cho phép người dùng triển khai nhanh chỉ với một cú click chuột.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
`Không có pipeline rõ ràng trong tài liệu nguồn`
Bài học chủ yếu mô tả luồng điều hướng giao diện của người dùng trên AWS Console:
1. Tìm kiếm dịch vụ "SageMaker" trên thanh công cụ của AWS Console.
2. Truy cập màn hình SageMaker AI.
3. Điều hướng menu bên trái tìm mục `Inference` -> click vào `Endpoints`.
4. Tìm kiếm endpoint tên `alex-embedding-endpoint` trong danh sách để kiểm tra các chỉ số CloudWatch giám sát hoạt động.

## 7. Techniques - Kỹ thuật sử dụng
- **Cloud Metric Monitoring (Giám sát chỉ số đám mây)**:
  - Purpose (mục đích): Theo dõi tần suất gọi và thời gian phản hồi của mô hình nhúng.
  - When to use (dùng khi nào): Áp dụng ngay sau khi triển khai endpoint lên môi trường sản xuất để phát hiện sớm các lỗi quá tải hoặc nghẽn băng thông.
  - Trade-off (đánh đổi): Không có. Đây là tính năng tích hợp mặc định của CloudWatch đi kèm dịch vụ SageMaker.
  - Common mistake (lỗi dễ gặp): Không cấu hình cảnh báo (alarms) khi số lượng lỗi (errors) vượt ngưỡng an toàn.

## 8. Code Walkthrough - Phân tích code nếu có
`Buổi học này không có code được cung cấp`
(Bài học giới thiệu giao diện AWS Console và hệ sinh thái công cụ).

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Sử dụng SageMaker Notebooks để thử nghiệm mã nguồn**
  - Pros: Tích hợp sẵn trong VPC của AWS, dễ dàng truy cập dữ liệu bảo mật trên S3 mà không cần cấu hình key cục bộ, tài nguyên tính toán mạnh mẽ (GPU/RAM lớn).
  - Cons: Chi phí đắt đỏ nếu quên tắt máy chủ notebook sau khi sử dụng (tính tiền theo giờ chạy máy ảo).
  - When to choose: Khi huấn luyện mô hình lớn hoặc xử lý dữ liệu nhạy cảm của doanh nghiệp.
- **Option 2: Thử nghiệm mã nguồn cục bộ trên Cursor/VS Code (Lựa chọn của khóa học)**
  - Pros: Hoàn toàn miễn phí, tận dụng được sức mạnh của các AI coding assistants cục bộ và dễ quản lý mã nguồn bằng Git.
  - Cons: Phải tự cấu hình môi trường Python và quyền truy cập AWS CLI trên máy cá nhân.
  - When to choose: (Recommended) Quá trình phát triển ứng dụng AI thông thường và tích hợp hệ thống.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Phát sinh chi phí lớn từ các Notebooks chạy ẩn (Orphaned Notebook Instances).
  - Root cause: Lập trình viên khởi tạo các Notebook Instance trong SageMaker để thử nghiệm code nhưng quên tắt (Stop) hoặc xóa (Delete) sau khi hoàn thành công việc.
  - Symptom: Tài khoản AWS bị trừ tiền liên tục hàng giờ ngay cả khi không có bất kỳ ai sử dụng hay gọi code.
  - Fix / prevention: Luôn tắt các instance Jupyter Notebook khi không làm việc. Sử dụng các script tự động tắt máy ảo sau một khoảng thời gian idle nhất định.

## 11. Knowledge Extension - Kiến thức mở rộng
- **SageMaker Ground Truth**: Đây là dịch vụ hỗ trợ gán nhãn dữ liệu cực kỳ mạnh mẽ của AWS. Nó cho phép các tổ chức xây dựng các luồng công việc gán nhãn kết hợp: Sử dụng lực lượng lao động công cộng (Amazon Mechanical Turk), đội ngũ nhân sự nội bộ của doanh nghiệp, hoặc các đối tác gán nhãn chuyên nghiệp để dán nhãn hàng triệu hình ảnh, văn bản hoặc dữ liệu đám mây điểm (point clouds) phục vụ huấn luyện các mô hình AI tùy chỉnh.

## 12. Study Pack - Gói ôn tập
### Must remember
1. SageMaker AI là tên thương hiệu mới của Amazon SageMaker.
2. SageMaker Studio là IDE đám mây tích hợp đầy đủ cho các nhà khoa học dữ liệu.
3. Mục Endpoints nằm dưới menu Inference là nơi quản trị các cổng kết nối API của mô hình.
4. Notebooks của SageMaker chạy các máy chủ Jupyter Lab trực tiếp trên đám mây.
5. SageMaker JumpStart cung cấp thư viện mô hình nguồn mở tải nhanh.

### Self-check questions
1. SageMaker Studio hỗ trợ những hoạt động nào trong vòng đời phát triển mô hình ML?
2. Hãy nêu sự khác nhau giữa SageMaker Notebooks và Google Colab.
3. Làm thế nào để kiểm tra xem endpoint của bạn có đang chạy hay không từ giao diện Console?
4. Ground Truth trong SageMaker giải quyết bài toán gì?
5. Lộ trình của ngày học tiếp theo (Day 4) sẽ làm gì với endpoint SageMaker vừa tạo?

### Flashcards
- Q: Dịch vụ nào của SageMaker hỗ trợ gán nhãn dữ liệu tự động hoặc thủ công?
  A: SageMaker Ground Truth.
- Q: Nơi quản lý các lượt chạy thử nghiệm và siêu tham số huấn luyện là gì?
  A: SageMaker Experiments.

### Interview Q&A nếu phù hợp
- Q: Làm thế nào để tối ưu hóa chi phí khi sử dụng SageMaker Notebook Instances trong môi trường doanh nghiệp?
  A: Doanh nghiệp thường áp dụng các biện pháp: Cấu hình Lifecycle Configurations cho Notebook để tự động chạy một script kiểm tra trạng thái hoạt động; nếu không có hoạt động kernel nào trong vòng 1-2 tiếng, script sẽ tự động gọi API dừng (Stop) instance đó. Đồng thời, thiết lập các cảnh báo AWS Budget để thông báo ngay lập tức khi chi phí dịch vụ SageMaker vượt quá hạn mức cho phép hàng ngày.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.
