# Task 4 Report — `terraform/6_agents/README.md`

## Trạng thái

Hoàn thành.

## Phạm vi đã thực hiện

- Đọc brief tại `.superpowers/sdd/task-4-brief.md`
- Đọc spec tại `docs/superpowers/specs/2026-07-08-part6-readmes-design.md`
- Đọc guides `1_permissions.md` đến `8_enterprise.md`
- Đọc toàn bộ file Terraform được yêu cầu trong `terraform/6_agents/`
- Đọc 5 backend README đã hoàn thành:
  - `backend/planner/README.md`
  - `backend/tagger/README.md`
  - `backend/reporter/README.md`
  - `backend/charter/README.md`
  - `backend/retirement/README.md`
- Tạo file mới `terraform/6_agents/README.md`

## Nội dung chính đã thêm vào README

README mới cho `terraform/6_agents` hiện bao phủ:

- mục tiêu và current state Bedrock-centric
- sơ đồ tài nguyên AWS bằng Mermaid
- inventory resource chi tiết cho SQS, DLQ, IAM role/policy, S3 package bucket, S3 objects, 5 Lambdas, event source mapping, CloudWatch log groups
- tổng hợp IAM roles/policies theo capability thực tế
- bảng environment variables theo từng Lambda
- outputs sau triển khai và lưu ý về output text cũ
- bảng các biến cần điền trong `terraform.tfvars`
- version constraints từ `main.tf` và `.terraform.lock.hcl`
- quan hệ với các part trước và 5 backend README
- quick-start commands
- section `Cách chuyển sang OpenAI models`
- mapping model hạ tầng:
  - planner -> `openai/gpt-5.4-mini`
  - tagger/reporter/charter/retirement -> `openai/gpt-5.4-nano`

## Điểm nhất quán đã kiểm tra

### Validation cho README mới

Đã chạy:

```bash
wc -l terraform/6_agents/README.md
rg -n "^## " terraform/6_agents/README.md
rg -n "IAM Roles & Policies|Environment Variables tổng hợp|Cách chuyển sang OpenAI models|BEDROCK_MODEL_ID|OPENAI_API_KEY" terraform/6_agents/README.md
```

Kết quả:

- file tồn tại
- 331 dòng, dưới ngưỡng 600
- đủ section bắt buộc
- có migration notes và các keyword bắt buộc

### Final consistency pass trên cả 6 README

Đã chạy:

```bash
wc -l backend/tagger/README.md backend/charter/README.md backend/reporter/README.md backend/retirement/README.md backend/planner/README.md terraform/6_agents/README.md
rg -n "Cách chuyển sang OpenAI models" backend/tagger/README.md backend/charter/README.md backend/reporter/README.md backend/retirement/README.md backend/planner/README.md terraform/6_agents/README.md
rg -n "openai/gpt-5.4-nano|openai/gpt-5.4-mini" backend/tagger/README.md backend/charter/README.md backend/reporter/README.md backend/retirement/README.md backend/planner/README.md terraform/6_agents/README.md
```

Kết quả:

- cả 6 file đều tồn tại
- tất cả đều dưới 600 dòng
- cả 6 file đều có section `Cách chuyển sang OpenAI models`
- model mapping khớp spec đã duyệt

## Phát hiện quan trọng

Có 1 mismatch đáng ghi nhận giữa Terraform output text và repo hiện tại:

- `terraform/6_agents/outputs.tf` trong output `setup_instructions` vẫn nhắc `uv run run_full_test.py`
- repo hiện tại không có `run_full_test.py`
- file test thực tế là `backend/test_full.py` và `backend/planner/test_full.py`

README mới đã document rõ mismatch này thay vì lặp lại hướng dẫn cũ.

## Tự review

Đã kiểm tra lại README theo các tiêu chí sau:

- phản ánh Terraform hiện tại, không giả vờ repo đã migrate sang OpenAI
- giữ naming `BEDROCK_MODEL_ID` và `BEDROCK_REGION` trong migration notes như brief yêu cầu
- chỉ ra rõ vai trò hiện tại của `OPENAI_API_KEY`
- đóng vai trò canonical infra-level counterpart cho 5 backend README
- có link ngược về backend README cho code-level changes
- không đụng vào các file ngoài phạm vi task

## Files đã thay đổi

- `terraform/6_agents/README.md`
- `.superpowers/sdd/task-4-report.md`

## Worktree ngoài phạm vi đã giữ nguyên

- `backend/database/README.md`
- `docs/superpowers/plans/2026-07-08-part6-readmes.md`

## Commit

Commit được tạo sau khi stage đúng 2 file thuộc task này.
