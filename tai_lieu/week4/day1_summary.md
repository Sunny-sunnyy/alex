# Day 1 - Multi-Agent Architectures & Database Shared Infrastructure

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

---

# 89. Day 1 - Multi-Agent vs Single-Agent Architectures for Production AI Systems

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [89. Day 1 - Multi-Agent vs Single-Agent Architectures for Production AI Systems.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/89.%20Day%201%20-%20Multi-Agent%20vs%20Single-Agent%20Architectures%20for%20Production%20AI%20Systems.txt) - Đã dùng
- Slide: [Production W4D1.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D1.pdf) (Slide 2, 3) - Đã dùng
- Code: Không có code trực tiếp cho lesson lý thuyết này.
- Summary lịch sử: [day5_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week3/day5_summary.md) - Đã dùng làm ngữ cảnh nền của tuần học trước.

## 2. Executive Summary - Tóm tắt cốt lõi
- Bài học mở đầu tuần 4 tập trung vào ba từ khóa chủ đạo của hệ thống AI thực tế: **agents (tác tử)**, **scale (quy mô)**, và **enterprise (doanh nghiệp)**.
- Phân biệt định nghĩa của Anthropic giữa **workflows (quy trình công việc)** - nơi LLM và công cụ được điều phối qua các code paths (đường dẫn mã) cố định, và **agents (tác tử)** - nơi LLM tự quyết định quy trình hành động và công cụ nào sẽ được gọi một cách linh hoạt.
- Giới thiệu hai mẫu thiết kế tác tử phổ biến: **multi-agent architectures (kiến trúc đa tác tử)** (có Planner điều phối các worker agents chuyên biệt) và **single agent with loop (tác tử đơn kèm vòng lặp)** (một tác tử duy nhất tự duy trì to-do list và lặp lại hành động).
- Nhấn mạnh nguyên tắc vàng: Luôn bắt đầu đơn giản với một LLM call duy nhất. Chỉ nên tăng độ phức tạp của kiến trúc (tách agent, thêm loop) khi các phép đo lường hiệu năng thực nghiệm cho thấy hệ thống hiện tại không đạt bar (tiêu chuẩn) success criteria (tiêu chí thành công).

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Phân biệt rõ sự khác nhau giữa workflows và agents theo định nghĩa của Anthropic.
  - Hiểu bản chất và đặc điểm hoạt động của kiến trúc multi-agent so với single agent with loop.
  - Nắm vững triết lý thiết kế hệ thống tác tử thực nghiệm dựa trên metrics (số liệu đo lường) thay vì võ đoán hạ tầng.
- **Practical goals - mục tiêu thực hành**:
  - Đánh giá một bài toán kinh doanh thực tế để xác định điểm bắt đầu phù hợp của kiến trúc tác tử (bắt đầu bằng single call).
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao việc nhảy trực tiếp vào xây dựng kiến trúc đa tác tử phức tạp ngay từ đầu lại là một phản mẫu thiết kế (anti-pattern).
  - Cơ chế tự điều phối công việc của một single agent with loop (ví dụ: Claude Code).

## 4. Previous Context - Liên hệ với bài trước
- Bài học này mở đầu cho Week 4 - Capstone Project Alex. Nó kế thừa trực tiếp luồng thu thập dữ liệu RAG của Researcher Agent đã hoàn tất ở cuối Week 3 để làm giàu tri thức cho hệ thống multi-agent sẽ được triển khai.

## 5. Core Theory - Lý thuyết cốt lõi
- **Workflows (Quy trình công việc)**: Hệ thống điều phối LLM và công cụ thông qua các đường dẫn code cứng được định nghĩa sẵn bởi lập trình viên.
- **Agents (Tác tử)**: Hệ thống mà trong đó LLM có quyền tự quyết định luồng đi, lựa chọn công cụ và thời điểm kết thúc tác vụ để đạt được mục tiêu.
- **Multi-agent architecture (Kiến trúc đa tác tử)**: Mô hình thiết kế sử dụng một tác tử Planner/Orchestrator làm nhiệm vụ tiếp nhận yêu cầu, phân rã công việc và điều phối các worker agents chuyên biệt thực thi.
- **Single agent with loop (Tác tử đơn với vòng lặp)**: Mô hình sử dụng một LLM duy nhất với context (ngữ cảnh) lớn, tự quản lý danh sách công việc cần làm (to-do list) và lặp đi lặp lại quy trình suy nghĩ (thought-action loop) cho đến khi hoàn thành mục tiêu.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
`Không có pipeline rõ ràng trong tài liệu nguồn`
Bài học chủ yếu giới thiệu luồng tư duy thiết kế tác tử:
1. **Commercial Problem**: Xác định rõ bài toán kinh doanh cần giải quyết.
2. **Success Criteria & Metric**: Thiết lập thước đo để đánh giá chất lượng đầu ra.
3. **Start Simple**: Bắt đầu bằng một LLM call đơn lẻ (single agent call), không loop.
4. **Evaluate**: Chạy thử nghiệm và thu thập metric hiệu năng.
5. **Iterate & Refactor**: Chỉ chia tách các tác tử hoặc thêm vòng lặp khi cần cô lập ngữ cảnh để cải thiện hiệu năng của một tác vụ cụ thể.

## 7. Techniques - Kỹ thuật sử dụng
- **Experimental Agent Design (Thiết kế tác tử thực nghiệm)**:
  - Purpose - mục đích: Tránh việc lãng phí tài nguyên và chi phí API vào các cấu trúc tác tử quá phức tạp không cần thiết (over-engineering).
  - When to use - dùng khi nào: Giai đoạn bắt đầu thiết kế bất kỳ ứng dụng AI Agentic nào.
  - Trade-off - đánh đổi: Phải thiết lập hệ thống thu thập metric và chạy kiểm thử lặp đi lặp lại để so sánh hiệu năng.
  - Common mistake - lỗi dễ gặp: Vội vã chia nhỏ hệ thống thành 5-10 tác tử ngay từ đầu khiến việc gỡ lỗi trở nên cực kỳ khó khăn.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Multi-Agent Architecture (Kiến trúc đa tác tử)**
  - Pros: Từng tác tử worker có context ngắn, tập trung chuyên biệt vào một nhiệm vụ; dễ dàng đánh giá và tinh chỉnh prompt độc lập.
  - Cons: Độ trễ lớn, Planner phải thực hiện nhiều cuộc gọi điều phối, chi phí API cao hơn.
  - When to choose: Các bài toán kinh doanh lớn gồm nhiều nghiệp vụ không liên quan trực tiếp (như lập báo cáo và vẽ biểu đồ).
- **Option 2: Single Agent with Loop (Tác tử đơn với vòng lặp)**
  - Pros: Tác tử tự xử lý linh hoạt, tự quản lý công việc và sửa sai tốt, kiến trúc lập trình gọn gàng.
  - Cons: Context phình to theo thời gian lặp, dễ bị trôi ngữ cảnh (context drift) hoặc rơi vào vòng lặp vô hạn.
  - When to choose: Các tác vụ giải quyết vấn đề kỹ thuật mở và phức tạp (như tác tử viết code tự động).

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Vòng lặp tác tử vô hạn (Agent infinite loop).
  - Root cause: Tác tử đơn trong vòng lặp không thể cập nhật trạng thái to-do list hoặc liên tục gặp lỗi khi gọi công cụ nhưng vẫn cố gắng thử lại vô hạn.
  - Symptom: Tiêu hao tài nguyên cực lớn, hóa đơn API tăng vọt đột ngột, Lambda bị timeout.
  - Fix / prevention: Bắt buộc cấu hình tham số giới hạn số lượt tối đa (`max_turns` hoặc `max_iterations`) trong code chạy Runner để cưỡng chế dừng khi vượt ngưỡng.

## 11. Knowledge Extension - Kiến thức mở rộng
- **Seminal Blog Post của Anthropic (12/2024)**: Bài viết "Building Effective Agents" chỉ ra rằng phần lớn các ứng dụng AI thành công trong sản xuất thực tế thực chất sử dụng mô hình Workflows (chạy theo code path định sẵn) hoặc Orchestrator-Workers đơn giản. Sự tự chủ hoàn toàn của tác tử (autonomous agents) thường khó kiểm soát và tốn kém hơn nhiều.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Workflows chạy theo code path cố định; Agents tự quyết định luồng đi và công cụ.
2. Multi-agent sử dụng Planner để điều phối các worker agents độc lập.
3. Single agent with loop tự duy trì to-do list và lặp lại suy nghĩ đến khi hoàn thành.
4. Triết lý thiết kế tác tử: Luôn bắt đầu đơn giản bằng một LLM call duy nhất.
5. Cần có metrics cụ thể để đánh giá hiệu năng trước khi tăng độ phức tạp của kiến trúc.

### Self-check questions
1. Sự khác biệt cơ bản giữa Workflows và Agents theo định nghĩa của Anthropic là gì?
2. Khi nào lập trình viên nên chọn kiến trúc đa tác tử thay vì tác tử đơn kèm vòng lặp?

### Flashcards
- Q: AI Agent là gì?
  A: Hệ thống mà LLM tự quyết định quy trình hành động và cách dùng công cụ để hoàn thành tác vụ.
- Q: Tham số nào dùng để ngăn chặn tác tử rơi vào vòng lặp vô hạn?
  A: `max_turns` (Giới hạn số lượt chạy tối đa).

### Interview Q&A
- Q: Tại sao bạn nên bắt đầu thiết kế hệ thống AI bằng một tác tử đơn (single call) trước khi chuyển sang đa tác tử (multi-agent)?
  A: Bắt đầu đơn giản giúp ta thiết lập được một baseline (mức cơ sở) về hiệu năng và chi phí. Nếu tác tử đơn đã giải quyết được yêu cầu với chi phí thấp và độ trễ tối ưu, ta không cần tốn công sức xây dựng và gỡ lỗi một hệ thống đa tác tử phức tạp. Chỉ khi tác tử đơn bị quá tải ngữ cảnh hoặc không thể thực hiện tốt các tác vụ chuyên biệt, ta mới tách nhỏ tác tử dựa trên bằng chứng dữ liệu thực nghiệm.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 90. Day 1 - Building Multi-Agent Financial AI - Database Architecture & AWS Setup

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [90. Day 1 - Building Multi-Agent Financial AI - Database Architecture & AWS Setup.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/90.%20Day%201%20-%20Building%20Multi-Agent%20Financial%20AI%20-%20Database%20Architecture%20&%20AWS%20Setup.txt) - Đã dùng
- Slide: [Production W4D1.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D1.pdf) (Slide 4, 5, 6, 7, 8, 9) - Đã dùng
- Code: Không có code trực tiếp cho lesson lý thuyết này.

## 2. Executive Summary - Tóm tắt cốt lõi
- Giới thiệu kiến trúc đa tác tử gồm 5 tác tử của dự án Alex: **Planner** (điều phối), **Tagger** (phân loại tài sản), **Reporter** (viết báo cáo danh mục), **Charter** (tạo biểu đồ), và **Retirement** (phân tích hưu trí).
- Cảnh báo hiện tượng **anthropomorphizing (nhân hóa)** tác tử: Coi tác tử như con người là một sai lầm thiết kế. Thực chất, tác tử là các LLM calls (cuộc gọi mô hình) được cung cấp system prompt và context (ngữ cảnh) chuyên biệt để hoàn thành tối ưu một tác vụ cụ thể.
- Kiến trúc triển khai trên AWS: Các tác tử là các AWS Lambda serverless functions độc lập gọi Bedrock LLM, giao tiếp bất đồng bộ qua hàng đợi **SQS (Simple Queue Service)** và lưu trữ dữ liệu vào cơ sở dữ liệu **Aurora Serverless v2**.
- Thiết lập luồng Front-end: NextJS static site lưu trên S3 kết hợp CloudFront CDN, kết nối qua API Gateway tới Backend API Lambda để đẩy các yêu cầu bất đồng bộ vào hàng đợi SQS.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Nắm vững vai trò và nhiệm vụ thương mại của 5 tác tử trong hệ thống tài chính Alex.
  - Hiểu cách thức phân tách nhiệm vụ tác tử để có thể kiểm thử và đánh giá độc lập.
  - Nắm được sơ đồ hạ tầng serverless hoàn chỉnh của ứng dụng SaaS Alex.
- **Practical goals - mục tiêu thực hành**:
  - Hình dung rõ ràng luồng đi của dữ liệu từ khi người dùng click trên frontend cho đến khi dữ liệu được ghi vào database.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao việc nhân hóa tác tử lại gây ra các sai lầm trong thiết kế ngữ cảnh hệ thống AI.
  - Vai trò của SQS trong việc tách rời (decouple) backend API và Planner Lambda.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này mở rộng đường ống dữ liệu RAG ở Week 3. Tri thức nghiên cứu thị trường trong S3 Vectors giờ đây sẽ được Planner Lambda truy xuất làm ngữ cảnh đầu vào khi điều phối phân tích danh mục.

## 5. Core Theory - Lý thuyết cốt lõi
- **Orchestrator Agent (Tác tử điều phối)**: Planner đóng vai trò đầu não tiếp nhận công việc, gọi Tagger để làm sạch dữ liệu danh mục nếu phát hiện instrument (công cụ tài chính) lạ, sau đó kích hoạt song song các worker agents để xử lý.
- **AWS SQS (Simple Queue Service)**: Dịch vụ hàng đợi tin nhắn serverless giúp lưu trữ tạm thời các yêu cầu phân tích, đảm bảo chịu tải tốt và không làm mất tin nhắn khi hệ thống backend bận.
- **Decoupled Architecture (Kiến trúc tách rời)**: Thiết kế hệ thống trong đó các thành phần giao tiếp qua hàng đợi tin nhắn thay vì gọi trực tiếp, giúp tăng khả năng chịu lỗi và dễ bảo trì.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng hoạt động tổng thể của hệ thống đa tác tử Alex:
1. **Input**: Người dùng gửi yêu cầu phân tích danh mục đầu tư từ NextJS Frontend.
2. **Processing steps**:
   - Frontend -> CloudFront -> API Gateway -> Backend API Lambda.
   - Backend API Lambda tạo bản ghi job trong database và đẩy tin nhắn yêu cầu vào SQS Queue.
   - SQS Queue kích hoạt Planner Lambda thực thi bất đồng bộ.
   - Planner Lambda kiểm tra database; nếu có cổ phiếu/ETF chưa được gán nhãn, gọi Tagger Lambda để phân loại vùng miền/ngành nghề.
   - Planner Lambda gọi song song 3 worker Lambdas: Reporter (phân tích danh mục), Charter (tạo JSON vẽ biểu đồ), và Retirement (tính toán Monte Carlo hưu trí).
   - Mỗi worker ghi trực tiếp kết quả phân tích vào cột JSONB tương ứng trong bảng `jobs` ở database.
3. **Output**: Planner Lambda cập nhật trạng thái job hoàn thành để frontend truy vấn và hiển thị báo cáo.

## 7. Techniques - Kỹ thuật sử dụng
- **Decoupled Parallel Processing (Xử lý song song tách rời)**:
  - Purpose - mục đích: Tối ưu hóa thời gian thực thi của hệ thống đa tác tử, tránh vượt quá giới hạn timeout (thời gian chờ) của AWS Lambda (15 phút).
  - When to use - dùng khi nào: Khi các worker agents (như Reporter, Charter, Retirement) không phụ thuộc dữ liệu chéo vào nhau.
  - Trade-off - đánh đổi: Đòi hỏi cơ chế quản lý bất đồng bộ phức tạp và khả năng xử lý concurrency (đồng thời) của tài khoản Bedrock phải đủ lớn để tránh lỗi rate limit.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Thiết lập một tác tử lớn thực hiện toàn bộ quy trình**
  - Pros: Code đơn giản, không cần hàng đợi SQS hay nhiều Lambda functions, không cần chia sẻ trạng thái database.
  - Cons: Context cực kỳ lớn dẫn đến chi phí token cao, dễ bị trôi ngữ cảnh, thời gian thực thi lâu dễ bị timeout.
  - When to choose: Các ứng dụng demo hoặc tác vụ xử lý danh mục cực nhỏ.
- **Option 2: Kiến trúc Multi-Agent phân tán trên Lambda (Lựa chọn của dự án)**
  - Pros: Từng tác tử chạy nhanh, chuyên biệt hóa cao, tận dụng được tính song song của Lambda, dễ dàng bảo trì độc lập.
  - Cons: Thiết lập hạ tầng Terraform rất phức tạp, cần cấu hình hàng đợi SQS và quản lý quyền IAM chéo giữa các Lambda.
  - When to choose: (Recommended) Các ứng dụng SaaS tài chính doanh nghiệp thực tế yêu cầu độ ổn định và khả năng scale cao.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Nghẽn tải hệ thống do rate limit của Bedrock API (Bedrock throttling).
  - Root cause: Nhiều Lambda worker cùng kích hoạt song song đồng thời vượt quá giới hạn concurrency mặc định của Bedrock cho một model.
  - Symptom: Một hoặc nhiều agent thất bại và ghi lỗi `ThrottlingException` vào cột error của bảng `jobs`.
  - Fix / prevention: Cấu hình giới hạn concurrency của Lambda function ở mức an toàn hoặc sử dụng Bedrock Provisioned Throughput cho môi trường sản xuất lớn.

## 11. Knowledge Extension - Kiến thức mở rộng
- **Mô hình kiến trúc Event-Driven (Kiến trúc hướng sự kiện)**: Việc sử dụng SQS để kích hoạt Lambda là một ví dụ điển hình của Event-Driven Architecture. Khi backend API đẩy tin nhắn vào SQS, nó lập tức phản hồi về cho frontend rằng "yêu cầu đang được xử lý". Người dùng không phải chờ đợi trực tiếp trên HTTP connection, giúp tăng trải nghiệm người dùng (UX) đáng kể.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Dự án Alex gồm 5 tác tử: Planner, Tagger, Reporter, Charter, và Retirement.
2. Tác tử thực chất là một LLM call với context và system prompt được thiết kế riêng.
3. Các tác tử của Alex được deploy dưới dạng các AWS Lambda serverless functions độc lập.
4. SQS Queue được dùng để truyền nhận yêu cầu bất đồng bộ từ API sang Planner.
5. Aurora Serverless v2 là nơi lưu trữ trạng thái chung cho tất cả các tác tử.

### Self-check questions
1. Tại sao việc coi các tác tử giống như một đội ngũ nhân sự bằng xương bằng thịt lại có thể dẫn đến lỗi thiết kế hệ thống?
2. Hãy mô tả cách thức Planner Lambda điều phối các worker agents chạy song song.

### Flashcards
- Q: Dịch vụ nào của AWS được dùng để làm hàng đợi bất đồng bộ cho Alex?
  A: AWS SQS (Simple Queue Service).
- Q: Database nào được chọn để lưu trữ thông tin portfolios của người dùng?
  A: AWS Aurora Serverless v2 PostgreSQL.

### Interview Q&A
- Q: Làm thế nào để giải quyết vấn đề chia sẻ kết quả tính toán giữa các Lambda agents chạy song song mà không làm xung đột ghi đè dữ liệu?
  A: (Recommended) Chúng ta thiết kế bảng `jobs` trong database với các cột JSONB độc lập cho từng agent (ví dụ: `report_payload`, `charts_payload`, `retirement_payload`). Khi một agent worker hoàn thành nhiệm vụ, nó chỉ thực hiện câu lệnh UPDATE vào đúng cột payload của mình dựa trên `job_id`. Planner không cần thu thập dữ liệu và ghi đè toàn bộ bản ghi, giúp loại bỏ hoàn toàn hiện tượng xung đột dữ liệu (race conditions).

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 91. Day 1 - Database Architecture for Production AI - Aurora Serverless for LLM Apps

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [91. Day 1 - Database Architecture for Production AI - Aurora Serverless for LLM Apps.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/91.%20Day%201%20-%20Database%20Architecture%20for%20Production%20AI%20-%20Aurora%20Serverless%20for%20LLM%20Apps.txt) - Đã dùng
- Slide: [Production W4D1.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D1.pdf) (Slide 10) - Đã dùng
- Code: Không có code trực tiếp cho lesson lý thuyết này.

## 2. Executive Summary - Tóm tắt cốt lõi
- Định nghĩa ba khái niệm database cơ bản trên AWS: **RDS** (dịch vụ quản lý cơ sở dữ liệu quan hệ), **Aurora** (engine quan hệ hiệu năng cao, độc quyền của Amazon), và **Aurora Serverless v2** (phiên bản co giãn tự động của Aurora).
- Aurora Serverless v2 tự động tăng/giảm dung lượng tính toán dựa trên tải thực tế, giúp tối ưu chi phí (scale xuống mức tối thiểu 0.5 ACU khi rảnh) và đảm bảo không có downtime (thời gian chết) khi tải tăng đột biến.
- Giới thiệu sơ bộ các dịch vụ cơ sở dữ liệu khác ngoài quan hệ trên AWS: **DynamoDB** (NoSQL key-value), **DocumentDB** (MongoDB-compatible), **Neptune** (graph database), **Timestream** (time-series), và **ElastiCache** (in-memory caching).
- Giải thích lý do dự án Alex chọn Aurora Serverless v2 PostgreSQL: Tích hợp sẵn tính năng **Data API** cho phép gọi cơ sở dữ liệu qua HTTP endpoint mà không cần quản lý connection pools hay kết nối VPC phức tạp từ Lambda.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Phân biệt được sự khác nhau giữa RDS, Aurora, và Aurora Serverless v2.
  - Hiểu cách thức tự động co giãn của Aurora Serverless v2 theo đơn vị ACU (Aurora Capacity Unit).
  - Nắm được sự khác biệt giữa các hệ cơ sở dữ liệu quan hệ và phi quan hệ (NoSQL) trên AWS.
- **Practical goals - mục tiêu thực hành**:
  - Đưa ra quyết định chọn lựa cơ sở dữ liệu phù hợp dựa trên yêu cầu cấu trúc dữ liệu và hạ tầng mạng (VPC vs Data API).
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao Aurora Serverless v2 lại là sự lựa chọn tối ưu cho các dự án serverless chạy trên AWS Lambda.
  - Sự khác nhau về cách thức quản lý giữa DynamoDB và RDS.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này chuyển dịch từ việc lưu trữ vector RAG phi cấu trúc (S3 Vectors ở Week 3) sang lưu trữ dữ liệu quan hệ có cấu trúc chặt chẽ (portfolios, positions của người dùng) cần tính nhất quán ACID cao.

## 5. Core Theory - Lý thuyết cốt lõi
- **Amazon RDS (Relational Database Service)**: Dịch vụ quản lý cơ sở dữ liệu quan hệ của AWS, tự động hóa việc backup, vá lỗi hệ thống và phân vùng vật lý.
- **Amazon Aurora**: Engine cơ sở dữ liệu quan hệ tương thích MySQL và PostgreSQL do AWS phát triển, tối ưu hóa tốc độ ghi và nhân bản lưu trữ trên nhiều Availability Zones (vùng sẵn sàng).
- **ACU (Aurora Capacity Unit)**: Đơn vị đo lường năng lực của Aurora Serverless. 1 ACU tương đương với khoảng 2GB RAM cùng CPU và tài nguyên mạng tương ứng.
- **Data API**: Cổng kết nối HTTP của Aurora cho phép ứng dụng gửi câu lệnh SQL qua HTTPS API, loại bỏ hoàn toàn yêu cầu thiết lập VPC bảo mật phức tạp cho các Lambda functions.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
`Không có pipeline rõ ràng trong tài liệu nguồn`
Bài học so sánh các kiến trúc cơ sở dữ liệu. Dưới đây là luồng hoạt động của Data API:
1. **Request**: Lambda function gửi câu lệnh SQL kèm theo API parameters qua HTTPS tới RDS Data API Endpoint.
2. **Authentication**: Data API xác thực IAM role của Lambda và giải mã credentials từ Secrets Manager.
3. **Execution**: Lệnh SQL được thực thi trực tiếp trên Aurora Serverless v2 cluster.
4. **Response**: Trả về dữ liệu kết quả dạng JSON có cấu trúc metadata đầy đủ về client Lambda.

## 7. Techniques - Kỹ thuật sử dụng
- **Database Elastic Scaling (Co giãn cơ sở dữ liệu đàn hồi)**:
  - Purpose - mục đích: Tự động hóa việc cấp phát tài nguyên RAM/CPU cho database mà không cần can thiệp thủ công, giảm thiểu chi phí khi hệ thống không hoạt động.
  - When to use - dùng khi nào: Các ứng dụng có lưu lượng truy cập biến động mạnh, không dự đoán trước được (như ứng dụng SaaS tài chính).
  - Trade-off - đánh đổi: Chi phí trên mỗi ACU giờ cao hơn so với việc thuê instance RDS cố định tương đương chạy 24/7.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Sử dụng Amazon DynamoDB (NoSQL)**
  - Pros: Khả năng scale cực lớn, thời gian phản hồi phần nghìn giây ổn định, tích hợp sâu với serverless.
  - Cons: Rất khó thực hiện các câu lệnh SQL JOIN phức tạp để tổng hợp số liệu danh mục đầu tư và phân bổ của nhiều tài khoản.
  - When to choose: Các ứng dụng chat, theo dõi trạng thái session, hoặc lưu trữ cấu hình đơn giản.
- **Option 2: Sử dụng RDS PostgreSQL truyền thống (Always-On Instance)**
  - Pros: Chi phí cố định rẻ cho các môi trường dev nhỏ (dùng t4g.micro instance).
  - Cons: Bắt buộc cấu hình Lambda chạy trong VPC, yêu cầu NAT Gateway (phát sinh thêm ~$30/tháng chi phí cố định) để Lambda có thể gọi ra ngoài internet (gọi Bedrock).
  - When to choose: Hệ thống doanh nghiệp lớn đã có sẵn hạ tầng VPC bảo mật và connection pool tập trung.
- **Option 3: Sử dụng Aurora Serverless v2 với Data API (Lựa chọn của dự án)**
  - Pros: Loại bỏ hoàn toàn sự phức tạp của VPC và NAT Gateway; Lambda kết nối cực kỳ nhanh qua HTTP; tự động scale.
  - Cons: Chi phí tối thiểu cao hơn instance RDS nhỏ nhất (0.5 ACU chạy liên tục tốn khoảng $43/tháng).
  - When to choose: (Recommended) Các dự án serverless phát triển nhanh trên Lambda cần tối ưu hóa kiến trúc mạng và giảm thiểu rủi ro bảo mật VPC.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Hóa đơn AWS tăng vọt do cấu hình sai ACU tối đa (ACU run-away cost).
  - Root cause: Thiết lập tham số `max_capacity` quá cao (ví dụ: 16 ACU) trên môi trường phát triển, kết hợp với các truy vấn SQL không được tối ưu hóa (như full table scan) chạy liên tục làm kích hoạt cơ chế tự động scale lên mức tối đa.
  - Symptom: Chi phí dịch vụ RDS tăng đột biến trong trang Billing.
  - Fix / prevention: Luôn giới hạn `max_capacity` ở mức tối thiểu cần thiết cho môi trường dev (ví dụ: `max_capacity = 1.0` hoặc `2.0`).

## 11. Knowledge Extension - Kiến thức mở rộng
- **Khởi động lạnh của Aurora Serverless v2**: Aurora Serverless v2 khắc phục hoàn toàn nhược điểm khởi động lạnh của phiên bản v1 (vốn mất từ 10-30 giây để kích hoạt từ trạng thái dừng). Phiên bản v2 luôn duy trì tối thiểu 0.5 ACU ở trạng thái hoạt động, giúp thời gian scale-up lên các mức dung lượng cao hơn diễn ra trong vòng mili-giây mà không làm gián đoạn kết nối của người dùng.

## 12. Study Pack - Gói ôn tập
### Must remember
1. RDS là dịch vụ quản lý cơ sở dữ liệu quan hệ hỗ trợ nhiều engine khác nhau.
2. Aurora là engine database quan hệ độc quyền của AWS tương thích MySQL/PostgreSQL.
3. Aurora Serverless v2 tự động co giãn năng lượng tính toán theo đơn vị ACU.
4. Data API cho phép truy cập database qua giao thức HTTP, loại bỏ yêu cầu VPC cho Lambda.
5. DynamoDB là giải pháp NoSQL chính của AWS, không hỗ trợ quan hệ SQL.

### Self-check questions
1. Tại sao việc sử dụng Data API lại giúp tiết kiệm chi phí NAT Gateway cho AWS Lambda?
2. Sự khác nhau giữa Aurora Serverless v1 và v2 về cơ chế co giãn tối thiểu (scale-to-zero) là gì?

### Flashcards
- Q: 1 ACU trong Aurora Serverless v2 tương đương với bao nhiêu RAM?
  A: Khoảng 2GB RAM.
- Q: Dịch vụ NoSQL key-value chính của AWS là gì?
  A: Amazon DynamoDB.

### Interview Q&A
- Q: Tại sao bạn lại chọn Aurora Serverless v2 PostgreSQL thay vì RDS PostgreSQL truyền thống cho một ứng dụng serverless chạy hoàn toàn trên AWS Lambda?
  A: (Recommended) Lý do lớn nhất là sự đơn giản trong kiến trúc mạng và tối ưu hóa kết nối. Lambda function hoạt động theo cơ chế co giãn rất nhanh; việc sử dụng RDS truyền thống yêu cầu ta phải đặt Lambda trong VPC (gây trễ khởi động lạnh) và sử dụng RDS Proxy để quản lý connection pooling nhằm tránh làm sập database khi có hàng ngàn instance Lambda cùng bật. Aurora Serverless v2 với Data API cho phép Lambda kết nối trực tiếp qua HTTP HTTPS API, bỏ qua hoàn toàn các giới hạn về connection pool và không yêu cầu thiết lập VPC, giúp tăng độ tin cậy và giảm 90% độ phức tạp của hạ tầng.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 92. Day 1 - Setting Up Aurora Serverless Database for Multi-Agent AI Systems

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [92. Day 1 - Setting Up Aurora Serverless Database for Multi-Agent AI Systems.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/92.%20Day%201%20-%20Setting%20Up%20Aurora%20Serverless%20Database%20for%20Multi-Agent%20AI%20Systems.txt) - Đã dùng
- Slide: [Production W4D1.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D1.pdf) (Slide 10) - Đã dùng
- Code:
  - [main.tf](file:///G:/AIProduction_t6_2026/production/week4/alex/terraform/5_database/main.tf) - Đã dùng và phân tích
  - [variables.tf](file:///G:/AIProduction_t6_2026/production/week4/alex/terraform/5_database/variables.tf) - Đã dùng
  - [outputs.tf](file:///G:/AIProduction_t6_2026/production/week4/alex/terraform/5_database/outputs.tf) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Thiết lập bổ sung chính sách bảo mật IAM tùy chỉnh `AlexRDSCustomPolicy` cấp quyền tạo, sửa, xóa cluster và thực thi Data API (`rds-data:ExecuteStatement`, v.v.).
- Đính kèm chính sách tùy chỉnh cùng các AWS managed policies (`AmazonRDSDataFullAccess`, `AWSLambda_FullAccess`, `AmazonSQSFullAccess`, `AmazonEventBridgeFullAccess`, `SecretsManagerReadWrite`) vào nhóm người dùng `AlexAccess` để cấp quyền cho tài khoản `aiengineer`.
- Triển khai hạ tầng database bằng Terraform trong thư mục `terraform/5_database`. Cấu hình tệp tin `terraform.tfvars` với region và ACU capacities (`min_capacity = 0.5`, `max_capacity = 1.0`).
- Phân tích chi tiết mã nguồn Terraform: Khởi tạo master password ngẫu nhiên thông qua `random_password`, lưu credentials tự động vào Secrets Manager, cấu hình default VPC subnet groups, security groups, và khởi tạo cụm database PostgreSQL 15.x bật sẵn HTTP endpoint (`enable_http_endpoint = true`).

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Nắm vững các phân quyền IAM cần thiết để vận hành Data API và quản trị database.
  - Hiểu cách thức cấu hình tự động tạo mật khẩu và lưu trữ credentials trong Secrets Manager thông qua Terraform.
  - Hiểu vai trò của default VPC và security groups đối với cơ sở dữ liệu serverless.
- **Practical goals - mục tiêu thực hành**:
  - Viết hoàn chỉnh file `terraform.tfvars` và chạy lệnh triển khai cụm database thành công.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao cụm database Aurora Serverless v2 vẫn cần được đặt trong VPC subnet group mặc dù chúng ta truy cập qua HTTP Data API bên ngoài internet.
  - Tác dụng của tham số `enable_http_endpoint` trong cấu hình Terraform.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này mở rộng nhóm quyền `AlexAccess` đã tạo ở Guide 1 để sẵn sàng cho việc cấp quyền database. Cụm database này sẽ nhận dữ liệu từ các agent được xây dựng ở Day 2.

## 5. Core Theory - Lý thuyết cốt lõi
- **Secrets Manager Integration**: Cơ chế tự động hóa quản lý mật khẩu của AWS, giúp lưu trữ an toàn thông tin đăng nhập database dưới dạng mã hóa và hỗ trợ xoay vòng khóa tự động.
- **Default VPC (Mạng ảo mặc định)**: Mạng logic biệt lập được AWS tự động tạo sẵn cho mỗi tài khoản, cung cấp các subnets mặc định để đặt các tài nguyên phần cứng như database.
- **enable_http_endpoint**: Tham số cấu hình trên cụm Aurora bắt buộc phải bật để kích hoạt RDS Data API Gateway, mở cổng HTTP HTTPS tiếp nhận yêu cầu từ SDK.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Quy trình triển khai cụm database bằng Terraform:
1. **Configuration**: Sao chép `terraform.tfvars.example` sang `terraform.tfvars`, điền AWS Region (ví dụ: `us-east-1`).
2. **Init**: Chạy lệnh `terraform init` để tải AWS providers.
3. **Execution**: Chạy `terraform apply`. Quy trình khởi tạo trên AWS:
   - Sinh mật khẩu ngẫu nhiên -> Tạo Secrets Manager Secret và lưu credentials -> Tìm Default VPC và các Subnets -> Tạo DB Subnet Group -> Tạo Security Group -> Tạo RDS Cluster (bật HTTP endpoint) -> Tạo RDS Cluster Instance liên kết.
4. **Output**: Trả về Cluster ARN và Secret ARN để ghi vào tệp tin `.env`.

## 7. Techniques - Kỹ thuật sử dụng
- **Terraform Secrets Manager Auto-Population (Tự động điền Secrets Manager bằng Terraform)**:
  - Purpose - mục đích: Loại bỏ hoàn toàn việc lưu trữ mật khẩu tĩnh (hardcoded password) trong mã nguồn hạ tầng, tăng độ an toàn thông tin.
  - When to use - dùng khi nào: Triển khai bất kỳ cơ sở dữ liệu quan hệ nào bằng IaC (Infrastructure as Code).
  - Code: Kết hợp resource `random_password` và `aws_secretsmanager_secret_version` để mã hóa mật khẩu tự động sang JSON string trước khi lưu.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích chi tiết file cấu hình [main.tf](file:///G:/AIProduction_t6_2026/production/week4/alex/terraform/5_database/main.tf)

- **Tạo mật khẩu ngẫu nhiên an toàn**:
  ```hcl
  # G:\AIProduction_t6_2026\production\week4\alex\terraform\5_database\main.tf
  resource "random_password" "master_password" {
    length           = 16
    special          = true
    override_special = "!#$%&*()-_=+[]{}<>:?" # Loại bỏ các ký tự gây lỗi cú pháp SQL
  }
  ```

- **Đóng gói và lưu thông tin đăng nhập vào Secrets Manager**:
  ```hcl
  resource "aws_secretsmanager_secret" "db_credentials" {
    name = "alex-aurora-credentials-${random_id.suffix.hex}"
  }

  resource "aws_secretsmanager_secret_version" "db_credentials" {
    secret_id     = aws_secretsmanager_secret.db_credentials.id
    secret_string = jsonencode({
      username = "alex_admin"
      password = random_password.master_password.result
    })
  }
  ```

- **Khai báo cụm Aurora Serverless v2 bật HTTP Endpoint**:
  ```hcl
  resource "aws_rds_cluster" "aurora_cluster" {
    cluster_identifier      = "alex-aurora-cluster"
    engine                  = "aurora-postgresql"
    engine_version          = "15.4" # Bản PostgreSQL ổn định
    database_name           = "alex"
    master_username         = jsondecode(aws_secretsmanager_secret_version.db_credentials.secret_string)["username"]
    master_password         = jsondecode(aws_secretsmanager_secret_version.db_credentials.secret_string)["password"]
    db_subnet_group_name    = aws_db_subnet_group.db_subnets.name
    vpc_security_group_ids  = [aws_security_group.db_security_group.id]
    skip_final_snapshot     = true
    enable_http_endpoint    = true # BẮT BUỘC để Lambda có thể kết nối không VPC

    serverlessv2_scaling_configuration {
      min_capacity = var.min_capacity
      max_capacity = var.max_capacity
    }
  }
  ```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Khai báo VPC tùy chỉnh (Custom VPC) cho database**
  - Pros: Bảo mật mạng cô lập hoàn toàn, dễ dàng kiểm soát luồng traffic mạng doanh nghiệp.
  - Cons: Cấu hình cực kỳ phức tạp (phải tạo subnets, route tables, internet gateways, NAT gateways), thời gian deploy lâu.
  - When to choose: Các hệ thống tài chính enterprise lớn bắt buộc tuân thủ các chuẩn bảo mật nghiêm ngặt (PCI-DSS).
- **Option 2: Sử dụng Default VPC và Subnets (Lựa chọn của khóa học)**
  - Pros: Triển khai nhanh gọn, tận dụng hạ tầng sẵn có của tài khoản AWS mà không tốn thêm chi phí NAT Gateway.
  - Cons: Chia sẻ chung tài nguyên mạng mặc định, không phù hợp cho các môi trường sản xuất lớn cần cô lập hoàn toàn.
  - When to choose: (Recommended) Giai đoạn xây dựng MVP, học tập thực hành.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Lỗi `HttpEndpointNotEnabledException` khi kết nối database từ code.
  - Root cause: Học viên cấu hình sai hoặc quên đặt giá trị `enable_http_endpoint = true` trong tệp Terraform.
  - Symptom: Lệnh apply chạy thành công nhưng chạy code Python gọi Data API bị crash ngay lập tức.
  - Fix / prevention: Chạy lệnh CLI để ép bật HTTP endpoint trên AWS Console ngay lập tức mà không cần rebuild: `aws rds modify-db-cluster --db-cluster-identifier alex-aurora-cluster --enable-http-endpoint --apply-immediately`.

## 11. Knowledge Extension - Kiến thức mở rộng
- **Mật khẩu ngẫu nhiên đặc biệt**: Hàm `override_special` trong Terraform cực kỳ quan trọng đối với các database engine. Một số ký tự đặc biệt mặc định (như `@`, `/`, hoặc `"`) có thể phá vỡ chuỗi kết nối SQL connection string hoặc gây lỗi biên dịch câu lệnh SQL chèn dữ liệu. Việc giới hạn các ký tự đặc biệt an toàn giúp tránh các lỗi kết nối database rất khó phát hiện.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Nhóm `AlexAccess` cần được đính kèm chính sách `AlexRDSCustomPolicy`.
2. Biến `min_capacity` nên đặt là 0.5 ACU để tối ưu hóa chi phí phát triển.
3. Tham số `enable_http_endpoint = true` là bắt buộc để kích hoạt Data API.
4. Mật khẩu database được tạo ngẫu nhiên và quản lý bởi AWS Secrets Manager.
5. Triển khai hạ tầng bằng lệnh `terraform apply` trong thư mục `terraform/5_database`.

### Self-check questions
1. Tại sao tệp Terraform lại sử dụng hàm `jsonencode` khi lưu trữ mật khẩu vào Secrets Manager?
2. Hãy chỉ ra tài nguyên Terraform chịu trách nhiệm cấu hình khả năng co giãn (scaling limits) cho cụm database.

### Flashcards
- Q: Lệnh của AWS CLI để sửa đổi bật HTTP endpoint cho cluster là gì?
  A: `aws rds modify-db-cluster --db-cluster-identifier [cluster-id] --enable-http-endpoint --apply-immediately`.
- Q: Tài nguyên Terraform dùng để sinh mật khẩu tự động là gì?
  A: `random_password`.

### Interview Q&A
- Q: Tại sao cụm cơ sở dữ liệu Aurora Serverless v2 vẫn bắt buộc phải cấu hình `db_subnet_group_name` nằm trong VPC mặc dù chúng ta bật tính năng Data API để gọi từ ngoài internet?
  A: (Recommended) Aurora Serverless v2 về mặt vật lý vẫn là các instances cơ sở dữ liệu chạy trên hạ tầng compute EC2 của AWS. Để đảm bảo an toàn dữ liệu và khả năng định tuyến nội bộ của AWS, cụm database bắt buộc phải được gắn vào một mạng ảo VPC. Khi chúng ta bật Data API, AWS sẽ đứng ra dựng một API Gateway nội bộ của họ (được quản lý hoàn toàn) để làm cầu nối HTTPS. API Gateway này tiếp nhận yêu cầu từ internet, xác thực quyền IAM và sau đó giao tiếp an toàn với các database instances nằm bên trong VPC subnet group. Do đó, việc cấu hình VPC subnet là bắt buộc để duy trì hạ tầng mạng vật lý cho cụm database hoạt động.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 93. Day 1 - Setting Up Aurora Database Infrastructure for Production AI Apps

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [93. Day 1 - Setting Up Aurora Database Infrastructure for Production AI Apps.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/93.%20Day%201%20-%20Setting%20Up%20Aurora%20Database%20Infrastructure%20for%20Production%20AI%20Apps.txt) - Đã dùng
- Code:
  - [client.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/src/client.py) - Đã dùng và phân tích
  - [schemas.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/src/schemas.py) - Đã dùng và phân tích
  - [models.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/src/models.py) - Đã dùng và phân tích
  - [test_data_api.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/test_data_api.py) - Đã dùng và phân tích
  - [run_migrations.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/run_migrations.py) - Đã dùng và phân tích
  - [seed_data.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/seed_data.py) - Đã dùng và phân tích

## 2. Executive Summary - Tóm tắt cốt lõi
- Lưu trữ các giá trị outputs từ Terraform (`cluster_arn`, `secret_arn`) vào tệp tin `.env` ở root project.
- Kiểm tra kết nối Data API bằng cách chạy `uv run test_data_api.py` tại thư mục `backend/database/` (kết nối thành công qua HTTPS, không cần VPC).
- Thực thi chạy migrations tạo các bảng dữ liệu bằng lệnh `uv run run_migrations.py` (chạy script Python đọc và thực thi tệp SQL `001_schema.sql`).
- Seed dữ liệu tham chiếu công cụ tài chính gồm 22 ETFs phổ biến (như SPY, QQQ, BND...) bằng lệnh `uv run seed_data.py`.
- Khám phá kiến trúc database package của Alex: `client.py` bóc tách định dạng dữ liệu thô của Data API thành dạng dictionary Python; `schemas.py` khai báo Pydantic models thực hiện kiểm tra dữ liệu đầu vào (ví dụ: đảm bảo tổng phân bổ allocation của các ETF luôn bằng 100%); `models.py` cung cấp query builder tương tác dữ liệu.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu cách thức cấu hình tệp tin môi trường `.env` kết nối dịch vụ Python với database AWS.
  - Hiểu cơ chế phân tách và giải mã định dạng dữ liệu phức tạp (như JSON/JSONB) trả về từ RDS Data API.
  - Nắm vững nguyên lý hoạt động của Pydantic validation trong kiểm soát chất lượng dữ liệu.
- **Practical goals - mục tiêu thực hành**:
  - Chạy thành công các script Python kiểm tra kết nối, migrations, và seed data.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao lại sử dụng Pydantic để validate tổng phân bổ (100%) thay vì đặt check constraint trong SQL.
  - Cách `DataAPIClient` bóc tách các trường giá trị `longValue`, `stringValue`, `isNull`.

## 4. Previous Context - Liên hệ với bài trước
- Sử dụng trực tiếp hạ tầng Aurora Serverless v2 đã deploy ở bài 92. Bản đồ outputs được đồng bộ hóa sang tệp `.env` đóng vai trò là "cầu nối" cho mã nguồn backend.

## 5. Core Theory - Lý thuyết cốt lõi
- **Data API Response Parsing**: RDS Data API trả về kết quả truy vấn dưới dạng cấu trúc JSON rất phức tạp (mỗi cột là một object chứa kiểu dữ liệu, ví dụ: `{"stringValue": "val"}`). Client phải tự viết hàm bóc tách về kiểu dữ liệu gốc của Python.
- **Pydantic Validation**: Cơ chế runtime validation (kiểm chứng thời gian chạy) giúp ngăn chặn dữ liệu lỗi lọt vào database, cực kỳ quan trọng khi nhận dữ liệu từ các LLMs vốn có tính ngẫu nhiên (hallucination).

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng khởi chạy và thiết lập cơ sở dữ liệu:
1. **Update Environment**: Sao chép `cluster_arn` và `secret_arn` vào `.env`.
2. **Connectivity Check**: Chạy `test_data_api.py` kiểm tra cổng HTTP Data API.
3. **Migration Execution**: Chạy `run_migrations.py`. Script đọc tệp SQL, gửi các lệnh CREATE TABLE sang Data API.
4. **Seed Reference Data**: Chạy `seed_data.py`. Vòng lặp gửi các bản ghi ETF chứa tên, symbol, giá, và cơ cấu phân bổ JSON sang database.
5. **Output**: Cơ sở dữ liệu Aurora sẵn sàng với đầy đủ bảng và 22 bản ghi ETF chuẩn.

## 7. Techniques - Kỹ thuật sử dụng
- **JSON Auto-Parsing in Client (Tự động giải mã JSON trong client)**:
  - Purpose - mục đích: Tự động chuyển đổi các cột kiểu dữ liệu JSONB trong PostgreSQL thành dictionary/list của Python ngay khi truy vấn, tinh giản code nghiệp vụ.
  - When to use: Xây dựng các lớp truy cập dữ liệu (data access layers) có sử dụng các cột lưu trữ tài liệu (document/metadata).
  - Code: Kiểm tra ký tự mở đầu `[` hoặc `{` của trường `stringValue` và thực hiện `json.loads()`.

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích file [client.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/src/client.py)
- **Bóc tách giá trị từ Data API response**:
  ```python
  # G:\AIProduction_t6_2026\production\week4\alex\backend\database\src\client.py
  def _extract_value(self, field: Dict) -> Any:
      """Giải mã các kiểu dữ liệu đóng gói của RDS Data API về kiểu Python tương ứng"""
      if field.get("isNull"):
          return None
      elif "booleanValue" in field:
          return field["booleanValue"]
      elif "longValue" in field:
          return field["longValue"]
      elif "doubleValue" in field:
          return field["doubleValue"]
      elif "stringValue" in field:
          value = field["stringValue"]
          # Tự động parse JSON nếu chuỗi lưu trữ dạng JSON (dùng cho JSONB)
          if value and value[0] in ["{", "["]:
              try:
                  return json.loads(value)
              except json.JSONDecodeError:
                  pass
          return value
      elif "blobValue" in field:
          return field["blobValue"]
      return None
  ```

### Phân tích file [schemas.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/src/schemas.py)
- **Kiểm tra tỷ lệ phân bổ của công cụ tài chính bằng Pydantic**:
  ```python
  # G:\AIProduction_t6_2026\production\week4\alex\backend\database\src\schemas.py
  class RegionAllocation(BaseModel):
      allocations: Dict[RegionType, float] = Field(
          description="Percentage allocation by geographic region. Must sum to 100."
      )

      @field_validator("allocations")
      def validate_sum(cls, v):
          total = sum(v.values())
          # Cho phép sai số nhỏ (dưới 3%) do sai số của số thực dấu phẩy động (float)
          if abs(total - 100) > 3:
              raise ValueError(f"Region allocations must sum to 100, got {total}")
          return v
  ```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Dùng thư viện SQLAlchemy ORM kết hợp PostgreSQL driver**
  - Pros: Code hướng đối tượng đẹp mắt, tự động sinh migrations, có cộng đồng sử dụng cực lớn.
  - Cons: Không thể chạy trực tiếp trên Lambda trừ phi đặt Lambda vào VPC và thiết lập RDS Proxy (do SQLAlchemy duy trì các kết nối TCP socket liên tục).
  - When to choose: Các ứng dụng chạy trên container truyền thống (App Runner, ECS) không bị giới hạn bởi connection pooling của serverless.
- **Option 2: Bọc trực tiếp Boto3 RDS-Data Client (Lựa chọn của dự án)**
  - Pros: (Recommended) Hoạt động hoàn hảo trên serverless Lambda không VPC; kết nối qua HTTP siêu nhẹ; không lo bị cạn kiệt connection pool.
  - Cons: Phải tự viết mã SQL thô (raw SQL) và tự viết bộ parser giải mã kiểu dữ liệu từ JSON.
  - When to choose: Phát triển các ứng dụng serverless microservices quy mô nhỏ và vừa trên AWS Lambda.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Lỗi kiểu dữ liệu khi chèn số thực Decimal vào database qua Data API.
  - Root cause: Data API không hỗ trợ truyền trực tiếp đối tượng `Decimal` của Python vào parameter.
  - Symptom: Boto3 ném lỗi validation parameter type.
  - Fix / prevention: Trong hàm `_build_parameters` của `client.py`, chuyển đổi đối tượng `Decimal`, `date`, hoặc `datetime` thành dạng `stringValue` (chuỗi văn bản) kèm ép kiểu trong câu SQL (ví dụ: `:param::numeric` hoặc `:param::date`).

## 11. Knowledge Extension - Kiến thức mở rộng
- **LiteLLM và Bedrock Region Config**: Khi gọi Bedrock qua thư viện LiteLLM, LiteLLM yêu cầu đặt biến môi trường tên là `AWS_REGION_NAME` để xác định vùng vật lý chứa model. Việc đặt sai biến môi trường này (ví dụ đặt thành `AWS_REGION` chuẩn) sẽ khiến LiteLLM không tìm thấy model và ném lỗi không tương thích.

## 12. Study Pack - Gói ôn tập
### Must remember
1. `AURORA_CLUSTER_ARN` và `AURORA_SECRET_ARN` là hai tham số bắt buộc trong `.env`.
2. Script `test_data_api.py` dùng để xác minh kết nối cơ sở dữ liệu serverless.
3. Migrations được chạy bằng cách thực thi script `run_migrations.py`.
4. Pydantic validator dùng để chặn dữ liệu sai (tổng phân bổ khác 100%) trước khi lưu database.
5. Thư viện `boto3` client `rds-data` được dùng làm cổng kết nối SQL chính.

### Self-check questions
1. Tại sao hàm `validate_sum` trong Pydantic schema lại cho phép sai số chênh lệch tối đa là 3%?
2. Bảng dữ liệu trả về từ rds-data client có cấu trúc cột như thế nào trong tệp `client.py`?

### Flashcards
- Q: File SQL chứa cấu trúc bảng cơ sở dữ liệu ban đầu tên là gì?
  A: `001_schema.sql`.
- Q: Lệnh chèn dữ liệu ETF tham chiếu vào database là gì?
  A: `uv run seed_data.py`.

### Interview Q&A
- Q: Làm thế nào để xử lý việc chuyển đổi dữ liệu kiểu JSONB hoặc Numeric sang dạng an toàn khi sử dụng Data API của AWS để thực hiện các câu lệnh INSERT/UPDATE?
  A: (Recommended) RDS Data API yêu cầu truyền tham số dạng chuẩn JSON. Đối với kiểu Numeric (Decimal) hoặc JSONB (dict/list của Python), ta thực hiện chuyển đổi giá trị thành chuỗi (`str` hoặc `json.dumps`) trong code Python. Đồng thời trong câu lệnh SQL, ta bắt buộc phải sử dụng cơ chế ép kiểu tường minh của PostgreSQL (ví dụ: `INSERT INTO instruments (allocation_regions) VALUES (:allocation_regions::jsonb)` và `master_password = :master_password::numeric`). Việc ép kiểu này giúp PostgreSQL hiểu đúng kiểu dữ liệu nhị phân cần lưu trữ, tránh lỗi không khớp kiểu dữ liệu giữa client và server.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 94. Day 1 - Setting Up Production Database Architecture for AI Agent Systems

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [94. Day 1 - Setting Up Production Database Architecture for AI Agent Systems.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/94.%20Day%201%20-%20Setting%20Up%20Production%20Database%20Architecture%20for%20AI%20Agent%20Systems.txt) - Đã dùng
- Slide: [Production W4D1.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D1.pdf) (Slide 4, 6, 7, 8, 9, 10) - Đã dùng
- Code:
  - [001_schema.sql](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/migrations/001_schema.sql) - Đã dùng và phân tích
  - [reset_db.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/reset_db.py) - Đã dùng và phân tích
  - [verify_database.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/verify_database.py) - Đã dùng và phân tích

## 2. Executive Summary - Tóm tắt cốt lõi
- Phân tích sơ đồ thực thể ERD của Alex gồm 5 bảng: `users` (thông tin mục tiêu hưu trí và asset allocation targets), `accounts` (tài khoản đầu tư, ví dụ: 401k, Roth IRA), `positions` (vị thế chứng khoán trong tài khoản), `instruments` (thông tin ETF/cổ phiếu tham chiếu toàn cầu), và `jobs` (quản lý trạng thái công việc phân tích).
- Thiết kế bảng `jobs` sử dụng các trường JSONB chuyên biệt cho kết quả của từng agent (`report_payload`, `charts_payload`, `retirement_payload`, `summary_payload`). Thiết kế này giúp các agent worker ghi dữ liệu song song độc lập mà không bị ghi đè hay cần merge (hợp nhất) phức tạp.
- Chạy script reset database `reset_db.py --with-test-data` để drop toàn bộ bảng cũ, chạy lại migrations, seed data, và khởi tạo tài khoản test `test_user_001` có 3 accounts và 5 positions trong account 401k.
- Chạy script `verify_database.py` để kiểm tra sức khỏe cơ sở dữ liệu (xác nhận tất cả các bảng tồn tại, tỷ lệ phân bổ của các ETF cộng lại luôn bằng 100%, index và trigger hoạt động tốt).
- Lưu ý chi phí: Thực hiện `terraform destroy` ở thư mục `terraform/5_database` khi dừng làm việc để tránh phí duy trì cụm Aurora Serverless v2.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu kiến trúc ERD quan hệ của một ứng dụng quản lý danh mục tài chính cá nhân.
  - Hiểu ưu điểm của kiểu dữ liệu JSONB trong việc lưu trữ kết quả phân tích AI không cấu trúc.
  - Nắm được cách thiết kế bảng để loại bỏ xung đột dữ liệu (race conditions) khi nhiều tác tử cùng ghi song song.
- **Practical goals - mục tiêu thực hành**:
  - Thực hiện reset database, chèn dữ liệu test user và chạy script kiểm định cơ sở dữ liệu thành công.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao bảng `jobs` lại tách thành các payload riêng biệt thay vì lưu chung vào một cột JSONB lớn.
  - Cách thức hoạt động của trigger tự động cập nhật `updated_at` trong PostgreSQL.

## 4. Previous Context - Liên hệ with các bài trước
- Bài học này hoàn tất tầng lưu trữ dữ liệu (Day 1 - Database) chuẩn bị đầy đủ dữ liệu ETF tham chiếu và test user portfolio để các Lambda agents ở Day 2 có thể truy vấn và ghi kết quả phân tích.

## 5. Core Theory - Lý thuyết cốt lõi
- **JSONB (Binary JSON)**: Kiểu dữ liệu lưu trữ JSON dưới dạng nhị phân phân rã của PostgreSQL. Cho phép truy vấn nhanh các thuộc tính con, hỗ trợ lập chỉ mục (GGIN indexes) và tiết kiệm không gian lưu trữ hơn so với văn bản JSON thô.
- **PostgreSQL Triggers**: Đoạn code lưu trữ tự động kích hoạt trước hoặc sau các sự kiện INSERT/UPDATE/DELETE trên một bảng để thực hiện các nghiệp vụ tự động (như ghi nhận thời gian thay đổi).

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng hoạt động của script reset_db:
1. **Drop Tables**: Drop toàn bộ 5 bảng hiện tại nếu tồn tại trên cơ sở dữ liệu.
2. **Schema Creation**: Chạy tệp SQL khởi tạo các bảng và triggers tự động cập nhật `updated_at`.
3. **Reference Seeding**: Nạp 22 ETFs thông dụng làm dữ liệu tham chiếu toàn cục.
4. **Test Data Generation**: Tạo test user `test_user_001` -> Tạo 3 accounts -> Tạo 5 positions liên kết.
5. **Output**: Trả về báo cáo trạng thái database hoàn tất sẵn sàng hoạt động.

## 7. Techniques - Kỹ thuật sử dụng
- **Parallel Output Writing (Ghi kết quả song song)**:
  - Purpose - mục đích: Hỗ trợ các tác tử worker ghi kết quả độc lập bất đồng bộ vào database mà không gây khóa chết (deadlocks) hoặc ghi đè kết quả của tác tử khác.
  - When to use: Xây dựng các bảng lưu trữ kết quả phân tích trong kiến trúc multi-agent chạy song song.
  - Design: Tách nhỏ các trường JSONB trong bảng `jobs` tương ứng với từng tác tử (`report_payload` cho Reporter, `charts_payload` cho Charter...).

## 8. Code Walkthrough - Phân tích code nếu có
### Phân tích file SQL [001_schema.sql](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/database/migrations/001_schema.sql)
- **Thiết lập trigger tự động cập nhật timestamp**:
  ```sql
  -- G:\AIProduction_t6_2026\production\week4\alex\backend\database\migrations\001_schema.sql
  CREATE OR REPLACE FUNCTION update_updated_at_column()
  RETURNS TRIGGER AS $$
  BEGIN
      NEW.updated_at = NOW();
      RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;

  -- Đính kèm trigger vào bảng users (áp dụng tương tự cho các bảng khác)
  CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
      FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
  ```

- **Khai báo bảng `jobs` phục vụ multi-agent**:
  ```sql
  CREATE TABLE IF NOT EXISTS jobs (
      id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
      clerk_user_id VARCHAR(255) REFERENCES users(clerk_user_id) ON DELETE CASCADE,
      job_type VARCHAR(50) NOT NULL,
      status VARCHAR(20) DEFAULT 'pending',
      request_payload JSONB,
      
      -- Tách biệt các trường kết quả của từng Agent để ghi song song
      report_payload JSONB,     -- Reporter agent's markdown analysis
      charts_payload JSONB,     -- Charter agent's visualization data
      retirement_payload JSONB, -- Retirement agent's projections
      summary_payload JSONB,    -- Planner's final summary/metadata
      
      error_message TEXT,
      created_at TIMESTAMP DEFAULT NOW(),
      started_at TIMESTAMP,
      completed_at TIMESTAMP,
      updated_at TIMESTAMP DEFAULT NOW()
  );
  ```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Thiết kế bảng `jobs` với một cột payload JSONB duy nhất**
  - Pros: Bảng dữ liệu cực kỳ tối giản, dễ mở rộng thêm các loại agent mới mà không cần chỉnh sửa SQL schema (no migrations needed).
  - Cons: Nguy cơ xung đột dữ liệu (race conditions) cực cao khi các Lambda agents chạy song song cố gắng chèn kết quả của mình vào cùng một trường JSONB của một `job_id` cùng một lúc.
  - When to choose: Hệ thống có luồng chạy tuần tự tuyến tính, các agent cập nhật dữ liệu nối tiếp nhau.
- **Option 2: Tách biệt các cột payload JSONB cho từng Agent (Lựa chọn của dự án)**
  - Pros: (Recommended) Cho phép ghi song song bất đồng bộ tuyệt đối từ các worker agents độc lập; gỡ lỗi và truy vấn trực tiếp cột kết quả của từng agent rất nhanh.
  - Cons: Yêu cầu cập nhật schema và chạy migrations nếu hệ thống bổ sung thêm tác tử worker mới (ví dụ thêm TaxOptimizer agent).
  - When to choose: Các ứng dụng đa tác tử chạy song song thực tế cần độ tin cậy dữ liệu cao.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Sai lệch dữ liệu `.env` sau khi chạy recreate database.
  - Root cause: Học viên chạy `terraform destroy` để tắt database tránh tốn chi phí. Khi chạy lại `terraform apply`, AWS Secrets Manager tạo ra một credentials ARN mới. Tuy nhiên, học viên quên không cập nhật lại giá trị `AURORA_SECRET_ARN` mới này vào `.env`.
  - Symptom: Chạy các script test hoặc seed dữ liệu báo lỗi `SecretsManager: ResourceNotFoundException` hoặc access denied.
  - Fix / prevention: Luôn cập nhật lại tệp `.env` với các ARNs mới từ outputs của Terraform mỗi khi khởi tạo lại cụm database.

## 11. Knowledge Extension - Kiến thức mở rộng
- **UUID v4 làm Khóa chính (Primary Key)**: Việc sử dụng UUID v4 (sinh ngẫu nhiên) thay vì ID tự tăng (Integer auto-increment) là chuẩn thiết kế bắt buộc cho các hệ thống serverless và phân tán. Nó giúp client (hoặc Lambda API) tự sinh ID duy nhất cho bản ghi mới ngay tại local mà không cần truy vấn database để lấy số tự tăng tiếp theo, loại bỏ nghẽn cổ chai và ngăn chặn lộ thông tin quy mô hệ thống qua ID (ví dụ: đối thủ đoán được số lượng user qua ID tự tăng).

## 12. Study Pack - Gói ôn tập
### Must remember
1. Sơ đồ dữ liệu gồm 5 bảng: users, accounts, positions, instruments, và jobs.
2. Bảng `jobs` chia nhỏ các trường payload để hỗ trợ các agent ghi song song bất đồng bộ.
3. Lệnh reset database và tạo dữ liệu test: `uv run reset_db.py --with-test-data`.
4. Script `verify_database.py` dùng để kiểm định sức khỏe và tính nhất quán của cơ sở dữ liệu.
5. Cần destroy database bằng Terraform khi dừng làm việc để tránh phát sinh chi phí.

### Self-check questions
1. Hãy mô tả mối quan hệ giữa bảng `positions` và bảng `instruments` trong sơ đồ ERD của Alex.
2. Bảng `jobs` lưu trữ những thông tin gì từ Planner và các worker agents?

### Flashcards
- Q: Lệnh chạy kiểm định tính toàn vẹn của database là gì?
  A: `uv run verify_database.py`.
- Q: Kiểu dữ liệu nào được PostgreSQL dùng để lưu trữ JSON dạng nhị phân hiệu năng cao?
  A: JSONB.

### Interview Q&A
- Q: Tại sao việc chèn dữ liệu test portfolio của người dùng bằng UUID v4 lại giúp tối ưu hóa hiệu năng chèn (insert performance) trong các cơ sở dữ liệu phân tán quy mô lớn?
  A: (Recommended) Sử dụng UUID v4 cho phép ứng dụng chèn dữ liệu bất đồng bộ từ nhiều nguồn (như nhiều Lambda functions chạy song song) mà không cần có một node trung tâm điều phối cấp phát ID tự tăng. Điều này loại bỏ hoàn toàn các khóa khóa hàng (row locking) trên bảng để lấy ID tiếp theo. Đối với các cơ sở dữ liệu phân tán (như Aurora với nhiều read replicas), UUID v4 giúp dữ liệu được phân bổ đều trên các phân vùng vật lý (data shards), tránh hiện tượng "hot hotspotting" (nhiều bản ghi chèn liên tiếp ghi vào cùng một phân vùng ổ đĩa như khi dùng ID tự tăng tuyến tính), từ đó tăng tốc độ ghi dữ liệu tổng thể của hệ thống.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.
