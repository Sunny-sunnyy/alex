# Update for Guide 8 — Enterprise Features

**Date:** 2026-07-10
**Status:** Deployed & Verified on AWS Lambda
**Region:** ap-southeast-1

---

## 1. Mục tiêu

Triển khai toàn bộ code-level enterprise features từ `guides/8_enterprise.md`:
- **Section 3 — Monitoring:** Structured JSON logging cho tất cả agents (CloudWatch + LangFuse dual output)
- **Section 4 — Guardrails:** Charter output validation, input sanitization, response size limits
- **Section 5 — Explainability:** Tagger rationale, Reporter recommendation reasoning, Audit logging

Phạm vi: code-level only. Không triển khai WAF, GuardDuty, VPC endpoints (terraform infrastructure changes).

---

## 2. Module mới: `backend/shared/`

Theo pattern giống hệt `backend/database/` — shared package được import bởi tất cả agents.

```
backend/shared/
├── pyproject.toml              # name = "alex-shared", uv package config
├── uv.lock
└── alex_shared/
    ├── __init__.py
    ├── guardrails.py           # validate_chart_data, sanitize_user_input, truncate_response
    └── audit.py                # AuditLogger class
```

### 2.1 `guardrails.py`

| Function | Purpose | Input | Output |
|---|---|---|---|
| `validate_chart_data(chart_json)` | Kiểm tra Charter agent output | JSON string | `(is_valid, error_msg, parsed_data)` |
| `sanitize_user_input(text)` | Phát hiện prompt injection | User text | Cleaned text hoặc `[INVALID INPUT DETECTED]` |
| `truncate_response(text, max_length)` | Giới hạn kích thước response | Response text + limit | Truncated text + warning marker |

**Prompt injection patterns được phát hiện:**
- `ignore previous instructions`
- `disregard all prior`
- `forget everything`
- `new instructions:`, `system:`, `assistant:`

### 2.2 `audit.py`

`AuditLogger.log_ai_decision()` — static method:
- Tạo audit entry với: timestamp, agent name, job_id, model, SHA256 input hash, output summary (type + size), duration_ms
- Ghi ra **CloudWatch** qua `logger.info(json.dumps(...))`
- Ghi ra **LangFuse** qua `observability.create_event(...)` (nếu observability context có sẵn)

---

## 3. Files đã thay đổi

### 3.1 Dependency (pyproject.toml) — 6 files

Mỗi agent được thêm `alex-shared` vào `dependencies` và `[tool.uv.sources]`:

| File | Dependency Source |
|---|---|
| `backend/charter/pyproject.toml` | `{ path = "../shared", editable = true }` |
| `backend/reporter/pyproject.toml` | `{ path = "../shared", editable = true }` |
| `backend/retirement/pyproject.toml` | `{ path = "../shared", editable = true }` |
| `backend/planner/pyproject.toml` | `{ path = "../shared", editable = true }` |
| `backend/tagger/pyproject.toml` | `{ path = "../shared", editable = true }` |
| `backend/api/pyproject.toml` | `{ path = "../shared", editable = true }` |

### 3.2 Agent code — 8 files

#### `backend/charter/lambda_handler.py`
- Import: `validate_chart_data`, `truncate_response`, `AuditLogger`, `datetime/timezone`
- **Guardrail**: Gọi `validate_chart_data()` sau khi parse JSON từ agent output. Nếu validation fail → fallback `{"charts": [], "error": "..."}`
- **Guardrail**: Gọi `truncate_response()` trước khi return
- **Structured events**: `CHARTER_STARTED`, `CHARTER_COMPLETED` (CloudWatch JSON)
- **Audit**: `AuditLogger.log_ai_decision()` trước return

#### `backend/tagger/agent.py`
- **Explainability**: Thêm field `rationale: str` vào `InstrumentClassification` Pydantic model, đặt **trước** các classification fields để model reasoning trước
- **Log**: Log rationale sau khi classification

#### `backend/tagger/lambda_handler.py`
- Import: `AuditLogger`, `datetime/timezone`
- **Structured events**: `TAGGER_STARTED`, `TAGGER_COMPLETED` trong `process_instruments()`

#### `backend/reporter/templates.py`
- **Explainability**: Thêm recommendation format bắt buộc vào `REPORTER_INSTRUCTIONS`:
  ```
  **Recommendation:** [action]
  **Reasoning:** [why]
  **Impact:** [expected outcome]
  **Priority:** [High/Medium/Low]
  ```

#### `backend/reporter/lambda_handler.py`
- Import: `truncate_response`, `AuditLogger`, `datetime/timezone`
- **Guardrail**: Gọi `truncate_response()` sau judge evaluation
- **Structured events**: `REPORTER_STARTED`, `REPORTER_COMPLETED`
- **Audit**: `AuditLogger.log_ai_decision()` với `observability` context

#### `backend/retirement/lambda_handler.py`
- Import: `truncate_response`, `AuditLogger`, `datetime/timezone`
- **Guardrail**: Gọi `truncate_response()` trên `result.final_output` trước khi lưu DB
- **Structured events**: `RETIREMENT_STARTED`, `RETIREMENT_COMPLETED`
- **Audit**: `AuditLogger.log_ai_decision()`

#### `backend/planner/lambda_handler.py`
- Import: `sanitize_user_input`, `AuditLogger`, `datetime/timezone`
- **Structured events**: `PLANNER_STARTED` (có user_id), `AGENT_INVOKED` x3 (reporter/charter/retirement), `PLANNER_COMPLETED`
- **Audit**: `AuditLogger.log_ai_decision()` sau khi orchestration hoàn tất

#### `backend/api/main.py`
- Import: `sanitize_user_input`
- **Guardrail**: Áp dụng sanitization cho free-text fields ở 3 endpoints:
  - `PUT /api/user` → `display_name`
  - `POST /api/accounts` → `account_name`, `account_purpose`
  - `PUT /api/accounts/{account_id}` → `account_name`, `account_purpose`

### 3.3 Package scripts fix — 5 files

Tất cả `package_docker.py` files (tagger, charter, reporter, retirement, planner):

| File | Fixes |
|---|---|
| `backend/tagger/package_docker.py` | ANSI strip + /shared mount |
| `backend/charter/package_docker.py` | ANSI strip + /shared mount |
| `backend/reporter/package_docker.py` | ANSI strip + /shared mount |
| `backend/retirement/package_docker.py` | ANSI strip + /shared mount |
| `backend/planner/package_docker.py` | ANSI strip + /shared mount |

---

## 4. Vấn đề gặp phải và cách khắc phục

### 4.1 Vấn đề 1: `uv export` ANSI color codes

**Triệu chứng:**
```
ERROR: Invalid requirement: '\x1b[32m# This file was autogenerated by uv...'
```

**Root cause:** Phiên bản `uv` mới hơn thêm ANSI color escape codes vào output của `uv export`. File `requirements.txt` được tạo ra chứa comment có màu, khiến `pip install` không parse được.

**Fix:** Thêm `import re` và strip ANSI codes trước khi filter requirements:
```python
ansi_stripped = re.sub(r'\x1b\[[0-9;]*m', '', requirements_result)
```
Đồng thời skip tất cả dòng comment (`#`) và dòng trống.

### 4.2 Vấn đề 2: Thiếu `/shared` mount trong Docker

**Triệu chứng:** Lambda deployment package không chứa `alex_shared` module.

**Root cause:** `package_docker.py` chỉ mount `backend/database/` vào Docker container, không mount `backend/shared/`. Module `alex_shared` không được cài đặt trong Lambda package.

**Fix:** Thêm vào tất cả 5 `package_docker.py`:
```python
"-v", f"{backend_dir}/shared:/shared",
# và trong Docker command:
"""... && pip install --target ./package --no-deps /shared"""
```

### 4.3 Vấn đề 3: Job timeout 3 phút

**Triệu chứng:** `test_full.py` báo "Job timed out after 3 minutes" trong khi pipeline vẫn đang chạy.

**Root cause:** Pipeline thực tế mất ~3.3 phút (Planner orchestration + Reporter 2 phút + Charter + Retirement). Timeout 3 phút trong test script là không đủ.

**Fix:** Không cần sửa code — pipeline tự hoàn thành sau 3.3 phút. Đây là giới hạn của test script, không phải lỗi hệ thống.

### 4.4 Vấn đề 4: Subagent over-engineering Task 1

**Triệu chứng:** Subagent (deepseek-v4-flash) tạo `pyproject.toml` không cần thiết và mất 5+ phút debug hatchling build system cho task đơn giản là tạo `__init__.py`.

**Root cause:** Model rẻ (haiku-tier) không đủ khả năng cho task đơn giản + thiếu context về project structure.

**Fix:** Kill subagent, làm Tasks 1-3 inline. Các task code changes sau đó cũng làm inline thay vì subagents.

---

## 5. Phương pháp kiểm tra

### 5.1 Local test
```bash
# Verify imports
cd backend/charter && uv run python -c "from lambda_handler import lambda_handler; print('OK')"
# ... (all 6 agents pass)

# Run test_simple.py for each agent (MOCK_LAMBDAS=true, real OpenAI API)
cd backend/tagger && uv run test_simple.py     # PASS
cd backend/reporter && uv run test_simple.py    # PASS
cd backend/charter && uv run test_simple.py     # PASS
cd backend/retirement && uv run test_simple.py  # PASS
cd backend/planner && uv run test_simple.py     # PASS
```

### 5.2 AWS Deploy

```bash
# Package (Docker required)
cd backend && uv run package_docker.py
# Result: 5/5 packaged (86-88 MB each)

# Deploy to Lambda
cd backend && uv run deploy_all_lambdas.py
# Result: Apply complete! Resources: 5 added, 5 changed, 5 destroyed
```

### 5.3 End-to-end test via SQS

```bash
cd backend && uv run test_full.py
```

**Job ID:** `6c0ceee0-4e2b-44a3-a88b-b966a1b18d25`
**Kết quả cuối cùng:** `completed`
- Report: 13,594 characters
- Charts: 5 visualizations
- Retirement: 11,427 characters
- Error: None

### 5.4 CloudWatch Structured Events Verification

Tất cả events confirmed trong CloudWatch logs:

**Planner events:**
```json
{"event": "PLANNER_STARTED", "job_id": "6c0ceee0...", "user_id": "test_user_001", "model": "openai/gpt-5.4-mini"}
{"event": "AGENT_INVOKED", "agent": "reporter", "job_id": "6c0ceee0..."}
{"event": "AGENT_INVOKED", "agent": "charter", "job_id": "6c0ceee0..."}
{"event": "AGENT_INVOKED", "agent": "retirement", "job_id": "6c0ceee0..."}
{"event": "AI_DECISION", "agent": "planner", "duration_ms": 198411}
{"event": "PLANNER_COMPLETED", "status": "success"}
```

**Reporter events:**
```json
{"event": "REPORTER_STARTED", "job_id": "6c0ceee0...", "model": "openai/gpt-5.4-mini"}
{"event": "AI_DECISION", "agent": "reporter", "duration_ms": 38030}
{"event": "REPORTER_COMPLETED", "report_length": 13373}
```

**Charter events:**
```json
{"event": "CHARTER_STARTED", "job_id": "6c0ceee0...", "model": "openai/gpt-4.1-nano"}
{"event": "AI_DECISION", "agent": "charter", "duration_ms": 8794, "output_summary": {"size_bytes": 2347}}
{"event": "CHARTER_COMPLETED", "charts_count": 5}
```

**Retirement events:**
```json
{"event": "RETIREMENT_STARTED", "job_id": "6c0ceee0...", "model": "openai/gpt-5.4-nano"}
{"event": "AI_DECISION", "agent": "retirement", "duration_ms": 19480}
{"event": "RETIREMENT_COMPLETED", "analysis_length": 11427}
```

---

## 6. Git commits

```
74a5f09 fix: strip ANSI codes from uv export and mount /shared in Docker packages
8221537 feat: Guide 8 enterprise features — guardrails, explainability, structured logging
```

**Tổng cộng:** 27 files changed, 1,636 insertions, 101 deletions

---

## 7. Model Configuration (Live)

| Agent | Model | Env Var |
|---|---|---|
| Planner | `openai/gpt-5.4-mini` | `MODEL_ID_PLANNER` |
| Tagger | `openai/gpt-5.4-nano` | `MODEL_ID_TAGGER` |
| Reporter | `openai/gpt-5.4-mini` | `MODEL_ID_REPORTER` |
| Charter | `openai/gpt-4.1-nano` | `MODEL_ID_CHARTER` |
| Retirement | `openai/gpt-5.4-nano` | `MODEL_ID_RETIREMENT` |
| Judge | `openai/gpt-5.4-nano` | `MODEL_ID_JUDGE` |

---

## 8. Những thứ KHÔNG thay đổi

- Terraform files (WAF, GuardDuty, VPC endpoints, alarms — nằm ngoài scope)
- Worktree changes hiện tại (`trace()` → `RunConfig()` migration)
- `observability.py` modules (đã hoạt động từ trước)
- `watch_agents.py` script (đã có sẵn)
- CloudWatch dashboards trong `terraform/8_enterprise` (đã deploy từ trước)
- `.env`, `terraform.tfvars`, credentials, API keys

---

## 9. Các lệnh hữu ích

### Kiểm tra structured events trên CloudWatch
```bash
aws logs tail /aws/lambda/alex-planner --since 10m --region ap-southeast-1 | grep '"event"'
aws logs tail /aws/lambda/alex-reporter --since 10m --region ap-southeast-1 | grep '"event"'
aws logs tail /aws/lambda/alex-charter --since 10m --region ap-southeast-1 | grep '"event"'
aws logs tail /aws/lambda/alex-retirement --since 10m --region ap-southeast-1 | grep '"event"'
```

### Package + Deploy
```bash
cd backend && uv run package_docker.py
cd backend && uv run deploy_all_lambdas.py
```

### Run full integration test
```bash
cd backend && uv run test_full.py
```
