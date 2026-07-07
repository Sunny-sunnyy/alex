# Day 2 - Building Multi-Agent Financial AI Systems with Context Engineering

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

---

# 95. Day 2 - Building Multi-Agent Financial AI Systems with Context Engineering

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [95. Day 2 - Building Multi-Agent Financial AI Systems with Context Engineering.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/95.%20Day%202%20-%20Building%20Multi-Agent%20Financial%20AI%20Systems%20with%20Context%20Engineering.txt) - Đã dùng
- Slide: [Production W4D2.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D2.pdf) (Slide 1, 2, 3) - Đã dùng
- Code: Không có code trực tiếp cho lesson lý thuyết này.
- Summary lịch sử: [day1_summary.md](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/day1_summary.md) - Đã dùng làm ngữ cảnh nền.

## 2. Executive Summary - Tóm tắt cốt lõi
- Bài học mở đầu Day 2 của Tuần 4 tập trung vào việc triển khai thực tế 5 tác tử (agents) cốt lõi của dự án Alex trên nền tảng AWS Lambda.
- Giới thiệu khái niệm chuyển dịch quan trọng từ prompt engineering (kỹ nghệ gợi ý) sang **context engineering (kỹ nghệ ngữ cảnh)**.
- Context engineering được định nghĩa là kỷ nghệ thiết kế và xây dựng các hệ thống động nhằm cung cấp đúng thông tin và công cụ, đúng định dạng, đúng thời điểm để LLM hoàn thành một tác vụ cụ thể.
- Thành phần cấu thành một ngữ cảnh đầy đủ của tác tử bao gồm: system instructions (chỉ dẫn hệ thống), long term memory (trí nhớ dài hạn - RAG), tools (công cụ), short term memory (trí nhớ ngắn hạn - lịch sử hội thoại) và user prompt (gợi ý người dùng).
- Nhấn mạnh lời khuyên của kỹ sư Philip Schmidt (DeepMind) về việc tránh over-engineering (thiết kế quá phức tạp) cấu trúc subagents (tác tử phụ) khi các mô hình tương lai đơn giản hơn có thể giải quyết tốt hơn.
- Khuyến khích đọc blog của Simon Willison để theo dõi các xu hướng thực tế về AI Agents.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu rõ định nghĩa và vai trò của context engineering trong kiến trúc tác tử hiện đại.
  - Phân biệt các thành phần của ngữ cảnh: system prompt, long term memory (RAG), tools, short term memory và task.
  - Nắm được triết lý thiết kế hệ thống tác tử tối giản, tập trung vào việc định hình ngữ cảnh thay vì lạm dụng framework.
- **Practical goals - mục tiêu thực hành**:
  - Nhận diện các thành phần ngữ cảnh cần thiết khi lập trình một tác tử cụ thể.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao việc tập trung vào chất lượng ngữ cảnh (context quality) lại quan trọng hơn việc lựa chọn framework lập trình tác tử.
  - Ý nghĩa câu nói của Philip Schmidt: "Sự khác biệt giữa một bản demo rẻ tiền và một tác tử kỳ diệu nằm ở chất lượng ngữ cảnh bạn cung cấp."

## 4. Previous Context - Liên hệ với bài trước
- Bài học này tiếp nối trực tiếp từ Week 4 Day 1 (thiết kế schema database quan hệ) và Week 3 (Researcher Agent thu thập tri thức đưa vào S3 Vectors). Context engineering chính là cách thức tích hợp các mảnh ghép này (RAG từ S3 Vectors và dữ liệu portfolios từ database) thành đầu vào chất lượng cao cho các Lambda Agents.

## 5. Core Theory - Lý thuyết cốt lõi
- **Context engineering (Kỹ nghệ ngữ cảnh)**: Kỷ nghệ thiết kế và xây dựng các hệ thống động nhằm cung cấp đúng thông tin và công cụ, đúng định dạng, đúng thời điểm cho LLM.
- **System instructions (Chỉ dẫn hệ thống)**: Các chỉ thị cố định định hình vai trò, nhiệm vụ và các giới hạn hành vi của tác tử.
- **Long term memory (Trí nhớ dài hạn)**: Dữ liệu lịch sử hoặc tri thức bên ngoài được truy xuất thông qua RAG (ở đây là S3 Vectors).
- **Short term memory (Trí nhớ ngắn hạn)**: Lịch sử tương tác của người dùng trong phiên làm việc hiện tại hoặc dữ liệu truyền nhận giữa các tác tử.
- **Subagent (Tác tử phụ)**: Các tác tử nhỏ chuyên biệt được gọi bởi một tác tử chính (loop-based agent) để thực hiện các nhiệm vụ con đáng tin cậy hơn.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
`Không có pipeline rõ ràng trong tài liệu nguồn`
Bài học giới thiệu luồng tư duy tối ưu hóa ngữ cảnh tác tử:
1. **Define Task**: Xác định rõ tác vụ đơn lẻ cần giao cho LLM.
2. **Assemble Instructions**: Viết system instructions rõ ràng, mạch lạc (không cần acromyms phức tạp).
3. **Equip Tools & Memory**: Cung cấp các công cụ cần thiết và kết nối bộ nhớ dài hạn (vector search).
4. **Format Context**: Định dạng toàn bộ dữ liệu đầu vào sao cho mô hình dễ tiếp thu nhất.
5. **Measure & Iterate**: Chạy thử nghiệm và đo lường kết quả để tinh chỉnh ngữ cảnh thay vì vội vã phức tạp hóa code.

## 7. Techniques - Kỹ thuật sử dụng
- **Dynamic Context Assembly (Lắp ráp ngữ cảnh động)**:
  - Purpose - mục đích: Đảm bảo mô hình nhận đủ thông tin cần thiết tại thời điểm gọi mà không bị loãng ngữ cảnh.
  - When to use - dùng khi nào: Trước mỗi lần gọi LLM trong hệ thống tác tử.
  - Trade-off - đánh đổi: Tăng chi phí xử lý và định dạng dữ liệu đầu vào.
  - Common mistake - lỗi dễ gặp: Nhồi nhét toàn bộ database vào context hoặc bỏ quên việc định dạng JSON rõ ràng.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Prompt Engineering (Kỹ nghệ gợi ý)**
  - Pros: Dễ thực hiện, chỉ cần chỉnh sửa văn bản hướng dẫn.
  - Cons: Giới hạn hiệu năng, mô hình không có dữ liệu thực tế hoặc công cụ để giải quyết bài toán động.
  - When to choose: Các tác vụ sinh văn bản đơn giản hoặc dịch thuật cơ bản.
- **Option 2: Context Engineering (Kỹ nghệ ngữ cảnh) (Khuyên dùng)**
  - Pros: Cho phép tác tử tương tác với thế giới thực thông qua RAG và tools, mang lại kết quả chính xác, cá nhân hóa.
  - Cons: Yêu cầu xây dựng hạ tầng phần mềm phức tạp hơn (database, vector index, API).
  - When to choose: Các hệ thống Agentic AI trong sản xuất thực tế phục vụ các bài toán kinh doanh cụ thể.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Over-engineering subagent architectures (Thiết kế quá phức tạp hệ thống tác tử phụ).
  - Root cause: Lập trình viên cố gắng chia nhỏ tác vụ thành quá nhiều subagents tự trị gọi nhau, dẫn đến tích lũy sai số và tăng độ trễ không cần thiết.
  - Symptom: Hệ thống phản hồi rất chậm, chi phí API cao, khó gỡ lỗi (debug).
  - Fix / prevention: Tuân thủ nguyên tắc "đơn giản là trên hết", không thiết kế các subagents phức tạp nếu một LLM call đơn lẻ với ngữ cảnh được tối ưu tốt có thể giải quyết được.

## 11. Knowledge Extension - Kiến thức mở rộng
- **Seminal blog post của Philip Schmidt (Google DeepMind)**: Bài viết "Rise of Subagents" (9/2026) chỉ ra rằng việc sử dụng subagents giúp các hệ thống tự trị (như Claude Code) hoạt động ổn định hơn bằng cách cô lập tác vụ. Tuy nhiên, ông cũng nhấn mạnh lời khuyên: "Đừng cố gắng over-engineer một giải pháp phức tạp hôm nay khi mà một mô hình mạnh hơn ngày mai có thể tự giải quyết một cách đơn giản hơn."

## 12. Study Pack - Gói ôn tập
### Must remember
1. Context engineering là xu hướng thay thế prompt engineering để xây dựng hệ thống tác tử sản xuất.
2. Ngữ cảnh tác tử gồm: instructions, tools, long-term memory (RAG), short-term memory và task.
3. Chất lượng ngữ cảnh quyết định sự khác biệt giữa ứng dụng demo và sản phẩm thực tế.
4. Tránh over-engineering kiến trúc đa tác tử khi chưa đo lường hiệu năng.
5. Simon Willison và Philip Schmidt là các nguồn tài nguyên uy tín để học về context engineering.

### Self-check questions
1. Context engineering khác Prompt engineering ở điểm cốt lõi nào?
2. Tại sao chất lượng ngữ cảnh lại quan trọng hơn framework lập trình tác tử?

### Flashcards
- Q: Kỹ nghệ ngữ cảnh (Context engineering) là gì?
  A: Thiết kế hệ thống động cung cấp đúng thông tin và công cụ cho LLM đúng thời điểm.
- Q: Philip Schmidt đưa ra lời khuyên gì về kiến trúc subagent?
  A: Tránh over-engineer hôm nay những gì mô hình mạnh hơn ngày mai có thể giải quyết đơn giản hơn.

### Interview Q&A
- Q: Khi xây dựng một tác tử AI, bạn sẽ ưu tiên việc viết prompt tối ưu hay xây dựng hệ thống quản lý ngữ cảnh động? Tại sao?
  A: Tôi sẽ ưu tiên xây dựng hệ thống quản lý ngữ cảnh động (context engineering). Mặc dù prompt rõ ràng là cần thiết, nhưng hiệu năng của tác tử trong môi trường thực tế phụ thuộc lớn vào việc truy xuất đúng dữ liệu RAG (long-term memory), gọi đúng công cụ (tools) và truyền đúng trạng thái hội thoại (short-term memory). Hệ thống ngữ cảnh động giúp mô hình có đủ thông tin chính xác tại thời điểm thực thi để đưa ra quyết định chính xác nhất.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 96. Day 2 - Setting Up AWS Bedrock Models and Enterprise APIs for AI Agents

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [96. Day 2 - Setting Up AWS Bedrock Models and Enterprise APIs for AI Agents.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/96.%20Day%202%20-%20Setting%20Up%20AWS%20Bedrock%20Models%20and%20Enterprise%20APIs%20for%20AI%20Agents.txt) - Đã dùng
- Slide: [Production W4D2.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D2.pdf) (Slide 4) - Đã dùng
- Code: [G:\AIProduction_t6_2026\production\week4\alex\.env.example](file:///G:/AIProduction_t6_2026/production/week4/alex/.env.example) - Đã dùng để đối chiếu cấu hình.

## 2. Executive Summary - Tóm tắt cốt lõi
- Giảng viên quyết định sử dụng dòng mô hình **Amazon Nova Pro** thay vì `gpt-oss-120b` (mô hình nguồn mở trên Bedrock) do Nova Pro hoạt động rất nhanh, giá thành cực kỳ rẻ và có hỗ trợ tool calling (gọi công cụ) tốt.
- Cảnh báo về giao diện thay đổi của trang quản lý Model Access trên AWS Bedrock Console.
- Khuyến nghị đăng ký truy cập mô hình tại vùng **US West (Oregon) us-west-2** để có danh sách mô hình đầy đủ nhất, đồng thời cũng đăng ký tại vùng chạy chính (ví dụ **us-east-1**) để tránh lỗi mâu thuẫn vùng cấu hình.
- Giới thiệu **Polygon.io** làm API cung cấp dữ liệu tài chính doanh nghiệp tiêu chuẩn thực tế. Cấu hình phân cấp qua biến `POLYGON_PLAN` với giá trị `free` (dữ liệu cuối ngày/caching) hoặc `paid` (dữ liệu thời gian thực).
- Giải thích lý do tránh dùng thư viện `yfinance`: yfinance dựa trên unofficial API (giao diện không chính thức) của Yahoo Finance, không cam kết chất lượng dịch vụ SLA (Service Level Agreement), không phù hợp cho sản phẩm SaaS chuyên nghiệp.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu lý do chọn Amazon Nova Pro cho các agents trong môi trường sản xuất (tốc độ, giá thành, hỗ trợ công cụ).
  - Nắm được cơ chế cách biệt vùng (region isolation) giữa vùng chạy mô hình Bedrock và vùng chạy hạ tầng Lambda.
  - Hiểu tầm quan trọng của việc lựa chọn API chính thức có SLA (như Polygon.io) thay vì các thư viện không chính thức (như yfinance).
- **Practical goals - mục tiêu thực hành**:
  - Yêu cầu quyền truy cập mô hình Bedrock Nova Pro trên AWS Console.
  - Đăng ký tài khoản và lấy API key trên Polygon.io.
  - Cập nhật đúng các tham số môi trường vào tệp `.env`.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao region của Bedrock (`BEDROCK_REGION`) và region hạ tầng (`DEFAULT_AWS_REGION`) có thể khác nhau và cách thức chúng tương tác qua môi trường.
  - Điểm hạn chế của thư viện `yfinance` khi triển khai hệ thống AI doanh nghiệp.

## 4. Previous Context - Liên hệ với bài trước
- Việc cấu hình Bedrock và Polygon.io này trực tiếp bổ sung các credentials (thông tin xác thực) vào tệp `.env` đã được khởi tạo từ Day 1. Những thông tin này giúp các agents Lambda (Planner, Tagger...) có thể kết nối với mô hình LLM và lấy dữ liệu giá cổ phiếu để phục vụ tính toán.

## 5. Core Theory - Lý thuyết cốt lõi
- **Model access (Quyền truy cập mô hình)**: Cơ chế cấp phép của AWS Bedrock yêu cầu người dùng phải tích vào điều khoản và yêu cầu quyền trước khi có thể gọi API của một mô hình cụ thể.
- **SLA (Service Level Agreement - Cam kết chất lượng dịch vụ)**: Văn bản cam kết từ nhà cung cấp dịch vụ về độ khả dụng, tốc độ phản hồi và độ ổn định của API.
- **Unofficial API (API không chính thức)**: Các cổng kết nối không được công bố hoặc hỗ trợ chính thức bởi dịch vụ gốc, thường bị chặn hoặc thay đổi cấu trúc bất ngờ mà không báo trước.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Quy trình cấu hình và chuẩn bị môi trường:
1. **Request Bedrock Access**: Vào AWS Bedrock Console tại vùng `us-west-2` (hoặc vùng của bạn) -> Model Access -> Yêu cầu quyền cho dòng Amazon Nova (đặc biệt là Nova Pro).
2. **Register Polygon.io**: Truy cập Polygon.io -> Đăng ký tài khoản free -> Lấy API Key.
3. **Configure Environment**: Mở file `.env` ở dự án gốc và điền các tham số:
   - `BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0` (hoặc model tương đương)
   - `BEDROCK_REGION=us-west-2`
   - `POLYGON_API_KEY=YOUR_KEY`
   - `POLYGON_PLAN=free`

## 7. Techniques - Kỹ thuật sử dụng
- **API Strategy Selection (Lựa chọn chiến lược API)**:
  - Purpose - mục đích: Đảm bảo tính ổn định và khả năng mở rộng của sản phẩm SaaS thương mại.
  - When to use - dùng khi nào: Khi bắt đầu thiết kế hệ thống cần tích hợp dữ liệu bên ngoài.
  - Trade-off - đánh đổi: Tốn chi phí vận hành nếu nâng cấp lên gói paid, nhưng đảm bảo độ tin cậy và có SLA.
  - Common mistake - lỗi dễ gặp: Dùng `yfinance` cho dự án sản xuất thực tế dẫn đến việc ứng dụng bị lỗi bất ngờ khi Yahoo thay đổi cấu trúc trang web.

## 8. Code Walkthrough - Phân tích code nếu có
`Code được cung cấp trong session nhưng chưa thấy code liên quan trực tiếp tới lesson này`

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Sử dụng yfinance (Free/Unofficial)**
  - Pros: Miễn phí hoàn toàn, không cần đăng ký API key, dễ sử dụng.
  - Cons: Không có SLA, dễ bị chặn IP (rate-limited) hoặc lỗi khi Yahoo thay đổi API không chính thức.
  - When to choose: Các dự án thử nghiệm cá nhân hoặc bài tập nhỏ.
- **Option 2: Sử dụng Polygon.io (Official/SLA) (Khuyên dùng)**
  - Pros: API chính thức, dữ liệu chuẩn Wall Street, có SLA cam kết, hỗ trợ phân tách gói cước free/paid trong mã nguồn.
  - Cons: Yêu cầu đăng ký tài khoản và có giới hạn rate limit ở gói cước free (5 cuộc gọi mỗi phút).
  - When to choose: Các sản phẩm SaaS tài chính chuyên nghiệp.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Bedrock AccessDeniedException / ModelNotAssociatedException.
  - Root cause: Gọi mô hình Bedrock ở một region (vùng) mà người dùng chưa thực hiện yêu cầu quyền truy cập (Model Access).
  - Symptom: Lambda báo lỗi access denied hoặc model not found khi chạy agent.
  - Fix / prevention: Đảm bảo đã request model access cho mô hình Nova Pro tại đúng region được cấu hình trong biến `BEDROCK_REGION` (ví dụ `us-west-2`). Khuyên dùng đăng ký quyền ở cả `us-west-2` và `us-east-1` để phòng ngừa.

## 11. Knowledge Extension - Kiến thức mở rộng
- **Sự khác biệt giữa các mô hình dòng Nova**: Amazon giới thiệu dòng Nova gồm: Nova Micro (tối ưu chi phí/tác vụ văn bản đơn giản), Nova Lite (tốc độ cao/đa phương tiện), Nova Pro (tác vụ phức tạp/hỗ trợ tool calling/suy luận chuyên sâu) và Nova Premier (mô hình lớn nhất cho tác vụ cực kỳ phức tạp). Trong dự án Alex, chúng ta bắt buộc sử dụng từ **Nova Pro** trở lên vì Nova Lite không hỗ trợ tool calling/MCP một cách ổn định.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Amazon Nova Pro là mô hình được chọn vì tốc độ, giá rẻ và hỗ trợ gọi công cụ.
2. Vùng Bedrock (`BEDROCK_REGION`) và vùng Lambda (`DEFAULT_AWS_REGION`) có thể khác nhau.
3. Polygon.io cung cấp API dữ liệu tài chính chính thức có SLA ổn định.
4. Tránh dùng `yfinance` cho các ứng dụng AI sản xuất thực tế vì tính thiếu ổn định.
5. Cấu hình biến `POLYGON_PLAN` thành `free` hoặc `paid` để điều khiển hành vi lấy dữ liệu.

### Self-check questions
1. Tại sao không nên sử dụng `yfinance` cho dự án Alex nếu mục tiêu là triển khai SaaS thực tế?
2. Làm thế nào để giải quyết lỗi khi gọi Bedrock báo mô hình không tồn tại hoặc bị từ chối truy cập?

### Flashcards
- Q: Biến môi trường nào quy định region để LiteLLM gọi Bedrock?
  A: `AWS_REGION_NAME` (được ánh xạ từ `BEDROCK_REGION` trong code).
- Q: Điểm khác biệt lớn nhất giữa yfinance và Polygon.io là gì?
  A: Polygon.io là API chính thức có cam kết chất lượng dịch vụ (SLA); yfinance sử dụng unofficial API không được Yahoo hỗ trợ.

### Interview Q&A
- Q: Khi triển khai hệ thống AI tích hợp dữ liệu tài chính, bạn sẽ xử lý như thế nào nếu gặp giới hạn rate limit ở gói cước API miễn phí của Polygon.io?
  A: (Recommended) Trong code, tôi sẽ thiết kế cơ chế caching (lưu trữ tạm thời) trong database. Đối với gói cước miễn phí (`POLYGON_PLAN=free`), hệ thống sẽ chỉ truy vấn giá đóng cửa cuối ngày (end-of-day) và cache lại trong bảng `instruments`. Các cuộc gọi tiếp theo từ tác tử sẽ đọc trực tiếp từ cache database thay vì gọi API liên tục, giúp tránh lỗi rate limit (5 calls/min). Chỉ khi người dùng nâng cấp lên gói trả phí (`paid`), hệ thống mới gọi trực tiếp API để lấy giá thời gian thực (intraday).

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 97. Day 2 - Exploring Multi-Agent Architecture - Tools and Structured Outputs

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [97. Day 2 - Exploring Multi-Agent Architecture - Tools and Structured Outputs.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/97.%20Day%202%20-%20Exploring%20Multi-Agent%20Architecture%20-%20Tools%20and%20Structured%20Outputs.txt) - Đã dùng
- Slide: [Production W4D2.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D2.pdf) (Slide 4) - Đã dùng
- Code: 
  - [backend/retirement/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/retirement/agent.py) - Đã dùng
  - [backend/retirement/lambda_handler.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/retirement/lambda_handler.py) - Đã dùng làm mẫu phân tích cấu trúc.
  - [backend/retirement/package_docker.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/retirement/package_docker.py) - Đã dùng làm mẫu script đóng gói.

## 2. Executive Summary - Tóm tắt cốt lõi
- Tất cả 5 agents mới (`planner`, `tagger`, `reporter`, `charter`, `retirement`) trong thư mục `backend/` đều có cấu trúc tệp chuẩn hóa và tương tự nhau.
- Cấu trúc chuẩn của một thư mục agent Lambda:
  - `lambda_handler.py`: Entrypoint (điểm khởi đầu) xử lý sự kiện khi Lambda được gọi.
  - `agent.py`: Nơi khởi tạo tác tử sử dụng OpenAI Agents SDK và định nghĩa logic chuẩn bị ngữ cảnh.
  - `templates.py`: Chứa prompt instructions (chỉ dẫn hệ thống) - phần cốt lõi của context engineering.
  - `package_docker.py`: Script Python dùng Docker để đóng gói toàn bộ code và thư viện phụ thuộc thành tệp `.zip` tương thích với môi trường Linux của AWS Lambda.
- Dự án sử dụng **OpenAI Agents SDK** tích hợp với Bedrock thông qua **LiteLLM** (hỗ trợ đầy đủ tool calling và structured outputs).
- Thay vì dùng các script shell/powershell riêng biệt cho từng hệ điều hành như ở tuần 2, tuần này toàn bộ quy trình đóng gói được viết bằng Python (`package_docker.py`) để chạy đa nền tảng dễ dàng.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Nắm vững cấu trúc thư mục tiêu chuẩn của các agents trong dự án Alex.
  - Hiểu cách thức hoạt động của `lambda_handler.py` như một cổng tiếp nhận yêu cầu trong môi trường serverless.
  - Hiểu tại sao cần sử dụng Docker để đóng gói thư viện phụ thuộc cho AWS Lambda.
- **Practical goals - mục tiêu thực hành**:
  - Khám phá và đọc hiểu cấu trúc mã nguồn của tác tử hưu trí (`retirement`).
- **What learner should be able to explain - người học cần giải thích được**:
  - Vai trò của từng tệp trong thư mục agent: `lambda_handler.py`, `agent.py`, `templates.py`, và `package_docker.py`.
  - Cơ chế hoạt động của `package_docker.py` sử dụng container để biên dịch dependencies (thư viện phụ thuộc).

## 4. Previous Context - Liên hệ với bài trước
- Cấu trúc đóng gói Lambda này phát triển từ kiến thức đóng gói cơ bản ở Week 2 Day 4, nhưng được cải tiến viết hoàn toàn bằng Python để hỗ trợ người dùng trên cả Windows, Mac và Linux mà không cần viết các kịch bản shell/powershell khác nhau.

## 5. Core Theory - Lý thuyết cốt lõi
- **Lambda Handler (Trình xử lý Lambda)**: Hàm entrypoint trong code Python nhận đối tượng `event` và `context` từ AWS Lambda runtime khi hàm được kích hoạt.
- **OpenAI Agents SDK**: Thư viện quản lý vòng lặp chạy tác tử, hỗ trợ cơ chế suy nghĩ/hành động (thought/action loop) và tích hợp các công cụ.
- **LiteLLM**: Thư viện cầu nối chuẩn hóa định dạng API của nhiều nhà cung cấp mô hình (như Bedrock, OpenAI, Anthropic) về một chuẩn duy nhất tương thích OpenAI.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Quy trình đóng gói và chuẩn bị Lambda Agent:
1. **Export Requirements**: Trích xuất các thư viện phụ thuộc từ `uv.lock` thành `requirements.txt` bằng công cụ `uv`.
2. **Docker Compile**: Khởi chạy một Docker container từ base image `public.ecr.aws/lambda/python:3.12` với kiến trúc target `--platform linux/amd64`.
3. **Install Dependencies**: Chạy lệnh `pip install` bên trong container để cài đặt các thư viện vào thư mục tạm `/package`, đảm bảo các thư viện nhị phân C-extensions được biên dịch tương thích với hệ điều hành Linux của AWS Lambda.
4. **Copy Application Code**: Copy các file code nghiệp vụ (`lambda_handler.py`, `agent.py`, `templates.py`, `observability.py`) vào thư mục `/package`.
5. **Compress Package**: Sử dụng module `zipfile` của Python để nén toàn bộ thư mục `/package` thành tệp zip (ví dụ `retirement_lambda.zip`).

## 7. Techniques - Kỹ thuật sử dụng
- **Cross-Platform Python Packaging (Đóng gói Python đa nền tảng)**:
  - Purpose - mục đích: Loại bỏ sự phụ thuộc vào các script shell/powershell hệ điều hành và công cụ `zip` dòng lệnh.
  - When to use - dùng khi nào: Khi viết script tự động hóa quy trình đóng gói phần mềm trong môi trường phát triển hỗn hợp (nhiều hệ điều hành).
  - Trade-off - đánh đổi: Phải viết thêm code Python xử lý nén file và copy thư mục, nhưng code này chạy được ở mọi nơi có Python.

## 8. Code Walkthrough - Phân tích code nếu có

### Phân tích [backend/retirement/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/retirement/agent.py#L236-L324)
Hàm `create_agent` chịu trách nhiệm thiết lập mô hình và đóng gói toàn bộ ngữ cảnh đầu vào:
```python
def create_agent(
    job_id: str, portfolio_data: Dict[str, Any], user_preferences: Dict[str, Any], db=None
):
    # Khởi tạo mô hình Bedrock thông qua LiteLLM
    model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
    bedrock_region = os.getenv("BEDROCK_REGION", "us-west-2")
    os.environ["AWS_REGION_NAME"] = bedrock_region # Thiết lập biến vùng cho LiteLLM

    model = LitellmModel(model=f"bedrock/{model_id}")

    # Thực hiện các tính toán tài chính và chạy giả lập Monte Carlo 500 kịch bản
    portfolio_value = calculate_portfolio_value(portfolio_data)
    allocation = calculate_asset_allocation(portfolio_data)
    monte_carlo = run_monte_carlo_simulation(
        portfolio_value, user_preferences.get("years_until_retirement", 30), ...
    )

    # Đóng gói ngữ cảnh cực kỳ chi tiết dạng Markdown đưa vào task prompt (Context Engineering)
    task = f"""
# Portfolio Analysis Context
- Portfolio Value: ${portfolio_value:,.0f}
- Asset Allocation: {allocation}
- Monte Carlo Success Rate: {monte_carlo["success_rate"]}%
...
Your task: Analyze this retirement readiness data...
"""
    tools = [] # Agent này đơn giản, không dùng tool gọi lại
    return model, tools, task
```

### Phân tích [backend/retirement/lambda_handler.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/retirement/lambda_handler.py#L62-L121)
Hàm xử lý chạy agent và ghi nhận kết quả bất đồng bộ:
```python
@retry(
    retry=retry_if_exception_type((RateLimitError, AgentTemporaryError, TimeoutError, asyncio.TimeoutError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
async def run_retirement_agent(job_id: str, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    user_preferences = get_user_preferences(job_id)
    db = Database()
    
    # Khởi tạo mô hình, công cụ và tác vụ từ agent.py
    model, tools, task = create_agent(job_id, portfolio_data, user_preferences, db)
    
    with trace("Retirement Agent"): # Ghi vết trace cho OpenAI Agents SDK
        agent = Agent(
            name="Retirement Specialist",
            instructions=RETIREMENT_INSTRUCTIONS,
            model=model,
            tools=tools
        )
        
        result = await Runner.run(agent, input=task, max_turns=20)
        
        # Ghi trực tiếp kết quả phân tích vào cột JSONB 'retirement_payload' của job tương ứng
        retirement_payload = {
            'analysis': result.final_output,
            'generated_at': datetime.utcnow().isoformat(),
            'agent': 'retirement'
        }
        success = db.jobs.update_retirement(job_id, retirement_payload)
        return {'success': success, 'final_output': result.final_output}
```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Sử dụng Bash / PowerShell Script để đóng gói**
  - Pros: Code script ngắn, gọi trực tiếp lệnh zip của hệ thống.
  - Cons: Không tương thích chéo; một script viết cho Mac/Linux không chạy được trên Windows nếu không cài WSL.
  - When to choose: Các nhà phát triển làm việc trên một hệ điều hành đồng nhất.
- **Option 2: Sử dụng Python Script kết hợp Docker (Khuyên dùng)**
  - Pros: Chạy độc lập với hệ điều hành của máy dev; Docker đảm bảo dependencies biên dịch đúng chuẩn Linux của Lambda.
  - Cons: Yêu cầu máy dev phải cài đặt và đang chạy Docker Desktop.
  - When to choose: Các dự án cộng tác nhóm nhiều hệ điều hành hoặc triển khai CI/CD.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Missing Docker daemon error.
  - Root cause: Chạy script `package_docker.py` nhưng Docker Desktop chưa được khởi động hoặc chưa bật tính năng chia sẻ thư mục.
  - Symptom: Script báo lỗi không thể kết nối tới docker daemon hoặc docker command not found.
  - Fix / prevention: Bắt buộc mở ứng dụng Docker Desktop trên máy tính trước khi thực hiện chạy script đóng gói.

## 11. Knowledge Extension - Kiến thức mở rộng
- **Tại sao phải dùng `--platform linux/amd64` trong Docker?**: Khi máy tính phát triển là Apple Silicon Mac (M1/M2/M3 sử dụng kiến trúc ARM64), nếu chạy lệnh pip install thông thường, Docker có thể tải các bản dựng nhị phân kiến trúc ARM64. Khi đưa lên AWS Lambda (mặc định cấu hình chạy x86_64), hàm sẽ crash ngay lập tức vì không tương thích tập lệnh CPU. Cờ `--platform linux/amd64` ép Docker phải giả lập môi trường x86_64 để tải và biên dịch đúng định dạng cho Lambda.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Cấu trúc agent Lambda gồm 4 file: `lambda_handler.py`, `agent.py`, `templates.py`, `package_docker.py`.
2. OpenAI Agents SDK kết nối Bedrock thông qua thư viện LiteLLM.
3. Đóng gói Lambda yêu cầu môi trường Docker để biên dịch các C-extensions tương thích Linux.
4. Python script đóng gói giúp hỗ trợ chéo nền tảng (cross-platform).
5. LiteLLM cần biến môi trường `AWS_REGION_NAME` để xác định vùng gọi Bedrock.

### Self-check questions
1. Tại sao hàm `lambda_handler.py` cần sử dụng `asyncio.run()` để kích hoạt chạy agent?
2. Tại sao việc đóng gói trực tiếp thư mục `site-packages` trên máy Windows để upload lên Lambda lại dễ gây ra lỗi?

### Flashcards
- Q: File nào đóng vai trò là entrypoint của AWS Lambda function?
  A: `lambda_handler.py` (chứa hàm `lambda_handler`).
- Q: Tại sao cần lọc bỏ thư viện `pyperclip` khi đóng gói cho Lambda?
  A: Vì Lambda là môi trường không có giao diện đồ họa (headless), thư viện clipboard hệ điều hành sẽ gây crash.

### Interview Q&A
- Q: Làm thế nào để đảm bảo một gói zip Lambda được build trên máy Windows có thể chạy ổn định trên môi trường AWS Lambda Linux mà không gặp lỗi biên dịch nhị phân?
  A: (Recommended) Chúng ta sử dụng một Docker container chạy chính thức ảnh AWS Lambda Python (ví dụ: `public.ecr.aws/lambda/python:3.12`) làm môi trường biên dịch trung gian. Bằng cách mount thư mục dự án vào container và chạy lệnh cài đặt dependencies ngay trong container, các thư viện nhị phân (C-extensions) sẽ được tải và biên dịch trực tiếp trên hệ điều hành Linux của container. File zip tạo ra từ thư mục này sẽ hoàn toàn tương thích với AWS Lambda.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 98. Day 2 - Building Multi-Agent Financial Systems - Code Review and Architecture

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [98. Day 2 - Building Multi-Agent Financial Systems - Code Review and Architecture.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/98.%20Day%202%20-%20Building%20Multi-Agent%20Financial%20Systems%20-%20Code%20Review%20and%20Architecture.txt) - Đã dùng
- Slide: [Production W4D2.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D2.pdf) (Slide 4) - Đã dùng
- Code: 
  - [backend/planner/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/planner/agent.py) - Đã dùng
  - [backend/planner/lambda_handler.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/planner/lambda_handler.py) - Đã dùng
  - [backend/tagger/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/tagger/agent.py) - Đã dùng
  - [backend/reporter/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/reporter/agent.py) - Đã dùng
  - [backend/charter/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/charter/agent.py) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Bài học đánh giá mã nguồn chi tiết của 5 agents và giải thích các quyết định thiết kế kiến trúc:
- **Charter & Retirement Agents**: Được tối giản tối đa, không dùng tools và structured outputs. Nhiệm vụ chỉ là nhận ngữ cảnh đầu vào được tính toán sẵn và sinh dữ liệu Markdown hoặc JSON tương ứng.
- **Tagger Agent**: Sử dụng **Structured Outputs** của OpenAI Agents SDK để ép đầu ra mô hình tuân thủ schema Pydantic phân loại quốc gia, ngành nghề, loại tài sản của cổ phiếu.
- **Reporter Agent**: Sử dụng duy nhất một **Tool** là `get_market_insights` để thực hiện tìm kiếm ngữ nghĩa (semantic search) trên kho dữ liệu S3 Vectors.
- **Planner Agent**: Đóng vai trò là đầu não tự trị (autonomous orchestrator). Nó được trang bị 3 function tools để kích hoạt song song 3 workers: `invoke_reporter`, `invoke_charter`, và `invoke_retirement`.
- Giới thiệu kỹ thuật sử dụng **RunContextWrapper** của OpenAI Agents SDK để truyền an toàn biến trạng thái `job_id` xuyên suốt các tool calls mà không bị rò rỉ hoặc dùng biến toàn cục (global variables).
- Phân biệt sự kết hợp tinh tế giữa **Agentic Workflow** (viết code cứng trong `lambda_handler` kiểm tra database và gọi trực tiếp `tagger` qua Lambda Invoke) và **Autonomous Agent** (để Planner tự quyết định thời điểm gọi các workers thông qua suy nghĩ).

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Phân tích sâu thiết kế công cụ (tools) và định dạng đầu ra (structured outputs) của từng tác tử trong hệ thống 5 agents.
  - Hiểu lý do tại sao LiteLLM kết hợp Bedrock không thể dùng đồng thời cả Tools và Structured Outputs trên cùng một Agent.
  - Nắm vững khái niệm truyền ngữ cảnh chạy (run context) qua `RunContextWrapper`.
  - Hiểu khi nào nên dùng code cứng (workflow) và khi nào nên để Agent tự trị (autonomous).
- **Practical goals - mục tiêu thực hành**:
  - Đánh giá cách tổ chức code chéo tiến trình (gọi chéo Lambda) trong Planner Agent.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao Planner Agent không được trang bị tool để gọi Tagger, mà Tagger lại được gọi qua code cứng Python ở đầu Planner Lambda.
  - Tác dụng của `RunContextWrapper` trong việc bảo mật và quản lý trạng thái của các tool calls.

## 4. Previous Context - Liên hệ với bài trước
- Kiến trúc này hiện thực hóa sơ đồ lý thuyết ở Day 1. Mỗi worker agent giờ đây hoạt động độc lập và chỉ tương tác với database thông qua `job_id` được Planner truyền qua SQS và các tool calls.

## 5. Core Theory - Lý thuyết cốt lõi
- **Structured Outputs (Đầu ra cấu trúc)**: Tính năng ép buộc LLM sinh ra dữ liệu JSON tuân thủ chính xác một schema được định nghĩa sẵn (ví dụ Pydantic class).
- **RunContextWrapper (Bộ bọc ngữ cảnh chạy)**: Một cơ chế trong OpenAI Agents SDK cho phép truyền các dữ liệu ngữ cảnh tùy chỉnh (như `job_id`, `user_id`) vào các hàm được định nghĩa làm công cụ cho tác tử.
- **Agentic Workflow (Quy trình tác tử lập trình)**: Luồng điều phối các LLM calls bằng mã nguồn lập trình thông thường (if/else, loops) có tính xác định cao.
- **Autonomous Agent (Tác tử tự trị)**: Mô hình điều phối dựa vào khả năng lập kế hoạch của LLM, tự quyết định gọi công cụ nào và gọi khi nào.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng xử lý chi tiết của Planner Lambda:
1. **Trigger**: Planner Lambda nhận event chứa `job_id` từ SQS.
2. **Handle Missing Instruments (Agentic Workflow)**:
   - Quét database xem các cổ phiếu trong portfolio của user có cổ phiếu nào chưa được tag ngành/quốc gia.
   - Nếu có, gọi trực tiếp Lambda `alex-tagger` qua Lambda Client. Tagger sử dụng Structured Outputs để phân loại và lưu kết quả vào database.
3. **Update Prices**: Gọi module cập nhật giá thị trường thời gian thực hoặc giá cache từ Polygon.io.
4. **Load Summary**: Đọc nhanh thông tin tổng quát của portfolio (không đọc toàn bộ data để tránh phình context).
5. **Orchestrate Workers (Autonomous Agent)**:
   - Khởi tạo Planner Agent với 3 tools: `invoke_reporter`, `invoke_charter`, `invoke_retirement`.
   - Planner Agent tự phân tích và kích hoạt song song các tool gọi Lambda của các worker agents.
   - Mỗi worker agent khi chạy xong sẽ cập nhật kết quả trực tiếp vào đúng cột JSONB tương ứng trong bảng `jobs` ở database.
6. **Complete**: Đánh dấu job hoàn thành trong database.

## 7. Techniques - Kỹ thuật sử dụng
- **Hybrid Coordination Pattern (Mô hình điều phối hỗn hợp)**:
  - Purpose - mục đích: Tận dụng tính chính xác của code lập trình thông thường cho các tác vụ cần tính ổn định (như tagging dữ liệu thiếu) và tính linh hoạt của LLM cho các tác vụ sáng tạo/phân tích (lập báo cáo, vẽ biểu đồ).
  - When to use - dùng khi nào: Khi xây dựng các hệ thống Agentic AI lớn trong doanh nghiệp.
  - Trade-off - đánh đổi: Code phức tạp hơn do phải chia tách luồng xử lý và quản lý trạng thái database chặt chẽ.

## 8. Code Walkthrough - Phân tích code nếu có

### Phân tích [backend/planner/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/planner/agent.py#L29-L71)
Cấu trúc wrapper ngữ cảnh và hàm gọi Lambda chéo:
```python
@dataclass
class PlannerContext:
    job_id: str  # Chứa job_id để các công cụ biết mình đang xử lý job nào

async def invoke_lambda_agent(
    agent_name: str, function_name: str, payload: Dict[str, Any]
) -> Dict[str, Any]:
    # Sử dụng boto3 client để gọi trực tiếp một Lambda function khác chéo mạng
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",  # Chờ kết quả phản hồi (Synchronous)
        Payload=json.dumps(payload),
    )
    result = json.loads(response["Payload"].read())
    return result
```

### Định nghĩa công cụ bằng RunContextWrapper trong [backend/planner/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/planner/agent.py#L243-L285)
```python
@function_tool
async def invoke_reporter(wrapper: RunContextWrapper[PlannerContext]) -> str:
    """Invoke the Report Writer agent to generate portfolio analysis narrative."""
    # Lấy job_id an sau từ context bọc trong wrapper
    return await invoke_reporter_internal(wrapper.context.job_id)

def create_agent(job_id: str, portfolio_summary: Dict[str, Any], db):
    context = PlannerContext(job_id=job_id)
    model = LitellmModel(model=f"bedrock/{model_id}")
    
    # Đăng ký các công cụ gọi Lambda cho Planner
    tools = [invoke_reporter, invoke_charter, invoke_retirement]
    
    task = f"Job {job_id} has {portfolio_summary['num_positions']} positions. Call appropriate agents."
    return model, tools, task, context
```

### Phân tích [backend/tagger/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/tagger/agent.py) (Structured Outputs)
Tagger ép kiểu đầu ra khớp định dạng JSON bằng Pydantic class:
```python
class InstrumentClassification(BaseModel):
    symbol: str
    asset_class: Literal["equity", "fixed_income", "commodities", "real_estate", "cash"]
    region: Literal["North America", "Europe", "Asia-Pacific", "Emerging Markets", "Other"]
    sector: Literal["technology", "financials", "healthcare", "energy", "industrials", "consumer", "other"]

def create_agent(instruments_to_tag):
    # Trả về output_type để ép model tuân thủ schema nhãn tài sản
    return model, [], task, InstrumentClassification
```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Để Planner Agent tự trị quyết định khi nào cần tag cổ phiếu**
  - Pros: Tác tử tự nhiên hơn, giảm bớt logic code trong lambda handler.
  - Cons: Planner có thể bỏ quên hoặc gọi sai công cụ tagger, làm tăng thời gian suy nghĩ của mô hình và tăng chi phí token.
  - When to choose: Các tác vụ mang tính khám phá cao.
- **Option 2: Gọi Tagger bằng code cứng trước khi chạy Planner Agent (Khuyên dùng)**
  - Pros: Đảm bảo 100% các cổ phiếu chưa tag đều được chuẩn hóa dữ liệu trước khi các worker agents phân tích, giảm tải suy nghĩ cho Planner.
  - Cons: Mất tính tự trị hoàn toàn của Planner đối với tác vụ tag.
  - When to choose: Các ứng dụng tài chính yêu cầu dữ liệu đầu vào phải sạch và nhất quán tuyệt đối.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Claude Code over-engineering (Tự động thêm công cụ không cần thiết).
  - Root cause: Khi sử dụng các công cụ sinh code như Claude Code, nó thường tự ý tạo ra các công cụ phức tạp (ví dụ: tạo tool để gọi thuật toán Monte Carlo cho Retirement Agent) thay vì chèn trực tiếp kết quả tính toán vào task context.
  - Symptom: Code phình to, độ trễ tăng do LLM phải gọi đi gọi lại công cụ thừa thãi.
  - Fix / prevention: Luôn kiểm tra và tinh giản code do LLM sinh ra. Nếu dữ liệu luôn được sử dụng trong task phân tích, hãy tính toán trước bằng Python và đưa thẳng vào task context dưới dạng Markdown (Context Engineering).

## 11. Knowledge Extension - Kiến thức mở rộng
- **Thiết kế cơ sở dữ liệu phi tập trung cho Đa tác tử (Decoupled Database Design)**: Thay vì thiết kế một bảng dữ liệu lớn dùng chung và các tác tử phải cập nhật đè lên nhau, dự án Alex thiết kế bảng `jobs` với các trường JSONB riêng biệt cho từng agent: `report_payload`, `charts_payload`, `retirement_payload`. Khi một agent chạy xong, nó chỉ cập nhật đúng cột của mình dựa vào `job_id`. Điều này loại bỏ hoàn toàn hiện tượng race conditions (xung đột ghi dữ liệu đồng thời) khi các Lambda chạy song song.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Charter và Retirement là các agents đơn giản, không dùng tools/structured outputs.
2. Tagger sử dụng Structured Outputs để phân loại dữ liệu chính xác theo schema Pydantic.
3. Reporter sử dụng Tool `get_market_insights` để truy cập tri thức RAG trên S3 Vectors.
4. Planner là Orchestrator tự trị gọi các worker qua Lambda Invoke.
5. Sử dụng `RunContextWrapper` để truyền `job_id` an toàn vào các tool calls.

### Self-check questions
1. Tại sao LiteLLM kết hợp Bedrock lại hạn chế việc một tác tử sử dụng đồng thời cả Tools và Structured Outputs?
2. Sự khác biệt giữa cách Tagger được gọi và cách Reporter được gọi từ Planner là gì?

### Flashcards
- Q: Cơ chế nào giúp Planner truyền job_id vào các công cụ trong OpenAI Agents SDK?
  A: `RunContextWrapper[PlannerContext]`.
- Q: Tại sao Charter Agent lại được thiết kế cực kỳ đơn giản không dùng tool?
  A: Vì nhiệm vụ của nó chỉ là chuyển đổi dữ liệu context có sẵn thành JSON biểu đồ, không cần tương tác bên ngoài.

### Interview Q&A
- Q: Tại sao trong hệ thống đa tác tử Alex, chúng ta lại cho các worker agents ghi trực tiếp kết quả vào database thay vì để chúng trả kết quả về cho Planner xử lý và ghi một thể?
  A: (Recommended) Thiết kế này giúp tối ưu hóa thời gian chạy và khả năng chịu lỗi của hệ thống. Nếu Planner phải đợi tất cả các worker trả kết quả về rồi mới xử lý, Planner Lambda sẽ bị treo và tốn chi phí chờ đợi (idle cost), đồng thời tăng rủi ro bị timeout (giới hạn 15 phút của Lambda). Bằng cách cho các worker tự ghi kết quả vào database, Planner chỉ đóng vai trò kích hoạt bất đồng bộ. Nếu một worker thất bại, các worker khác vẫn hoàn thành và lưu được dữ liệu, giúp hệ thống có khả năng graceful degradation (suy giảm chức năng nhẹ nhàng) thay vì sụp đổ hoàn toàn.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 99. Day 2 - Testing Multi-Agent Systems Locally Before Lambda Deployment

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [99. Day 2 - Testing Multi-Agent Systems Locally Before Lambda Deployment.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/99.%20Day%202%20-%20Testing%20Multi-Agent%20Systems%20Locally%20Before%20Lambda%20Deployment.txt) - Đã dùng
- Slide: [Production W4D2.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D2.pdf) (Slide 4) - Đã dùng
- Code: 
  - [backend/planner/lambda_handler.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/planner/lambda_handler.py#L35-L85) - Đã dùng (Đoạn mã retry)
  - [backend/test_simple.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/test_simple.py) - Đã dùng để kiểm tra cấu trúc test hệ thống.

## 2. Executive Summary - Tóm tắt cốt lõi
- Nhấn mạnh tầm quan trọng của việc kiểm thử cục bộ (local testing) toàn bộ 5 agents trước khi deploy lên đám mây AWS.
- Giới thiệu thư viện **tenacity** làm công cụ xây dựng retry logic (logic thử lại) mạnh mẽ cho các cuộc gọi API LLM Bedrock để đối phó với lỗi **Rate Limit (giới hạn tần suất)**.
- Phân tích cơ chế chạy chéo tiến trình của Planner: Khi Planner gọi các worker agents (Reporter, Charter, Retirement), nó thực hiện các cuộc gọi Lambda thông qua API AWS thay vì gọi các module Python cục bộ. Điều này giúp hệ thống phân tán hoàn toàn tải xử lý chéo mạng (cross-process boundaries).
- Cung cấp tệp `test_simple.py` ở thư mục cha `backend/` giúp tự động chạy kiểm thử tuần tự local cho cả 5 agents cùng một lúc để xác minh tính ổn định của prompt và kết nối Bedrock.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu cách thức hoạt động của cơ chế retry tự động sử dụng exponential backoff (giảm giật số mũ).
  - Nắm vững thiết kế giao tiếp chéo tiến trình (cross-process communication) của các agents thông qua Lambda Invoke.
  - Hiểu lợi ích của việc kiểm thử cục bộ (local test harness) đối với hệ thống đa tác tử.
- **Practical goals - mục tiêu thực hành**:
  - Chạy thử nghiệm local từng agent bằng `test_simple.py` trong từng thư mục.
  - Chạy thử nghiệm tổng thể hệ thống bằng `test_simple.py` ở thư mục `backend/`.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao việc gọi chéo Lambda từ Planner lại ưu việt hơn việc import code chạy trực tiếp trong cùng một tiến trình Python khi scale hệ thống.
  - Cách thiết lập decorator `@retry` của thư viện `tenacity`.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này thực hiện kiểm thử cho toàn bộ code nghiệp vụ của 5 agents đã được phân tích ở bài 98. Nó sử dụng cấu hình `.env` của bài 96 để kết nối trực tiếp tới Bedrock Nova Pro trong quá trình test local.

## 5. Core Theory - Lý thuyết cốt lõi
- **Exponential backoff (Giảm giật số mũ)**: Thuật toán tăng thời gian chờ giữa các lần thử lại theo cấp số nhân để tránh làm quá tải hệ thống đích (ví dụ: chờ 4s, 8s, 16s, 32s...).
- **Cross-process boundaries (Ranh giới liên tiến trình)**: Việc truyền nhận dữ liệu và kích hoạt thực thi giữa các tiến trình hệ điều hành độc lập hoặc các server độc lập qua mạng (ở đây là Lambda client invoke).
- **Rate limiting (Giới hạn tần suất)**: Cơ chế kiểm soát lưu lượng của nhà cung cấp API (Bedrock) nhằm giới hạn số lượng request tối đa trên một phút (RPM) hoặc số token trên một phút (TPM).

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng kiểm thử cục bộ hệ thống (Local Test Pipeline):
1. **Prepare Database**: Reset database local hoặc dùng database cloud để có dữ liệu mẫu.
2. **Execute Agent Test**: Chạy `uv run test_simple.py` trong từng thư mục con. Thiết lập biến `MOCK_LAMBDAS=true` để Planner không gọi Lambda thực tế mà chỉ in log mô phỏng.
3. **Execute System Test**: Di chuyển ra thư mục cha `backend/` và chạy `uv run test_simple.py` để tự động kích hoạt kiểm thử tuần tự cả 5 agents.
4. **Output Verification**: Kiểm tra kết quả in ra màn hình (JSON biểu đồ, Markdown báo cáo, text hưu trí) để đảm bảo không có lỗi cú pháp hoặc lỗi kết nối Bedrock.

## 7. Techniques - Kỹ thuật sử dụng
- **Resilient API Retries (Thử lại API đàn hồi)**:
  - Purpose - mục đích: Đảm bảo hệ thống không bị crash đột ngột khi Bedrock bị quá tải hoặc đạt giới hạn rate limit tạm thời.
  - When to use - dùng khi nào: Tại các hàm gọi API bên thứ ba có nguy cơ nghẽn tải.
  - Trade-off - đánh đổi: Tăng thời gian phản hồi của request nếu phải thử lại nhiều lần.
  - Common mistake - lỗi dễ gặp: Thử lại vô hạn lần hoặc thử lại với tất cả các loại lỗi (bao gồm cả lỗi code sai cú pháp).

## 8. Code Walkthrough - Phân tích code nếu có

### Phân tích retry logic trong [backend/planner/lambda_handler.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/planner/lambda_handler.py#L35-L42)
Sử dụng `tenacity` để tự động gọi lại hàm khi gặp lỗi `RateLimitError` từ Bedrock:
```python
@retry(
    # Chỉ thực hiện retry nếu bắt được lỗi RateLimitError từ LiteLLM
    retry=retry_if_exception_type(RateLimitError),
    stop=stop_after_attempt(5),  # Dừng lại sau tối đa 5 lần thử thất bại
    wait=wait_exponential(multiplier=1, min=4, max=60),  # Exponential backoff từ 4s đến tối đa 60s
    before_sleep=lambda retry_state: logger.info(
        f"Planner: Rate limit hit, retrying in {retry_state.next_action.sleep} seconds..."
    )
)
async def run_orchestrator(job_id: str) -> None:
    # Logic chạy Planner Agent nằm ở đây...
    pass
```

### Phân tích cơ chế gọi chéo Lambda trong [backend/planner/agent.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/planner/agent.py#L35-L71)
```python
async def invoke_lambda_agent(
    agent_name: str, function_name: str, payload: Dict[str, Any]
) -> Dict[str, Any]:
    # Nếu đang chạy test local với cờ MOCK_LAMBDAS=True
    if MOCK_LAMBDAS:
        logger.info(f"[MOCK] Would invoke {agent_name} with payload: {json.dumps(payload)[:200]}")
        return {"success": True, "message": f"[Mock] {agent_name} completed", "mock": True}

    # Nếu chạy thực tế trên Cloud, gọi Lambda thực qua AWS SDK Boto3
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    # Đọc Payload trả về từ Lambda worker
    result = json.loads(response["Payload"].read())
    return result
```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Chạy toàn bộ agents trong cùng một tiến trình Python (Monolithic)**
  - Pros: Rất dễ lập trình, tốc độ gọi hàm cực nhanh vì không có độ trễ mạng.
  - Cons: Không thể tận dụng thế mạnh co giãn độc lập của Serverless Lambda; nếu một agent bị treo/rò rỉ bộ nhớ sẽ làm sập toàn bộ hệ thống; dễ vượt quá giới hạn timeout 15 phút.
  - When to choose: Các ứng dụng chạy local hoặc ứng dụng demo quy mô nhỏ.
- **Option 2: Gọi chéo Lambda qua mạng (Distributed Serverless) (Khuyên dùng)**
  - Pros: (Recommended) Tách biệt hoàn toàn ranh giới tiến trình, từng agent tự co giãn độc lập, dễ quan sát log CloudWatch riêng biệt, tận dụng tối đa tính chạy song song của Lambda.
  - Cons: Phức tạp trong việc thiết lập cấu hình IAM và mạng, phát sinh độ trễ mạng (network latency) giữa các Lambda calls.
  - When to choose: Các hệ thống SaaS doanh nghiệp thực tế.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Bedrock Throttling Exception in Parallel Execution.
  - Root cause: Planner kích hoạt song song 3 Lambda workers (Reporter, Charter, Retirement), cả 3 worker này cùng lúc gửi request gọi Bedrock, vượt quá giới hạn concurrent requests mặc định của tài khoản AWS đối với mô hình Nova Pro.
  - Symptom: Một hoặc nhiều Lambda worker bị lỗi `ThrottlingException` và ghi trạng thái thất bại vào database.
  - Fix / prevention: Thiết lập cấu hình retry có giảm giật số mũ (exponential backoff) sử dụng `tenacity` trên toàn bộ các agents để chúng tự giãn cách thời gian gọi Bedrock khi bị nghẽn.

## 11. Knowledge Extension - Kiến thức mở rộng
- **Thư viện backoff so với tenacity**: Trong cộng đồng Python, ngoài `tenacity` còn có thư viện `backoff` rất nổi tiếng. `backoff` sử dụng decorators dựa trên generator và có cú pháp nhẹ hơn, tuy nhiên `tenacity` (kế thừa từ thư viện `retrying` cũ) lại cung cấp khả năng tùy biến điều kiện dừng, điều kiện đợi và log trước/sau khi sleep cực kỳ mạnh mẽ, rất phù hợp cho các cuộc gọi API phức tạp của AI Agents.

## 12. Study Pack - Gói ôn tập
### Must remember
1. Kiểm thử cục bộ (local testing) là bước bắt buộc trước khi triển khai Cloud để tiết kiệm chi phí và thời gian.
2. Thư viện `tenacity` giúp cài đặt logic tự động thử lại (retry) khi gặp lỗi rate limit.
3. Thiết kế Planner gọi Lambda chéo giúp hệ thống phân tán và tận dụng tính song song của AWS Lambda.
4. Cờ `MOCK_LAMBDAS=True` được dùng để chạy test Planner local mà không kích hoạt gọi Lambda thực tế.
5. Tệp `backend/test_simple.py` chạy kiểm thử tuần tự cả 5 agents và báo cáo số lượng pass/fail.

### Self-check questions
1. Tại sao thuật toán Exponential Backoff lại quan trọng khi xử lý lỗi Rate Limit của Bedrock?
2. Sự khác nhau giữa tệp `test_simple.py` trong thư mục `backend/planner/` và tệp `test_simple.py` trong thư mục `backend/` là gì?

### Flashcards
- Q: Thư viện Python nào được dùng trong dự án Alex để xử lý retry tự động?
  A: `tenacity`.
- Q: Loại InvocationType nào được dùng trong boto3 lambda invoke để gọi đồng bộ (chờ kết quả trả về)?
  A: `"RequestResponse"`.

### Interview Q&A
- Q: Hãy giải thích cách bạn xử lý khi Planner Agent chạy trên Lambda vượt quá giới hạn thời gian chờ (timeout) do các worker agents phản hồi quá chậm?
  A: (Recommended) Để giải quyết vấn đề này, tôi thực hiện hai giải pháp đồng thời: Thứ nhất, tách rời ranh giới tiến trình bằng cách để Planner gọi các worker Lambda chạy bất đồng bộ hoặc chạy song song thực sự (sử dụng `asyncio.gather` trong Python). Thứ hai, cấu hình thời gian chờ hiển thị (visibility timeout) của hàng đợi SQS ở mức `910` giây (15 phút 10 giây), lớn hơn một chút so với giới hạn timeout tối đa của Planner Lambda (`900` giây) để đảm bảo SQS không gửi lại tin nhắn trùng lặp khi Planner vẫn đang tích cực điều phối.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 100. Day 2 - Packaging and Deploying Multi-Agent AI Systems to AWS Lambda

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [100. Day 2 - Packaging and Deploying Multi-Agent AI Systems to AWS Lambda.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/100.%20Day%202%20-%20Packaging%20and%20Deploying%20Multi-Agent%20AI%20Systems%20to%20AWS%20Lambda.txt) - Đã dùng
- Slide: [Production W4D2.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D2.pdf) (Slide 4) - Đã dùng
- Code: 
  - [backend/package_docker.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/package_docker.py) - Đã dùng
  - [terraform/6_agents/main.tf](file:///G:/AIProduction_t6_2026/production/week4/alex/terraform/6_agents/main.tf) - Đã dùng
  - [terraform/6_agents/variables.tf](file:///G:/AIProduction_t6_2026/production/week4/alex/terraform/6_agents/variables.tf) - Đã dùng làm ngữ cảnh.

## 2. Executive Summary - Tóm tắt cốt lõi
- Bài học hướng dẫn quy trình đóng gói hàng loạt (batch packaging) và triển khai hạ tầng Terraform cho cả 5 agents lên AWS.
- Chạy script [backend/package_docker.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/package_docker.py) để tự động gọi script đóng gói của từng agent con bằng Docker. Kết quả tạo ra các file `.zip` sạch tương thích với Linux.
- Cấu hình tệp `terraform.tfvars` trong thư mục [terraform/6_agents](file:///G:/AIProduction_t6_2026/production/week4/alex/terraform/6_agents) bao gồm region, bucket tên, endpoint tên và Polygon API key.
- Hạ tầng Terraform triển khai bao gồm:
  - **AWS SQS Queue**: Hàng đợi `alex-analysis-jobs` dùng để truyền job bất đồng bộ. Có Dead Letter Queue (DLQ) để xử lý tin nhắn lỗi.
  - **IAM Role & Policies**: Cấp quyền tối thiểu cho Lambda truy cập S3 Vectors, Bedrock, Aurora Data API, SQS và SageMaker.
  - **S3 Bucket for Lambda Packages**: AWS Lambda giới hạn upload trực tiếp code có dung lượng >50MB. Terraform tạo một bucket S3 trung gian để upload file zip lên đó trước, sau đó Lambda sẽ liên kết trỏ tới S3 object này.
  - **5 AWS Lambda functions**: Khởi tạo và cấu hình biến môi trường cho cả 5 agents.
  - **SQS Lambda Event Source Mapping**: Liên kết để SQS tự động trigger (kích hoạt) Planner Lambda khi có message.
- Sử dụng script `deploy_all_lambdas.py` trong `backend/` để cập nhật nhanh mã nguồn Lambda sau khi hạ tầng đã được apply thành công.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu giới hạn kích thước gói zip của AWS Lambda và cơ chế bắt cầu qua S3 bucket.
  - Nắm được cấu trúc tệp Terraform điều phối hạ tầng đa tác tử (Lambda, SQS, IAM).
  - Hiểu cách thức thiết lập SQS Event Source Mapping để tự động kích hoạt Lambda.
  - Nắm vững vai trò của Dead Letter Queue (DLQ) trong thiết kế hệ thống chịu lỗi.
- **Practical goals - mục tiêu thực hành**:
  - Đóng gói hàng loạt 5 agents bằng Docker.
  - Triển khai hạ tầng Terraform cho agents tại thư mục `terraform/6_agents/`.
  - Cập nhật code Lambda bằng `deploy_all_lambdas.py`.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao cần thiết lập `visibility_timeout` của SQS tương thích với timeout của Lambda xử lý.
  - Cơ chế hoạt động của IAM policy cấp quyền cho Planner gọi các agents khác.

## 4. Previous Context - Liên hệ với bài trước
- Tệp Terraform này liên kết trực tiếp với Aurora Serverless v2 database (triển khai ở Day 1) bằng cách nhận cluster ARN và secret ARN làm biến môi trường, đồng thời liên kết với S3 Vectors bucket đã tạo từ Week 3 Day 4.

## 5. Core Theory - Lý thuyết cốt lõi
- **Local Backend (Kho lưu trữ trạng thái cục bộ)**: Cơ chế lưu trữ file trạng thái `terraform.tfstate` của Terraform ngay tại thư mục hiện hành (được gitignore để đảm bảo an toàn).
- **Visibility timeout (Thời gian chờ hiển thị)**: Khoảng thời gian SQS khóa tin nhắn không cho các consumer khác nhìn thấy sau khi một consumer đã nhận nó, tránh xử lý trùng lặp.
- **Dead Letter Queue (DLQ - Hàng đợi thư chết)**: Hàng đợi phụ chứa các tin nhắn bị lỗi nhiều lần (vượt quá `maxReceiveCount`) để quản trị viên kiểm tra sau.
- **Event Source Mapping (Ánh xạ nguồn sự kiện)**: Tài nguyên AWS liên kết trực tiếp một nguồn sự kiện (như SQS) với một Lambda function để AWS tự động poll và kích hoạt Lambda.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng đóng gói và triển khai Cloud (Deployment Pipeline):
1. **Batch Package**: Chạy `uv run package_docker.py` trong thư mục `backend/` để tạo các file zip cho 5 agents.
2. **Setup TFVars**: Copy `terraform.tfvars.example` sang `terraform.tfvars` trong `terraform/6_agents/` và điền cấu hình.
3. **Terraform Apply**:
   - Chạy `terraform init` để tải AWS provider.
   - Chạy `terraform apply` để tạo SQS, S3 bucket, IAM role và upload các zip packages từ local lên S3.
   - Terraform tạo ra 5 Lambda functions liên kết với các S3 objects tương ứng.
4. **Lambda Event Binding**: Terraform liên kết SQS `alex-analysis-jobs` với Lambda `alex-planner` qua event source mapping.
5. **Quick Deploy Code (Optional)**: Chạy `uv run deploy_all_lambdas.py` trong `backend/` bất cứ khi nào thay đổi code Python để cập nhật trực tiếp lên Lambda mà không cần chạy lại Terraform.

## 7. Techniques - Kỹ thuật sử dụng
- **S3-Bridged Lambda Deployment (Triển khai Lambda bắt cầu qua S3)**:
  - Purpose - mục đích: Vượt qua giới hạn kích thước upload trực tiếp 50MB của AWS Lambda API.
  - When to use - dùng khi nào: Khi các package Lambda chứa nhiều thư viện nặng (như Pydantic, LiteLLM, Boto3, v.v.) khiến dung lượng nén vượt quá 50MB.
  - Trade-off - đánh đổi: Tốn thêm dung lượng lưu trữ trên S3 bucket, nhưng đảm bảo deploy thành công các gói code lên tới 250MB (khi giải nén).

## 8. Code Walkthrough - Phân tích code nếu có

### Phân tích [terraform/6_agents/main.tf](file:///G:/AIProduction_t6_2026/production/week4/alex/terraform/6_agents/main.tf)
#### Cấu hình SQS Queue và Visibility Timeout:
```hcl
resource "aws_sqs_queue" "analysis_jobs" {
  name                       = "alex-analysis-jobs"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 86400  # Lưu trữ tin nhắn trong 1 ngày
  receive_wait_time_seconds = 10     # Kích hoạt Long Polling để giảm request thừa
  visibility_timeout_seconds = 910   # 15 phút + 10 giây buffer (khớp với timeout tối đa của Planner Lambda)
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.analysis_jobs_dlq.arn
    maxReceiveCount     = 3          # Thử lại tối đa 3 lần trước khi đưa vào DLQ
  })
}

resource "aws_sqs_queue" "analysis_jobs_dlq" {
  name = "alex-analysis-jobs-dlq"
}
```

#### Ánh xạ quyền IAM chéo và gọi chéo Lambda:
```hcl
resource "aws_iam_role_policy" "lambda_agents_policy" {
  name = "alex-lambda-agents-policy"
  role = aws_iam_role.lambda_agents_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Cho phép Planner Lambda có quyền kích hoạt (invoke) các Lambda function khác có tiền tố alex-
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:alex-*"
      },
      # Quyền đọc tin nhắn từ SQS
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.analysis_jobs.arn
      },
      # Quyền gọi Bedrock LLM chéo vùng
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/*",
          "arn:aws:bedrock:*:*:inference-profile/*"
        ]
      }
    ]
  })
}
```

#### Ánh xạ Trigger SQS sang Lambda:
```hcl
resource "aws_lambda_event_source_mapping" "planner_sqs" {
  event_source_arn = aws_sqs_queue.analysis_jobs.arn
  function_name    = aws_lambda_function.planner.arn
  batch_size       = 1  # Mỗi lần trigger chỉ xử lý 1 tin nhắn (1 job phân tích)
}
```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Đóng gói và upload trực tiếp code Lambda qua Terraform local**
  - Pros: Không cần tạo thêm S3 bucket để chứa code, file cấu hình ngắn hơn.
  - Cons: Chỉ hoạt động nếu gói zip dưới 50MB; nếu cài thêm thư viện sẽ bị lỗi quá giới hạn kích thước upload trực tiếp của AWS API.
  - When to choose: Các hàm Lambda siêu nhỏ, không có dependencies phức tạp.
- **Option 2: Đóng gói đẩy lên S3 trung gian rồi mới cập nhật Lambda (Khuyên dùng)**
  - Pros: Hỗ trợ kích thước gói code lên tới 250MB, ổn định cho dự án thực tế có nhiều thư viện nặng.
  - Cons: Yêu cầu quản lý thêm S3 bucket và phát sinh phí lưu trữ nhỏ trên S3.
  - When to choose: Các dự án AI Agents phức tạp sử dụng nhiều thư viện bên thứ ba.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: SQS message processing loop (Tin nhắn xử lý lặp lại vô hạn).
  - Root cause: Thiết lập tham số `visibility_timeout_seconds` của SQS nhỏ hơn thời gian thực thi thực tế của Planner Lambda (ví dụ: SQS timeout là 30s nhưng Lambda chạy mất 1.5 phút). SQS tưởng Lambda đã chết nên tự động mở khóa tin nhắn và gửi lại cho Lambda khác, dẫn đến xử lý trùng lặp và làm nghẽn hệ thống.
  - Symptom: Một job phân tích được chạy đi chạy lại nhiều lần, ghi đè kết quả liên tục vào database.
  - Fix / prevention: Cấu hình `visibility_timeout_seconds` của SQS tối thiểu bằng timeout của Lambda xử lý cộng thêm một khoảng đệm an toàn (ví dụ: SQS `910`s cho Lambda `900`s).

## 11. Knowledge Extension - Kiến thức mở rộng
- **Cơ chế Long Polling của SQS**: Việc thiết lập `receive_wait_time_seconds = 10` kích hoạt cơ chế Long Polling (truy vấn dài). SQS sẽ giữ kết nối và chờ tối đa 10 giây nếu hàng đợi trống thay vì phản hồi ngay lập tức rằng "không có tin nhắn". Điều này giúp giảm số lượng cuộc gọi API rỗng (empty receives), tiết kiệm chi phí vận hành SQS cho doanh nghiệp lên tới 90%.

## 12. Study Pack - Gói ôn tập
### Must remember
1. `package_docker.py` giúp tự động hóa việc đóng gói code chéo hệ điều hành.
2. AWS Lambda giới hạn upload trực tiếp ở mức 50MB; các gói lớn hơn phải được upload qua S3.
3. Hàng đợi SQS `alex-analysis-jobs` được dùng để trigger Planner bất đồng bộ.
4. Visibility timeout của SQS phải lớn hơn timeout của Lambda xử lý (ví dụ: SQS 910s, Lambda 900s).
5. IAM policy của agents Lambda cần cấp quyền InvokeFunction cho tiền tố `alex-*` để gọi chéo nhau.

### Self-check questions
1. Tại sao gói zip của Planner Lambda lại nặng hơn 50MB và làm thế nào Terraform vượt qua giới hạn này?
2. Điều gì xảy ra với một tin nhắn SQS nếu Planner Lambda bị crash 3 lần liên tiếp trong quá trình xử lý?

### Flashcards
- Q: Tài nguyên Terraform nào dùng để liên kết SQS Queue làm trigger cho Lambda?
  A: `aws_lambda_event_source_mapping`.
- Q: Dead Letter Queue (DLQ) có tác dụng gì?
  A: Cô lập các tin nhắn bị lỗi nhiều lần để tránh làm nghẽn hàng đợi chính.

### Interview Q&A
- Q: Khi triển khai kiến trúc đa tác tử trên AWS Lambda, làm thế nào để cấu hình bảo mật IAM theo nguyên tắc đặc quyền tối thiểu (least privilege)?
  A: (Recommended) Chúng ta tạo một IAM Role dùng chung hoặc các Role riêng biệt cho từng Lambda. Trong IAM Policy, chỉ cho phép các quyền cần thiết: ghi log vào đúng Log Group của nó; đọc/xóa tin nhắn trên đúng SQS queue của dự án; gọi Lambda với resource giới hạn bởi tiền tố `arn:aws:lambda:...:function:alex-*`; và chỉ truy cập đúng Secrets Manager chứa credentials của database quan hệ. Tránh tuyệt đối việc sử dụng wildcard `*` cho các hành động nhạy cảm hoặc tài nguyên toàn hệ thống.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.

---

# 101. Day 2 - End-to-End Testing of Multi-Agent Systems on AWS Lambda

Course domain: AI Engineer Production Track: Deploy LLMs & Agents at Scale
Course name: AI Engineer Production Track: Deploy LLMs & Agents at Scale

## 1. Source Map - Bản đồ nguồn
- Transcript: [101. Day 2 - End-to-End Testing of Multi-Agent Systems on AWS Lambda.txt](file:///G:/AIProduction_t6_2026/production/tai_lieu/week4/101.%20Day%202%20-%20End-to-End%20Testing%20of%20Multi-Agent%20Systems%20on%20AWS%20Lambda.txt) - Đã dùng
- Slide: [Production W4D2.pdf](file:///G:/AIProduction_t6_2026/production/slide/week4/Production%20W4D2.pdf) (Slide 4, 5, 6) - Đã dùng
- Code: 
  - [backend/test_full.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/test_full.py) - Đã dùng

## 2. Executive Summary - Tóm tắt cốt lõi
- Bài học cuối cùng hướng dẫn quy trình kiểm thử End-to-End (E2E) thực tế trên đám mây AWS sau khi đã hoàn tất triển khai hạ tầng.
- Việc kiểm thử được thực thi bất đồng bộ thông qua tệp [backend/test_full.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/test_full.py).
- Quy trình E2E kiểm thử mô phỏng chính xác hành vi người dùng: Gửi tin nhắn chứa `job_id` vào SQS Queue, SQS kích hoạt Planner Lambda trên AWS, Planner tự gọi chéo các worker Lambda khác để tính toán và lưu trữ dữ liệu, trong khi client kiểm thử liên tục poll database để hiển thị tiến độ thời gian thực.
- Thử nghiệm E2E chạy thực tế tốn khoảng 1.5 - 2 phút do độ trễ gọi API Bedrock chéo mạng.
- Kết quả kiểm thử thành công trả về đầy đủ báo cáo phân tích, dữ liệu biểu đồ JSON, kết quả Monte Carlo hưu trí và tóm tắt được ghi nhận chính xác trong database quan hệ.

## 3. Lesson Goals - Mục tiêu bài học
- **Concept goals - mục tiêu kiến thức**:
  - Hiểu cơ chế kiểm thử bất đồng bộ (asynchronous test harness) trong kiến trúc hướng sự kiện (event-driven).
  - Nắm được luồng đi của dữ liệu đầu-cuối từ SQS qua các Lambda Agents đến database.
- **Practical goals - mục tiêu thực hành**:
  - Chạy kiểm thử E2E hệ thống đa tác tử trên AWS bằng `test_full.py`.
  - Giám sát trạng thái job trong database.
- **What learner should be able to explain - người học cần giải thích được**:
  - Tại sao script kiểm thử E2E local lại phải chạy vòng lặp polling database thay vì chờ phản hồi HTTP trực tiếp từ Lambda.
  - Các bước diễn ra từ khi đẩy message vào SQS đến khi database cập nhật trạng thái `completed`.

## 4. Previous Context - Liên hệ với bài trước
- Bài học này kiểm thử toàn bộ hệ thống hạ tầng đã được cấu hình và deploy ở bài 100. Nó sử dụng dữ liệu database quan hệ (bảng `jobs`, `users`, `accounts`, `positions`) đã được thiết kế và di cư (migrations) ở Day 1.

## 5. Core Theory - Lý thuyết cốt lõi
- **Asynchronous testing (Kiểm thử bất đồng bộ)**: Phương pháp kiểm thử trong đó client kích hoạt tác vụ và không chặn kết nối để đợi kết quả, mà truy vấn định kỳ hoặc nhận webhook để biết trạng thái hoàn thành.
- **SQS Message Triggering (Kích hoạt bằng tin nhắn SQS)**: Cơ chế đẩy sự kiện vào hàng đợi để AWS tự động điều phối tài nguyên compute (Lambda) xử lý mà không cần client duy trì kết nối trực tiếp.
- **Database polling (Truy vấn cơ sở dữ liệu định kỳ)**: Kỹ thuật client liên tục gửi truy vấn đến database sau mỗi khoảng thời gian cố định (ví dụ 2 giây) để theo dõi sự thay đổi trạng thái của một bản ghi.

## 6. Workflow / Pipeline - Quy trình / luồng hoạt động
### Luồng hoạt động chi tiết đầu-cuối của E2E Test (End-to-End Detailed Workflow Walkthrough):
1. **Setup Test Data**: Script `test_full.py` kết nối database, kiểm tra xem test user `test_user_001` đã tồn tại chưa; nếu chưa, tự động tạo mới cùng tài khoản và 4 vị thế cổ phiếu (`SPY`, `QQQ`, `BND`, `VTI`).
2. **Create Job Record**: Script chèn một bản ghi job mới vào bảng `jobs` trong database với trạng thái `pending` và payload yêu cầu phân tích toàn diện. Nhận về `job_id` dạng UUID.
3. **Queue Ingestion**: Script sử dụng AWS SDK Boto3 SQS client để gửi một tin nhắn chứa JSON `{'job_id': job_id}` vào hàng đợi `alex-analysis-jobs`.
4. **Trigger Planner**: SQS phát hiện tin nhắn và kích hoạt hàm Lambda `alex-planner` (thông qua event source mapping).
5. **planner execution**:
   - Planner Lambda chuyển trạng thái job trong database sang `running`.
   - Chạy hàm Python `handle_missing_instruments` kiểm tra tag, gọi Lambda `alex-tagger` nếu thiếu nhãn.
   - Gọi module cập nhật giá thị trường từ Polygon.io.
   - Gọi song song 3 Lambda workers: `alex-reporter`, `alex-charter`, `alex-retirement`.
   - Mỗi worker tự chạy agent suy luận và ghi kết quả (Markdown report, JSON charts, Monte Carlo) vào đúng cột payload của mình trong database.
   - Khi tất cả hoàn tất, Planner Lambda chuyển trạng thái job sang `completed`.
6. **Client Polling**: Trong lúc AWS Lambda đang chạy trên cloud, script `test_full.py` ở local chạy vòng lặp `while` truy vấn database mỗi 2 giây để kiểm tra cột `status` của job.
7. **Result Output**: Khi phát hiện trạng thái chuyển sang `completed`, script dừng vòng lặp, tải dữ liệu báo cáo, biểu đồ, kết quả hưu trí về máy và in báo cáo định dạng đẹp ra màn hình console.

## 7. Techniques - Kỹ thuật sử dụng
- **DB-Based Async Job Coordination (Điều phối job bất đồng bộ qua Database)**:
  - Purpose - mục đích: Quản lý trạng thái và kết quả của các tiến trình chạy dài (long-running processes) trong môi trường serverless không duy trì trạng thái (stateless).
  - When to use - dùng khi nào: Khi các tác vụ xử lý có thời gian chạy vượt quá thời gian chờ tối đa của HTTP Gateway (thường là 29-30 giây).
  - Trade-off - đánh đổi: Tạo thêm lưu lượng truy vấn (read load) lên database trong quá trình polling.

## 8. Code Walkthrough - Phân tích code nếu có

### Phân tích [backend/test_full.py](file:///G:/AIProduction_t6_2026/production/week4/alex/backend/test_full.py#L98-L211)
Quy trình gửi sự kiện SQS và polling database của E2E Test:
```python
def main():
    db = Database()
    sqs = boto3.client('sqs')
    
    # 1. Tạo dữ liệu mẫu và chèn job trạng thái pending vào database
    test_user_id = setup_test_data(db)
    job_id = db.jobs.create(job_data)
    
    # 2. Tìm URL của hàng đợi SQS alex-analysis-jobs
    QUEUE_NAME = 'alex-analysis-jobs'
    response = sqs.list_queues(QueueNamePrefix=QUEUE_NAME)
    queue_url = response['QueueUrls'][0]
    
    # 3. Đẩy message chứa job_id vào SQS để kích hoạt Planner Lambda bất đồng bộ
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({'job_id': job_id})
    )
    
    # 4. Chạy vòng lặp poll database theo dõi trạng thái job
    start_time = time.time()
    timeout = 180  # Giới hạn thời gian test tối đa 3 phút
    last_status = None
    
    while time.time() - start_time < timeout:
        job = db.jobs.find_by_id(job_id)
        status = job['status']
        
        if status != last_status:
            print(f"[{int(time.time() - start_time)}s] Status: {status}")
            last_status = status
            
        if status == 'completed':
            # Job thành công, lấy dữ liệu in ra màn hình
            print("Job completed successfully!")
            print(f"Report length: {len(job['report_payload'].get('content', ''))} chars")
            print(f"Retirement success rate: {job['retirement_payload'].get('success_rate')}%")
            break
        elif status == 'failed':
            print(f"Job failed: {job.get('error_message')}")
            break
            
        time.sleep(2)  # Nghỉ 2 giây trước lần truy vấn tiếp theo
```

## 9. Options / Trade-offs - Bản đồ lựa chọn
- **Option 1: Gọi đồng bộ API Gateway Lambda rồi đợi kết quả phản hồi HTTP**
  - Pros: Rất đơn giản cho client, không cần viết vòng lặp polling database.
  - Cons: API Gateway có giới hạn thời gian chờ cứng (hard timeout) tối đa là 29-30 giây. Vì hệ thống agents xử lý tài chính mất từ 1.5 - 2 phút để hoàn thành, cuộc gọi API sẽ bị lỗi 504 Gateway Timeout mặc dù backend vẫn đang chạy.
  - When to choose: Các tác vụ nhanh dưới 15 giây.
- **Option 2: Gọi bất đồng bộ qua SQS và theo dõi trạng thái qua DB (Khuyên dùng)**
  - Pros: Vượt qua hoàn toàn giới hạn timeout của API Gateway, tăng trải nghiệm người dùng vì giao diện phản hồi lập tức là "đang xử lý", tăng khả năng chịu lỗi của hệ thống.
  - Cons: Yêu cầu lập trình thêm cơ chế polling ở client và quản lý trạng thái job phức tạp hơn.
  - When to choose: Các tác vụ phân tích nặng, gọi nhiều LLMs hoặc xử lý dữ liệu lớn.

## 10. Pitfalls - Lỗi / bẫy thường gặp
- **Failure mode**: Infinite Polling Loop.
  - Root cause: Script kiểm thử không định nghĩa thời gian timeout tối đa cho vòng lặp `while` truy vấn database. Khi Lambda gặp lỗi nghiêm trọng (như crash hệ thống) mà không thể cập nhật trạng thái `failed` vào DB, trạng thái job sẽ mãi mãi là `running`.
  - Symptom: Script test chạy mãi mãi không dừng, gây tốn tài nguyên CPU máy phát triển.
  - Fix / prevention: Luôn cấu hình tham số giới hạn thời gian chờ tối đa (timeout, ví dụ `180` giây) trong vòng lặp polling của script test để cưỡng chế ngắt kết nối.

## 11. Knowledge Extension - Kiến thức mở rộng
- **Khái niệm "Eventual Consistency - Tính nhất quán cuối cùng"**: Trong kiến trúc hướng sự kiện bất đồng bộ như dự án Alex, khi người dùng gửi yêu cầu, dữ liệu không lập tức hiển thị. Hệ thống chấp nhận một khoảng trễ thời gian (ở đây là 1.5 - 2 phút) để các agents Lambda phối hợp tính toán. Cuối cùng, dữ liệu trong database sẽ đạt trạng thái nhất quán và đầy đủ. Đây là nguyên lý thiết kế tối quan trọng của các hệ thống phân tán quy mô lớn (distributed systems at scale).

## 12. Study Pack - Gói ôn tập
### Must remember
1. `test_full.py` kiểm thử hệ thống bất đồng bộ đầu-cuối qua SQS và database polling.
2. API Gateway có giới hạn timeout cứng là 29s, do đó các tác vụ agents chạy lâu bắt buộc phải xử lý bất đồng bộ.
3. Luồng đi sự kiện: Client -> SQS -> Planner Lambda -> Workers Lambda -> Database updates -> Client Polling.
4. Script test E2E cần có cơ chế ngắt vòng lặp (timeout) để tránh lặp vô hạn khi Lambda bị crash.
5. Kết quả phân tích của từng worker agent được lưu trữ ở các cột payload JSONB riêng biệt của bảng `jobs`.

### Self-check questions
1. Tại sao cuộc gọi trực tiếp HTTP API Gateway lại không phù hợp để chạy hệ thống agents Alex?
2. Hãy mô tả cách thức script `test_full.py` phát hiện Planner Lambda đã hoàn tất xử lý.

### Flashcards
- Q: Thời gian chạy trung bình của một job phân tích đa tác tử Alex trên AWS Lambda là bao lâu?
  A: Khoảng 1.5 - 2 phút.
- Q: Cơ chế nào giúp client kiểm thử nhận biết được sự thay đổi trạng thái của job?
  A: Database polling loop (Vòng lặp truy vấn DB định kỳ mỗi 2 giây).

### Interview Q&A
- Q: Làm thế nào bạn có thể tối ưu hóa cơ chế kiểm tra tiến độ công việc (job progress) từ phía client thay vì sử dụng kỹ thuật database polling liên tục gây tải cho cơ sở dữ liệu?
  A: (Recommended) Để tối ưu hóa, tôi có thể thay thế database polling bằng hai giải pháp: Một là sử dụng **WebSockets** (thông qua AWS API Gateway WebSocket API). Khi Planner Lambda cập nhật trạng thái job thành công trong database, nó sẽ gửi một thông báo qua cổng WebSocket tới client đang kết nối thời gian thực. Hai là sử dụng cơ chế **Server-Sent Events (SSE)** hoặc thiết lập một dịch vụ Pub/Sub (như AWS AppSync/GraphQL Subscriptions) để đẩy trực tiếp sự kiện về client. Những cách này giúp loại bỏ hoàn toàn các yêu cầu đọc lặp đi lặp lại lên database quan hệ.

## 13. Missing Inputs - Còn thiếu gì
- Không phát hiện thiếu thông tin nào cho bài học này.
