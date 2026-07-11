Tôi là sinh viên đang học khóa học “AI in Production”, và chúng ta đang làm việc trong repo Alex của khóa học.

  Mục tiêu của phiên này trước hết là nạp đúng bối cảnh dự án. Không viết code, không sửa file, không chạy test/deploy/AWS/Terraform,
  không cài dependency trước khi hoàn thành bước này.

  ## 1. Kiểm tra trạng thái repo

  - Chạy `git status --short` để nhận biết các thay đổi có sẵn; tuyệt đối không sửa, reset, stage hoặc commit các thay đổi đó.
  - Không đọc hoặc in giá trị từ `.env`, `terraform.tfvars`, credentials, API key, hoặc secret files.

  ## 2. Ưu tiên CodeGraph cho code structure

  CodeGraph đã được cài và MCP Codex được cấu hình.

  1. Kiểm tra index bằng `codegraph status .`.
  2. Nếu index hợp lệ và up-to-date:
     - Dùng `codegraph_explore` cho các câu hỏi về architecture code, symbol, request flow, dependency, callers/callees, impact và
     test bị ảnh hưởng.
     - Không đọc tuần tự toàn bộ source code chỉ để “hiểu repo”.
  3. Nếu MCP tool chưa xuất hiện trong session:
     - Dùng CLI `codegraph explore "<câu hỏi>"` làm fallback.
     - Báo rõ rằng cần mở session Codex mới để MCP được nạp nếu cần.
  4. Nếu `.codegraph/` bị thiếu hoặc index lỗi:
     - Không tự ý rebuild khi chưa báo cho tôi.
     - Đề xuất chính xác lệnh cần chạy: `codegraph init .`
  5. Sau khi chỉnh code ở các lượt sau:
     - Ưu tiên dùng CodeGraph để xem impact trước khi đọc file thủ công hoặc chạy test.
     - Dùng `codegraph affected` khi cần xác định test bị ảnh hưởng.

  Lưu ý: CodeGraph là nguồn cho quan hệ tĩnh của code; không thay thế việc đọc guide, README, cấu hình, AWS state, CloudWatch logs
  hoặc runtime behavior.

  ## 3. Tài liệu bắt buộc phải đọc

  Đọc kỹ các file sau:

  - `gameplan.md` — ưu tiên cao nhất
  - `guides/agent_architecture.md`
  - `guides/architecture.md`
  - Toàn bộ Guides 1–8 theo đúng thứ tự
  - `backend/*/README.md`
  - `frontend/README.md`
  - `terraform/*/README.md`
  - `Update_for_8_enterprise.md`
  - `README_about_enterprise.md`

  Chỉ đọc các link/tài liệu liên quan thêm khi thật sự cần để giải thích mâu thuẫn hoặc hiểu implementation hiện tại.

  ## 4. Bối cảnh hiện tại

  - Tôi đang đã hoàn thành toàn bộ dự án.
  - và đã hoàn thành các guide trước đó.
  - Ưu tiên source of truth theo thứ tự:
    1. Code và Terraform hiện tại
    2. README hiện tại của từng folder
    3. `gameplan.md`
    4. Guide gốc

  Đặc biệt lưu ý các guide cũ có thể còn mô tả Bedrock/App Runner, trong khi implementation hiện tại có thể đã migrate sang OpenAI
  qua LiteLLM và Researcher có thể chạy bằng Lambda Function URL.

  ## 5. Báo cáo sau khi nạp context

  Sau khi hoàn tất, chỉ trả lời ngắn gọn:

  - CodeGraph: version, trạng thái index, MCP/CLI đã dùng.
  - Tech stack và entry points chính.
  - Luồng chính: frontend/API → SQS → Planner → specialist agents → Aurora; Researcher → ingest → S3 Vectors.
  - Các mâu thuẫn hoặc rủi ro quan trọng giữa guide và implementation hiện tại.
  - Các thay đổi có sẵn trong worktree cần được giữ nguyên.
  - Những câu hỏi thực sự cần làm rõ trước khi bắt đầu.

  Sau đó dừng lại và chờ lệnh tiếp theo của tôi.