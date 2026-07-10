# Guide 8 Enterprise — Code-level Features Design

Date: 2026-07-10
Status: Approved
Scope: Code-level guardrails, explainability, structured logging. No new AWS infrastructure.

## Overview

Implement the code-level enterprise features from `guides/8_enterprise.md` Sections 3-5:
- **Guardrails** (Section 4): charter output validation, input sanitization, response size limits
- **Explainability** (Section 5): tagger rationale, reporter recommendation reasoning, audit logging
- **Structured Logging** (Section 3): JSON event logs for all agents → CloudWatch + LangFuse

## New Modules: `backend/shared/`

Pattern follows the existing `backend/database/` shared library approach.

### `backend/shared/__init__.py`
Empty init to make the directory a Python package.

### `backend/shared/guardrails.py`
Three standalone functions, no class needed:

- `validate_chart_data(chart_json: str) -> tuple[bool, str, dict]`
  Validates Charter agent output. Checks: valid JSON, `charts` key exists, each chart has `type` and `data`, pie charts have `name`+`value`, bar charts have `category`. Returns `(is_valid, error_message, parsed_data)`.

- `sanitize_user_input(text: str) -> str`
  Checks for prompt injection patterns (`ignore previous instructions`, `disregard all prior`, `forget everything`, `new instructions:`, `system:`, `assistant:`). Returns `[INVALID INPUT DETECTED]` if found, original text otherwise. Case-insensitive.

- `truncate_response(text: str, max_length: int = 50000) -> str`
  Truncates response if longer than max_length. Appends `[Response truncated due to length]` marker.

### `backend/shared/audit.py`

- `AuditLogger` class with static method:
  - `log_ai_decision(agent_name, job_id, input_data, output_data, model_used, duration_ms, observability=None) -> dict`
  - Creates audit entry with: timestamp, agent, job_id, model, input_hash (SHA256), output summary (type, size_bytes), duration_ms
  - Logs to CloudWatch via `logger.info(json.dumps(...))`
  - Sends LangFuse event via `observability.create_event(...)` when observability context is available
  - Returns the audit dict

## Modified Files

### 1. `backend/charter/lambda_handler.py`
- Import `validate_chart_data`, `truncate_response` from `shared.guardrails`
- Import `AuditLogger` from `shared.audit`
- After `result.final_output`: call `validate_chart_data()`, on failure return safe fallback `{"charts": [], "error": "..."}`
- Before returning: call `truncate_response()` on final output
- Before returning: call `AuditLogger.log_ai_decision()`
- Structured logging: `CHARTER_STARTED`, `CHARTER_COMPLETED` events (CloudWatch JSON + LangFuse via observability)

### 2. `backend/planner/lambda_handler.py`
- Import `sanitize_user_input` from `shared.guardrails`
- Import `AuditLogger` from `shared.audit`
- Sanitize any user-provided text fields before passing to agents
- Structured logging: `PLANNER_STARTED`, `AGENT_INVOKED`, `AGENT_COMPLETED`, `PLANNER_COMPLETED` events
- Call `AuditLogger.log_ai_decision()` at completion
- All events go to both CloudWatch (`logger.info(json.dumps({...}))`) and LangFuse (`observability.create_event(...)`)

### 3. `backend/reporter/lambda_handler.py`
- Import `truncate_response` from `shared.guardrails`
- Import `AuditLogger` from `shared.audit`
- Before returning: call `truncate_response()` on final output
- Structured logging: `REPORTER_STARTED`, `REPORTER_COMPLETED` events
- Call `AuditLogger.log_ai_decision()` at completion

### 4. `backend/reporter/templates.py`
- Add `ANALYSIS_INSTRUCTIONS_WITH_EXPLANATION` constant appended to the existing instructions
- Format per recommendation: **Recommendation**, **Reasoning**, **Impact**, **Priority** (High/Medium/Low)

### 5. `backend/retirement/lambda_handler.py`
- Import `truncate_response` from `shared.guardrails`
- Import `AuditLogger` from `shared.audit`
- Before returning: call `truncate_response()` on final output
- Structured logging: `RETIREMENT_STARTED`, `RETIREMENT_COMPLETED` events
- Call `AuditLogger.log_ai_decision()` at completion

### 6. `backend/tagger/agent.py`
- Add `rationale: str` field to `InstrumentClassification` Pydantic model, placed **before** the classification fields (forces model to reason first)
- In `classify_instrument()`: log the rationale after classification

### 7. `backend/tagger/lambda_handler.py`
- Import `AuditLogger` from `shared.audit`
- Structured logging: `TAGGER_STARTED`, `TAGGER_COMPLETED` events
- Call `AuditLogger.log_ai_decision()` at completion

### 8. `backend/api/main.py`
- Import `sanitize_user_input` from `shared.guardrails`
- Apply to endpoints accepting user-generated text input (update preferences, goals, etc.)

## Structured Logging Event Schema

All events follow this JSON format for CloudWatch:
```json
{
  "event": "AGENT_NAME_STATUS",
  "job_id": "...",
  "timestamp": "ISO8601",
  "model": "openai/gpt-5.4-xxx",
  "duration_ms": 1234,
  "user_id": "clerk_user_id"
}
```

For LangFuse, same data sent via `observability.create_event(name=event_name, status_message=json.dumps({...}))`.

Agent-specific events:
- **Planner**: `PLANNER_STARTED`, `AGENT_INVOKED` (per worker agent), `AGENT_COMPLETED` (per worker agent), `PLANNER_COMPLETED`
- **Worker agents** (Tagger, Reporter, Charter, Retirement): `<AGENT>_STARTED`, `<AGENT>_COMPLETED`
- **All agents**: `<AGENT>_FAILED` on exception

## What This Does NOT Touch

- Terraform infrastructure (WAF, GuardDuty, VPC endpoints, CloudWatch alarms)
- Existing worktree changes (`trace()` → `RunConfig()` migration)
- `observability.py` modules (already working)
- `watch_agents.py` script (already exists)
- CloudWatch dashboards in `terraform/8_enterprise` (already deployed)
- `.env`, `terraform.tfvars`, or any secret files

## Testing Plan

1. Run each agent's `test_simple.py` to verify imports and basic functionality
2. Run `test_full.py` for reporter, charter, retirement, tagger individually
3. Run `backend/test_full.py` for end-to-end SQS pipeline
4. Check CloudWatch logs for structured JSON events
5. Check LangFuse dashboard for event traces

## Files Summary

| File | Action |
|---|---|
| `backend/shared/__init__.py` | NEW |
| `backend/shared/guardrails.py` | NEW |
| `backend/shared/audit.py` | NEW |
| `backend/charter/lambda_handler.py` | EDIT: guardrails + logging + audit |
| `backend/planner/lambda_handler.py` | EDIT: sanitization + logging + audit |
| `backend/reporter/lambda_handler.py` | EDIT: guardrails + logging + audit |
| `backend/reporter/templates.py` | EDIT: explainability instructions |
| `backend/retirement/lambda_handler.py` | EDIT: guardrails + logging + audit |
| `backend/tagger/agent.py` | EDIT: rationale field |
| `backend/tagger/lambda_handler.py` | EDIT: logging + audit |
| `backend/api/main.py` | EDIT: input sanitization |
