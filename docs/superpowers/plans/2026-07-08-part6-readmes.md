# Part 6 READMEs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tạo 6 README tiếng Việt cho các folder chính của Part 6, phản ánh đúng code/Terraform hiện tại và có thêm mục hướng dẫn chuyển sang OpenAI models.

**Architecture:** Triển khai theo 3 cụm tài liệu: backend agents nhẹ (`tagger`, `charter`), backend agents nặng hơn (`reporter`, `retirement`), và cụm orchestration/infrastructure (`planner`, `terraform/6_agents`). Mỗi task vừa khám phá dependency trực tiếp, vừa viết README tương ứng, rồi tự kiểm tra section bắt buộc, line count, và độ khớp với source of truth.

**Tech Stack:** Markdown, Mermaid, Python backend code, Terraform, `rg`, `sed`, `wc`

## Global Constraints

- Chỉ tạo/chỉnh README cho 6 folder đã chốt trong spec.
- README phải bằng tiếng Việt có dấu.
- Mỗi README mặc định dưới 600 dòng; nếu vượt phải dừng lại xin phép user trước khi ghi file đó.
- Khi guide text và code lệch nhau, lấy code hiện tại, README cục bộ còn đúng, và Terraform hiện tại làm source of truth.
- `backend/planner/README.md` phải bao phủ thêm các script cross-cutting ở `backend/`.
- Mỗi README phải có section `Cách chuyển sang OpenAI models`.
- Section migration phải trung thực: không mô tả repo như thể đã migrate thật.
- Tạm giữ naming cũ như `BEDROCK_MODEL_ID` và `BEDROCK_REGION` trong phần migration để giảm churn.
- Mapping model cần phản ánh quyết định hiện tại:
  - `backend/planner` → `openai/gpt-5.4-mini`
  - `backend/retirement` → `openai/gpt-5.4-nano`
  - `backend/charter` → `openai/gpt-5.4-nano`
  - `backend/reporter` → `openai/gpt-5.4-nano`
  - `backend/tagger` → `openai/gpt-5.4-nano`

---

## File Structure

**Files to create**

- `backend/tagger/README.md` — tài liệu cho agent phân loại instrument, test scripts cục bộ, cách chuyển model sang OpenAI.
- `backend/charter/README.md` — tài liệu cho agent tạo chart payload, output JSON workflow, cách chuyển model sang OpenAI.
- `backend/reporter/README.md` — tài liệu cho agent viết report, vector query, `judge.py`, và cách chuyển model sang OpenAI.
- `backend/retirement/README.md` — tài liệu cho agent retirement analysis, simulation/report flow, và cách chuyển model sang OpenAI.
- `backend/planner/README.md` — tài liệu cho orchestrator, lambda invocation graph, và toàn bộ cross-cutting scripts ở `backend/`.
- `terraform/6_agents/README.md` — tài liệu cho toàn bộ hạ tầng Part 6 trên AWS, IAM, SQS, Lambda env vars, outputs, và migration notes sang OpenAI.

**Files to read for context while implementing**

- `backend/tagger/*` trừ `uv.lock`
- `backend/charter/*` trừ `uv.lock`
- `backend/reporter/*` trừ `uv.lock`
- `backend/retirement/*` trừ `uv.lock`
- `backend/planner/*` trừ `uv.lock`
- `backend/package_docker.py`
- `backend/deploy_all_lambdas.py`
- `backend/test_simple.py`
- `backend/test_full.py`
- `backend/test_multiple_accounts.py`
- `backend/test_scale.py`
- `backend/watch_agents.py`
- `terraform/6_agents/main.tf`
- `terraform/6_agents/variables.tf`
- `terraform/6_agents/outputs.tf`
- `terraform/6_agents/terraform.tfvars.example`
- `guides/3_ingest.md`
- `guides/4_researcher.md`
- `guides/5_database.md`
- `guides/6_agents.md`
- `backend/database/README.md`
- `backend/ingest/README.md`
- `backend/researcher/README.md`
- `terraform/3_ingestion/README.md`
- `terraform/4_researcher/README.md`
- `terraform/5_database/README.md`

### Task 1: Create README for `backend/tagger` and `backend/charter`

**Files:**
- Create: `backend/tagger/README.md`
- Create: `backend/charter/README.md`
- Read: `backend/tagger/agent.py`
- Read: `backend/tagger/lambda_handler.py`
- Read: `backend/tagger/observability.py`
- Read: `backend/tagger/package_docker.py`
- Read: `backend/tagger/templates.py`
- Read: `backend/tagger/test_simple.py`
- Read: `backend/tagger/test_full.py`
- Read: `backend/tagger/track_tagger.py`
- Read: `backend/tagger/try_tagger.py`
- Read: `backend/tagger/pyproject.toml`
- Read: `backend/charter/agent.py`
- Read: `backend/charter/lambda_handler.py`
- Read: `backend/charter/observability.py`
- Read: `backend/charter/package_docker.py`
- Read: `backend/charter/templates.py`
- Read: `backend/charter/test_simple.py`
- Read: `backend/charter/test_full.py`
- Read: `backend/charter/pyproject.toml`

**Interfaces:**
- Consumes: Spec at `docs/superpowers/specs/2026-07-08-part6-readmes-design.md`
- Produces:
  - `backend/tagger/README.md`
  - `backend/charter/README.md`
  - Shared terminology for later READMEs: “current state”, “Cách chuyển sang OpenAI models”, “source of truth”

- [ ] **Step 1: Read code and extract inventory for `tagger`**

Run:

```bash
sed -n '1,260p' backend/tagger/agent.py
sed -n '1,260p' backend/tagger/lambda_handler.py
sed -n '1,220p' backend/tagger/templates.py
sed -n '1,220p' backend/tagger/observability.py
sed -n '1,220p' backend/tagger/package_docker.py
sed -n '1,220p' backend/tagger/test_simple.py
sed -n '1,220p' backend/tagger/test_full.py
sed -n '1,260p' backend/tagger/track_tagger.py
sed -n '1,220p' backend/tagger/try_tagger.py
sed -n '1,220p' backend/tagger/pyproject.toml
```

Expected: xác định được entry points, env vars, model init, packaging flow, test flow.

- [ ] **Step 2: Read code and extract inventory for `charter`**

Run:

```bash
sed -n '1,260p' backend/charter/agent.py
sed -n '1,240p' backend/charter/lambda_handler.py
sed -n '1,220p' backend/charter/templates.py
sed -n '1,220p' backend/charter/observability.py
sed -n '1,220p' backend/charter/package_docker.py
sed -n '1,220p' backend/charter/test_simple.py
sed -n '1,220p' backend/charter/test_full.py
sed -n '1,220p' backend/charter/pyproject.toml
```

Expected: xác định được JSON/chart workflow, env vars, packaging flow, test flow.

- [ ] **Step 3: Write `backend/tagger/README.md`**

README must include this section skeleton:

```markdown
# `backend/tagger` — ...
## Nhiệm vụ chính
## Cấu trúc thư mục
## Sơ đồ tổng quan kiến trúc
## Chi tiết từng file
## Workflow chính
## Mối liên kết giữa các file
## Mối liên hệ với folder khác
## Cách sử dụng nhanh
## Cách chuyển sang OpenAI models
## Tóm tắt
```

Migration notes must explicitly mention:

```markdown
- Current state: `LitellmModel(model=f"bedrock/{model_id}")`
- Suggested model: `openai/gpt-5.4-nano`
- Files to adjust when migrating: `backend/tagger/agent.py`, `terraform/6_agents/main.tf`, `terraform/6_agents/variables.tf`, `terraform/6_agents/terraform.tfvars.example`
```

- [ ] **Step 4: Write `backend/charter/README.md`**

README must include this section skeleton:

```markdown
# `backend/charter` — ...
## Nhiệm vụ chính
## Cấu trúc thư mục
## Sơ đồ tổng quan kiến trúc
## Chi tiết từng file
## Workflow chính
## Mối liên kết giữa các file
## Mối liên hệ với folder khác
## Cách sử dụng nhanh
## Cách chuyển sang OpenAI models
## Tóm tắt
```

Migration notes must explicitly mention:

```markdown
- Current state: uses Bedrock model env naming and `AWS_REGION_NAME`
- Suggested model: `openai/gpt-5.4-nano`
- Re-check JSON output stability after migration because this agent emits chart payloads
```

- [ ] **Step 5: Validate both READMEs**

Run:

```bash
wc -l backend/tagger/README.md backend/charter/README.md
rg -n "^## " backend/tagger/README.md backend/charter/README.md
rg -n "Cách chuyển sang OpenAI models|mermaid|BEDROCK_MODEL_ID|openai/gpt-5.4-nano" backend/tagger/README.md backend/charter/README.md
```

Expected:

- both files exist
- both files stay under 600 lines
- both files include required section and migration section

- [ ] **Step 6: Commit**

```bash
git add backend/tagger/README.md backend/charter/README.md
git commit -m "docs: add part 6 tagger and charter readmes"
```

### Task 2: Create README for `backend/reporter` and `backend/retirement`

**Files:**
- Create: `backend/reporter/README.md`
- Create: `backend/retirement/README.md`
- Read: `backend/reporter/agent.py`
- Read: `backend/reporter/lambda_handler.py`
- Read: `backend/reporter/judge.py`
- Read: `backend/reporter/observability.py`
- Read: `backend/reporter/package_docker.py`
- Read: `backend/reporter/templates.py`
- Read: `backend/reporter/test_simple.py`
- Read: `backend/reporter/test_full.py`
- Read: `backend/reporter/pyproject.toml`
- Read: `backend/retirement/agent.py`
- Read: `backend/retirement/lambda_handler.py`
- Read: `backend/retirement/observability.py`
- Read: `backend/retirement/package_docker.py`
- Read: `backend/retirement/templates.py`
- Read: `backend/retirement/test_simple.py`
- Read: `backend/retirement/test_full.py`
- Read: `backend/retirement/pyproject.toml`

**Interfaces:**
- Consumes:
  - `backend/tagger/README.md` and `backend/charter/README.md` terminology and migration phrasing
  - Spec at `docs/superpowers/specs/2026-07-08-part6-readmes-design.md`
- Produces:
  - `backend/reporter/README.md`
  - `backend/retirement/README.md`
  - documented rationale for `gpt-5.4-nano` on both agents

- [ ] **Step 1: Read code and extract inventory for `reporter`**

Run:

```bash
sed -n '1,320p' backend/reporter/agent.py
sed -n '1,260p' backend/reporter/lambda_handler.py
sed -n '1,240p' backend/reporter/judge.py
sed -n '1,220p' backend/reporter/templates.py
sed -n '1,220p' backend/reporter/observability.py
sed -n '1,220p' backend/reporter/package_docker.py
sed -n '1,220p' backend/reporter/test_simple.py
sed -n '1,220p' backend/reporter/test_full.py
sed -n '1,220p' backend/reporter/pyproject.toml
```

Expected: xác định được vector query/tool flow, markdown output flow, `judge.py` role, env vars, model init path.

- [ ] **Step 2: Read code and extract inventory for `retirement`**

Run:

```bash
sed -n '1,340p' backend/retirement/agent.py
sed -n '1,260p' backend/retirement/lambda_handler.py
sed -n '1,220p' backend/retirement/templates.py
sed -n '1,220p' backend/retirement/observability.py
sed -n '1,220p' backend/retirement/package_docker.py
sed -n '1,220p' backend/retirement/test_simple.py
sed -n '1,220p' backend/retirement/test_full.py
sed -n '1,220p' backend/retirement/pyproject.toml
```

Expected: xác định được projection/simulation flow, env vars, output persistence path, test/build flow.

- [ ] **Step 3: Write `backend/reporter/README.md`**

README must include this section skeleton:

```markdown
# `backend/reporter` — ...
## Nhiệm vụ chính
## Cấu trúc thư mục
## Sơ đồ tổng quan kiến trúc
## Chi tiết từng file
## Workflow chính
## Mối liên kết giữa các file
## Mối liên hệ với folder khác
## Cách sử dụng nhanh
## Cách chuyển sang OpenAI models
## Tóm tắt
```

Migration notes must explicitly mention:

```markdown
- Suggested model: `openai/gpt-5.4-nano`
- `judge.py` also needs review during migration if it still instantiates a Bedrock model
- If report quality drops, upgrade `reporter` before other specialist agents
```

- [ ] **Step 4: Write `backend/retirement/README.md`**

README must include this section skeleton:

```markdown
# `backend/retirement` — ...
## Nhiệm vụ chính
## Cấu trúc thư mục
## Sơ đồ tổng quan kiến trúc
## Chi tiết từng file
## Workflow chính
## Mối liên kết giữa các file
## Mối liên hệ với folder khác
## Cách sử dụng nhanh
## Cách chuyển sang OpenAI models
## Tóm tắt
```

Migration notes must explicitly mention:

```markdown
- Suggested model: `openai/gpt-5.4-nano`
- Current repo still uses Bedrock naming and init path
- Because this agent performs retirement reasoning, README must warn to validate output quality after migration even though cost/latency is prioritized
```

- [ ] **Step 5: Validate both READMEs**

Run:

```bash
wc -l backend/reporter/README.md backend/retirement/README.md
rg -n "^## " backend/reporter/README.md backend/retirement/README.md
rg -n "Cách chuyển sang OpenAI models|judge.py|openai/gpt-5.4-nano|BEDROCK_REGION" backend/reporter/README.md backend/retirement/README.md
```

Expected:

- both files exist
- both files stay under 600 lines
- migration notes and required sections are present

- [ ] **Step 6: Commit**

```bash
git add backend/reporter/README.md backend/retirement/README.md
git commit -m "docs: add part 6 reporter and retirement readmes"
```

### Task 3: Create README for `backend/planner`

**Files:**
- Create: `backend/planner/README.md`
- Read: `backend/planner/agent.py`
- Read: `backend/planner/lambda_handler.py`
- Read: `backend/planner/templates.py`
- Read: `backend/planner/market.py`
- Read: `backend/planner/prices.py`
- Read: `backend/planner/observability.py`
- Read: `backend/planner/package_docker.py`
- Read: `backend/planner/test_simple.py`
- Read: `backend/planner/test_full.py`
- Read: `backend/planner/test_market.py`
- Read: `backend/planner/pyproject.toml`
- Read: `backend/package_docker.py`
- Read: `backend/deploy_all_lambdas.py`
- Read: `backend/test_simple.py`
- Read: `backend/test_full.py`
- Read: `backend/test_multiple_accounts.py`
- Read: `backend/test_scale.py`
- Read: `backend/watch_agents.py`

**Interfaces:**
- Consumes:
  - The language conventions set in Tasks 1-2
  - Spec at `docs/superpowers/specs/2026-07-08-part6-readmes-design.md`
- Produces:
  - `backend/planner/README.md`
  - the canonical explanation for cross-cutting backend scripts in Part 6

- [ ] **Step 1: Read planner code and orchestration helpers**

Run:

```bash
sed -n '1,340p' backend/planner/agent.py
sed -n '1,340p' backend/planner/lambda_handler.py
sed -n '1,260p' backend/planner/templates.py
sed -n '1,260p' backend/planner/market.py
sed -n '1,220p' backend/planner/prices.py
sed -n '1,220p' backend/planner/observability.py
sed -n '1,220p' backend/planner/package_docker.py
sed -n '1,220p' backend/planner/test_simple.py
sed -n '1,220p' backend/planner/test_full.py
sed -n '1,220p' backend/planner/test_market.py
sed -n '1,220p' backend/planner/pyproject.toml
```

Expected: xác định được orchestration flow, lambda invocation graph, Polygon pricing flow, mock/local behavior, and planner-specific model init.

- [ ] **Step 2: Read cross-cutting backend scripts**

Run:

```bash
sed -n '1,260p' backend/package_docker.py
sed -n '1,260p' backend/deploy_all_lambdas.py
sed -n '1,260p' backend/test_simple.py
sed -n '1,260p' backend/test_full.py
sed -n '1,260p' backend/test_multiple_accounts.py
sed -n '1,260p' backend/test_scale.py
sed -n '1,260p' backend/watch_agents.py
```

Expected: xác định được packaging/deployment/test/watch workflows để gộp vào README planner.

- [ ] **Step 3: Write `backend/planner/README.md`**

README must include this section skeleton:

```markdown
# `backend/planner` — ...
## Nhiệm vụ chính
## Cấu trúc thư mục
## Sơ đồ tổng quan kiến trúc
## Chi tiết từng file
## Workflow chính
## Mối liên kết giữa các file
## Mối liên hệ với folder khác
## Cross-cutting scripts trong `backend/`
## Cách sử dụng nhanh
## Cách chuyển sang OpenAI models
## Tóm tắt
```

Migration notes must explicitly mention:

```markdown
- Suggested model: `openai/gpt-5.4-mini`
- Planner should remain the strongest model in Part 6 because it owns orchestration decisions
- Test and log scripts that print Bedrock details should be reviewed when migrating
```

- [ ] **Step 4: Validate planner README**

Run:

```bash
wc -l backend/planner/README.md
rg -n "^## " backend/planner/README.md
rg -n "Cross-cutting scripts trong `backend/`|Cách chuyển sang OpenAI models|openai/gpt-5.4-mini|deploy_all_lambdas.py|watch_agents.py" backend/planner/README.md
```

Expected:

- file exists
- file stays under 600 lines
- cross-cutting section exists
- migration section exists

- [ ] **Step 5: Commit**

```bash
git add backend/planner/README.md
git commit -m "docs: add part 6 planner readme"
```

### Task 4: Create README for `terraform/6_agents`

**Files:**
- Create: `terraform/6_agents/README.md`
- Read: `terraform/6_agents/main.tf`
- Read: `terraform/6_agents/variables.tf`
- Read: `terraform/6_agents/outputs.tf`
- Read: `terraform/6_agents/terraform.tfvars.example`
- Read: `terraform/6_agents/.terraform.lock.hcl`
- Read: `backend/planner/README.md`
- Read: `backend/tagger/README.md`
- Read: `backend/reporter/README.md`
- Read: `backend/charter/README.md`
- Read: `backend/retirement/README.md`

**Interfaces:**
- Consumes:
  - completed backend READMEs from Tasks 1-3
  - spec at `docs/superpowers/specs/2026-07-08-part6-readmes-design.md`
- Produces:
  - `terraform/6_agents/README.md`
  - canonical infra-level migration notes for Part 6 OpenAI switch

- [ ] **Step 1: Read Terraform and extract resource inventory**

Run:

```bash
sed -n '1,420p' terraform/6_agents/main.tf
sed -n '421,840p' terraform/6_agents/main.tf
sed -n '1,260p' terraform/6_agents/variables.tf
sed -n '1,260p' terraform/6_agents/outputs.tf
sed -n '1,260p' terraform/6_agents/terraform.tfvars.example
sed -n '1,220p' terraform/6_agents/.terraform.lock.hcl
```

Expected: xác định đầy đủ resources, IAM, env vars, outputs, package sources, and Bedrock assumptions.

- [ ] **Step 2: Write `terraform/6_agents/README.md`**

README must include this section skeleton:

```markdown
# `terraform/6_agents` — ...
## Mục tiêu
## Sơ đồ tài nguyên AWS
## Chi tiết từng tài nguyên
## IAM Roles & Policies
## Environment Variables tổng hợp
## Outputs sau khi triển khai
## Các biến cần điền trong `terraform.tfvars`
## Version Constraints
## Quan hệ với các phần khác
## Cách sử dụng nhanh
## Cách chuyển sang OpenAI models
## Tóm tắt
```

Migration notes must explicitly mention:

```markdown
- Current state: Terraform injects `BEDROCK_MODEL_ID` and `BEDROCK_REGION` into all Part 6 Lambdas
- Early-stage migration can keep those variable names but change their semantics and values
- Review Bedrock IAM policy blocks, env vars, `openai_api_key`, and `terraform.tfvars.example` together
- This README must point readers back to each backend README for code-level changes
```

- [ ] **Step 3: Validate Terraform README**

Run:

```bash
wc -l terraform/6_agents/README.md
rg -n "^## " terraform/6_agents/README.md
rg -n "IAM Roles & Policies|Environment Variables tổng hợp|Cách chuyển sang OpenAI models|BEDROCK_MODEL_ID|OPENAI_API_KEY" terraform/6_agents/README.md
```

Expected:

- file exists
- file stays under 600 lines
- required infra sections and migration notes are present

- [ ] **Step 4: Final consistency pass across all six READMEs**

Run:

```bash
wc -l backend/tagger/README.md backend/charter/README.md backend/reporter/README.md backend/retirement/README.md backend/planner/README.md terraform/6_agents/README.md
rg -n "Cách chuyển sang OpenAI models" backend/tagger/README.md backend/charter/README.md backend/reporter/README.md backend/retirement/README.md backend/planner/README.md terraform/6_agents/README.md
rg -n "openai/gpt-5.4-nano|openai/gpt-5.4-mini" backend/tagger/README.md backend/charter/README.md backend/reporter/README.md backend/retirement/README.md backend/planner/README.md terraform/6_agents/README.md
```

Expected:

- all six files exist
- all six files stay under 600 lines
- all six files include migration section
- model mapping matches the approved spec

- [ ] **Step 5: Commit**

```bash
git add terraform/6_agents/README.md backend/tagger/README.md backend/charter/README.md backend/reporter/README.md backend/retirement/README.md backend/planner/README.md
git commit -m "docs: add part 6 backend and terraform readmes"
```
