# Task 1 Report

## Phạm vi

Đã hoàn thành README cho:

- `backend/tagger/README.md`
- `backend/charter/README.md`

Không đụng tới file ngoài phạm vi task. Đã giữ nguyên file unrelated đang modified là `backend/database/README.md`.

## Source of truth đã dùng

Ưu tiên theo yêu cầu:

1. current code trong `backend/tagger` và `backend/charter`
2. current Terraform trong `terraform/6_agents`
3. guide/spec để bổ sung context khi cần

Các file đã đọc theo brief:

- `backend/tagger/agent.py`
- `backend/tagger/lambda_handler.py`
- `backend/tagger/observability.py`
- `backend/tagger/package_docker.py`
- `backend/tagger/templates.py`
- `backend/tagger/test_simple.py`
- `backend/tagger/test_full.py`
- `backend/tagger/track_tagger.py`
- `backend/tagger/try_tagger.py`
- `backend/tagger/pyproject.toml`
- `backend/charter/agent.py`
- `backend/charter/lambda_handler.py`
- `backend/charter/observability.py`
- `backend/charter/package_docker.py`
- `backend/charter/templates.py`
- `backend/charter/test_simple.py`
- `backend/charter/test_full.py`
- `backend/charter/pyproject.toml`

File bổ sung đã đọc để chốt migration/current state:

- `docs/superpowers/specs/2026-07-08-part6-readmes-design.md`
- `terraform/6_agents/main.tf`
- `terraform/6_agents/variables.tf`
- `terraform/6_agents/outputs.tf`
- `terraform/6_agents/terraform.tfvars.example`
- guides `1_permissions.md` đến `8_enterprise.md`
- `guides/architecture.md`
- `guides/agent_architecture.md`

## Kết quả thực hiện

### `backend/tagger/README.md`

README mô tả:

- vai trò Tagger trong Part 6
- tree thư mục thực tế
- sơ đồ kiến trúc và workflow bằng Mermaid
- file-by-file inventory bám code thật
- current Bedrock/LiteLLM model flow
- env vars thực sự dùng
- packaging, test, deploy commands
- section `Cách chuyển sang OpenAI models`

Điểm current state được ghi rõ:

- model runtime là `LitellmModel(model=f"bedrock/{model_id}")`
- `AWS_REGION_NAME` được set từ `BEDROCK_REGION`
- `OPENAI_API_KEY` hiện chủ yếu phục vụ observability/tracing
- file migration phải chỉnh gồm:
  - `backend/tagger/agent.py`
  - `terraform/6_agents/main.tf`
  - `terraform/6_agents/variables.tf`
  - `terraform/6_agents/terraform.tfvars.example`

Model mapping theo brief:

- `backend/tagger` -> `openai/gpt-5.4-nano`

### `backend/charter/README.md`

README mô tả:

- vai trò Charter trong Part 6
- tree thư mục thực tế
- sơ đồ kiến trúc và workflow bằng Mermaid
- file-by-file inventory bám code thật
- luồng build `portfolio_analysis` rồi gọi model
- cách parse JSON từ `final_output`
- cách chuyển mảng `charts` thành `charts_payload`
- cách lưu DB qua `db.jobs.update_charts`
- section `Cách chuyển sang OpenAI models`

Điểm current state được ghi rõ:

- naming/env hiện tại vẫn Bedrock-centric
- `AWS_REGION_NAME` được set cho LiteLLM Bedrock
- output là JSON text và đang parse thủ công
- `OPENAI_API_KEY` hiện chủ yếu phục vụ observability/tracing

Model mapping theo brief:

- `backend/charter` -> `openai/gpt-5.4-nano`

Migration note đặc thù đã nêu rõ:

- cần re-check JSON output stability sau khi migrate vì charter emit chart payloads

## Validation đã chạy

Đã chạy đúng các command trong brief:

```bash
wc -l backend/tagger/README.md backend/charter/README.md
rg -n "^## " backend/tagger/README.md backend/charter/README.md
rg -n "Cách chuyển sang OpenAI models|mermaid|BEDROCK_MODEL_ID|openai/gpt-5.4-nano" backend/tagger/README.md backend/charter/README.md
```

Kết quả:

- `backend/tagger/README.md`: 224 dòng
- `backend/charter/README.md`: 211 dòng
- cả hai đều dưới 600 dòng
- cả hai đều có đầy đủ section bắt buộc
- cả hai đều có section `Cách chuyển sang OpenAI models`
- cả hai đều có `mermaid`
- cả hai đều nhắc `BEDROCK_MODEL_ID`
- cả hai đều dùng đúng model mapping `openai/gpt-5.4-nano`

## Self-review

Đã tự review lại diff sau khi tạo file.

Kết luận:

- không thấy mismatch nào giữa README và current code đã đọc
- không mô tả sai rằng repo đã migrate sang OpenAI
- không chỉnh sửa file unrelated
- không có dấu hiệu vượt line budget

## Commit

Commit đã tạo:

- `d1b5448 docs: add part 6 tagger and charter readmes`

## Concerns

- Không chạy `uv run test_simple.py` hay `uv run test_full.py` vì brief chỉ yêu cầu validation tài liệu, không yêu cầu verify runtime behavior.
- Một số guide text Part 4 còn nói App Runner trong khi codebase có chỗ ghi đã chuyển researcher sang Lambda/function URL; README task này đã ưu tiên current code/Terraform của Part 6 nên không dùng guide text làm source of truth chính.
