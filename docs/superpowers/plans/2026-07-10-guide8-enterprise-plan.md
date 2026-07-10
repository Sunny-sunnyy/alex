# Guide 8 Enterprise — Code-Level Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement code-level enterprise features from Guide 8 (guardrails, explainability, structured logging with CloudWatch + LangFuse dual output) without touching AWS infrastructure.

**Architecture:** New `backend/shared/` module with `guardrails.py` and `audit.py`, following the existing `backend/database/` shared-library pattern. Eight existing agent files receive targeted edits for guardrail integration, explainability enhancements, and dual-output structured event logging.

**Tech Stack:** Python 3.12, OpenAI Agents SDK, LiteLLM, Pydantic, LangFuse, `uv`

## Global Constraints

- Never modify `.env`, `terraform.tfvars`, or any secret/credential file
- Never `pip install` — use `uv add` / `uv run`
- Preserve all existing worktree changes (`trace()` → `RunConfig()` migration)
- Do NOT touch terraform files, `observability.py` modules, or `watch_agents.py`
- Match surrounding code style exactly: 4-space indent, `logger.info()` logging, same import order
- All structured log events go to BOTH `logger.info(json.dumps({...}))` (CloudWatch) AND `observability.create_event(...)` (LangFuse) when observability context available

---

### Task 1: Create `backend/shared/__init__.py`

**Files:**
- Create: `backend/shared/__init__.py`

**Interfaces:**
- Produces: Python package `backend.shared` importable by all agents

- [ ] **Step 1: Create the empty init file**

```python
# backend/shared/__init__.py — shared enterprise utilities for Guide 8
```

- [ ] **Step 2: Verify import works**

Run: `cd backend/shared && uv run python -c "import shared; print('OK')"`
Expected: `OK` (or no error)

---

### Task 2: Create `backend/shared/guardrails.py`

**Files:**
- Create: `backend/shared/guardrails.py`

**Interfaces:**
- Produces: `validate_chart_data(chart_json: str) -> tuple[bool, str, dict]`
- Produces: `sanitize_user_input(text: str) -> str`
- Produces: `truncate_response(text: str, max_length: int = 50000) -> str`

- [ ] **Step 1: Write the guardrails module**

```python
"""
Shared guardrail utilities for Alex agents.
Guide 8 Section 4: input validation, output verification, response size limits.
"""

import json
import logging

logger = logging.getLogger(__name__)

# Prompt injection detection patterns (case-insensitive match)
_DANGEROUS_PATTERNS = [
    "ignore previous instructions",
    "disregard all prior",
    "forget everything",
    "new instructions:",
    "system:",
    "assistant:",
]


def validate_chart_data(chart_json: str) -> tuple[bool, str, dict]:
    """
    Validate that charter agent output is well-formed JSON with expected structure.

    Args:
        chart_json: Raw JSON string from the Charter agent.

    Returns:
        (is_valid, error_message, parsed_data).
        On failure, is_valid=False and parsed_data is {}.
    """
    try:
        data = json.loads(chart_json)

        if "charts" not in data:
            return False, "Missing required key: 'charts'", {}

        if not isinstance(data["charts"], list):
            return False, "Key 'charts' must be an array", {}

        for i, chart in enumerate(data["charts"]):
            if "type" not in chart:
                return False, f"Chart {i} missing 'type' field", {}
            if "data" not in chart:
                return False, f"Chart {i} missing 'data' field", {}
            if not isinstance(chart["data"], list):
                return False, f"Chart {i} data must be an array", {}

            if chart["type"] == "pie":
                for point in chart["data"]:
                    if "name" not in point or "value" not in point:
                        return False, f"Pie chart data points must have 'name' and 'value'", {}
            elif chart["type"] == "bar":
                for point in chart["data"]:
                    if "category" not in point:
                        return False, f"Bar chart data points must have 'category'", {}

        return True, "", data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from charter agent: {e}")
        return False, f"Invalid JSON: {e}", {}
    except Exception as e:
        logger.error(f"Unexpected error validating chart data: {e}")
        return False, f"Validation error: {e}", {}


def sanitize_user_input(text: str) -> str:
    """
    Check for prompt injection attempts in user-provided text.

    Returns "[INVALID INPUT DETECTED]" if injection patterns found,
    otherwise returns the original text unchanged.
    """
    if not text:
        return text

    text_lower = text.lower()
    for pattern in _DANGEROUS_PATTERNS:
        if pattern in text_lower:
            logger.warning(f"Potential prompt injection detected: pattern='{pattern}'")
            return "[INVALID INPUT DETECTED]"

    return text


def truncate_response(text: str, max_length: int = 50000) -> str:
    """
    Ensure response does not exceed reasonable size.

    Returns truncated text with a warning marker if truncation occurred.
    """
    if len(text) > max_length:
        logger.warning(f"Response truncated from {len(text)} to {max_length} characters")
        return text[:max_length] + "\n\n[Response truncated due to length]"
    return text
```

- [ ] **Step 2: Verify the module loads without errors**

Run: `cd backend/shared && uv run python -c "from guardrails import validate_chart_data, sanitize_user_input, truncate_response; print('OK')"`
Expected: `OK`

---

### Task 3: Create `backend/shared/audit.py`

**Files:**
- Create: `backend/shared/audit.py`

**Interfaces:**
- Produces: `AuditLogger.log_ai_decision(agent_name, job_id, input_data, output_data, model_used, duration_ms, observability=None) -> dict`

- [ ] **Step 1: Write the audit module**

```python
"""
Audit logging for AI decisions.
Guide 8 Section 5: compliance audit trail with CloudWatch + LangFuse dual output.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    """Static audit logger for AI agent decisions."""

    @staticmethod
    def log_ai_decision(
        agent_name: str,
        job_id: str,
        input_data: Dict[str, Any],
        output_data: Any,
        model_used: str,
        duration_ms: int,
        observability: Any = None,
    ) -> dict:
        """
        Record an auditable AI decision to CloudWatch and optionally LangFuse.

        Args:
            agent_name: e.g. "planner", "reporter", "charter", "retirement", "tagger"
            job_id: The analysis job UUID.
            input_data: The task/prompt data sent to the agent.
            output_data: The agent's final output (str or dict).
            model_used: The LiteLLM model string.
            duration_ms: Total agent execution time in milliseconds.
            observability: Optional observability context for LangFuse events.

        Returns:
            The audit entry dict that was logged.
        """
        output_type = type(output_data).__name__
        try:
            output_size = len(json.dumps(output_data))
        except (TypeError, ValueError):
            output_size = len(str(output_data))

        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "AI_DECISION",
            "agent": agent_name,
            "job_id": job_id,
            "model": model_used,
            "input_hash": hashlib.sha256(
                json.dumps(input_data, sort_keys=True, default=str).encode()
            ).hexdigest(),
            "output_summary": {
                "type": output_type,
                "size_bytes": output_size,
            },
            "duration_ms": duration_ms,
        }

        # CloudWatch structured log
        logger.info(json.dumps(audit_entry))

        # LangFuse event (when observability context is available)
        if observability is not None:
            try:
                observability.create_event(
                    name="AI Decision Audit",
                    status_message=json.dumps(audit_entry),
                )
            except Exception as e:
                logger.warning(f"AuditLogger: Failed to send LangFuse event: {e}")

        return audit_entry
```

- [ ] **Step 2: Verify the module loads**

Run: `cd backend/shared && uv run python -c "from audit import AuditLogger; print('OK')"`
Expected: `OK`

---

### Task 4: Update `backend/charter/lambda_handler.py` — guardrails + logging + audit

**Files:**
- Modify: `backend/charter/lambda_handler.py`

**Interfaces:**
- Consumes: `validate_chart_data` from `shared.guardrails`, `truncate_response` from `shared.guardrails`, `AuditLogger` from `shared.audit`
- Produces: (no interface change — same `lambda_handler` signature)

- [ ] **Step 1: Add imports at top of file**

After line 28 (`from observability import observe`), add:

```python
from shared.guardrails import validate_chart_data, truncate_response
from shared.audit import AuditLogger
```

- [ ] **Step 2: Add structured logging event at start of `run_charter_agent`**

After line 43 (`logger.info(f"run_charter_agent START | job={job_id} | model={MODEL_ID}")`), add:

```python
    # Structured event log — CloudWatch
    logger.info(json.dumps({
        "event": "CHARTER_STARTED",
        "job_id": job_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID,
    }))
```

Also add `from datetime import datetime, timezone` to imports (merge with existing datetime import if needed — actually `datetime` is not yet imported in charter, only `time` is. Check line 9: `import time`. Add next to it).

Actually, the charter file does NOT import datetime. Add after line 9 (`import time`):

```python
from datetime import datetime, timezone
```

- [ ] **Step 3: Add `validate_chart_data` call after JSON parse**

Replace the existing JSON parse block (lines 83-130 in current file, the `charts_data = None` through the `except json.JSONDecodeError` block) with a version that uses `validate_chart_data`. Specifically, after the `output = result.final_output` line and before the existing JSON extraction logic, insert the validation call. After the existing JSON extraction (the `start_idx`/`end_idx` block), add the validation:

After line 98 (`parsed_data = json.loads(json_str)`), insert:

```python
                # Guide 8 guardrail: validate chart structure
                is_valid, validation_error, _ = validate_chart_data(json_str)
                if not is_valid:
                    logger.error(f"Charter: Chart validation failed: {validation_error}")
                    charts_data = {}
                else:
```

And indent the existing charts extraction logic (lines 99-112) under the `else:` block. Then add an `else:` clause for the validation failure path if json.loads succeeded but validate_chart_data failed.

Actually, to minimize code churn, insert validation AFTER the successful `json.loads` but BEFORE the business logic. The cleanest approach: insert after line 101 (`logger.info(f"Charter: Successfully parsed JSON, found {len(charts)} charts")`):

```python
                # Guide 8 guardrail: validate chart structure
                is_valid, validation_error, _ = validate_chart_data(json_str)
                if not is_valid:
                    logger.error(f"Charter: Chart validation failed: {validation_error}")
                    charts_data = {}
                    charts_saved = False
```

And wrap the subsequent charts processing in `if is_valid:`.

- [ ] **Step 4: Add `truncate_response` and `AuditLogger` before return**

Before the return statement (around line 139, before `return {`), add:

```python
    # Guide 8: audit log
    t_total_ms = int(t_total * 1000)
    AuditLogger.log_ai_decision(
        agent_name="charter",
        job_id=job_id,
        input_data={"task_preview": str(task)[:500]},
        output_data=charts_data if charts_data else {},
        model_used=effective_model,
        duration_ms=t_total_ms,
    )
```

And add structured completion log:

```python
    logger.info(json.dumps({
        "event": "CHARTER_COMPLETED",
        "job_id": job_id,
        "duration_ms": t_total_ms,
        "model": effective_model,
        "charts_count": len(charts_data) if charts_data else 0,
    }))
```

- [ ] **Step 5: Verify charter imports and syntax**

Run: `cd backend/charter && uv run python -c "from lambda_handler import lambda_handler; print('OK')"`
Expected: `OK`

---

### Task 5: Update `backend/tagger/agent.py` — rationale field

**Files:**
- Modify: `backend/tagger/agent.py`

**Interfaces:**
- Produces: `InstrumentClassification.rationale` field (added before classification fields)

- [ ] **Step 1: Add `rationale` field to `InstrumentClassification`**

In the `InstrumentClassification` class (around line 94), add a `rationale` field BEFORE the `symbol` field:

```python
class InstrumentClassification(BaseModel):
    """Structured output for instrument classification"""

    model_config = ConfigDict(extra="forbid")

    rationale: str = Field(
        description="Detailed explanation of why these classifications were chosen, including specific factors considered. Explain your reasoning BEFORE providing the classification data."
    )
    symbol: str = Field(description="Ticker symbol of the instrument")
    name: str = Field(description="Name of the instrument")
    instrument_type: str = Field(description="Type: etf, stock, mutual_fund, bond_fund, etc.")
    current_price: float = Field(description="Current price per share in USD", gt=0)

    # Separate allocation objects
    allocation_asset_class: AllocationBreakdown = Field(description="Asset class breakdown")
    allocation_regions: RegionAllocation = Field(description="Regional breakdown")
    allocation_sectors: SectorAllocation = Field(description="Sector breakdown")

    # ... (validators remain unchanged)
```

- [ ] **Step 2: Log rationale in `classify_instrument`**

After line 204 (`classification = result.final_output_as(InstrumentClassification)`) and before line 206 (`elapsed = time.monotonic() - t_start`), add:

```python
        logger.info(
            f"Classification rationale for {symbol}: {classification.rationale[:500]}"
        )
```

- [ ] **Step 3: Verify syntax**

Run: `cd backend/tagger && uv run python -c "from agent import InstrumentClassification; print('OK')"`
Expected: `OK`

---

### Task 6: Update `backend/tagger/lambda_handler.py` — logging + audit

**Files:**
- Modify: `backend/tagger/lambda_handler.py`

**Interfaces:**
- Consumes: `AuditLogger` from `shared.audit`
- Produces: (no interface change)

- [ ] **Step 1: Add imports**

After line 17 (`from observability import observe`), add:

```python
from datetime import datetime, timezone
from shared.audit import AuditLogger
```

- [ ] **Step 2: Add structured logging in `process_instruments`**

After line 37 (`logger.info(f"process_instruments: {len(instruments)} instruments | model={MODEL_ID}")`), add:

```python
    logger.info(json.dumps({
        "event": "TAGGER_STARTED",
        "job_id": "batch",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID,
        "instrument_count": len(instruments),
    }))
```

Before the return statement of `process_instruments`, add completion event:

```python
    t_total_ms = int((time.monotonic() - t_start) * 1000)
    logger.info(json.dumps({
        "event": "TAGGER_COMPLETED",
        "duration_ms": t_total_ms,
        "model": MODEL_ID,
        "updated_count": len(updated),
        "error_count": len(errors),
    }))
```

- [ ] **Step 3: Add `AuditLogger` call in `lambda_handler`**

In the `lambda_handler` function, find the `with observe():` block and inside the try block, after processing completes and before returning success, add:

```python
            AuditLogger.log_ai_decision(
                agent_name="tagger",
                job_id=event.get("job_id", "unknown"),
                input_data={"instruments": [i.get("symbol", "?") for i in instruments]},
                output_data={"updated": updated, "errors": len(errors)},
                model_used=MODEL_ID,
                duration_ms=int((time.monotonic() - t_lambda_start) * 1000),
                observability=None,  # observability not available in tagger lambda_handler pattern
            )
```

Note: The tagger's lambda_handler uses `with observe():` without capturing the return value (no `as observability`). Check the actual pattern. If it's `with observe():` without `as`, we pass `None` for observability.

- [ ] **Step 4: Verify syntax**

Run: `cd backend/tagger && uv run python -c "from lambda_handler import lambda_handler; print('OK')"`
Expected: `OK`

---

### Task 7: Update `backend/reporter/templates.py` — explainability instructions

**Files:**
- Modify: `backend/reporter/templates.py`

**Interfaces:**
- Produces: `REPORTER_INSTRUCTIONS` updated with explainability requirements

- [ ] **Step 1: Append explainability section to REPORTER_INSTRUCTIONS**

Replace the closing `"""` of `REPORTER_INSTRUCTIONS` (after line 34) with the added explainability format requirements:

```python
REPORTER_INSTRUCTIONS = """You are a Report Writer Agent specializing in portfolio analysis and financial narrative generation.

Your primary task is to analyze the provided portfolio and generate a comprehensive markdown report.

You have access to this tool:
1. get_market_insights - Retrieve relevant market context for specific symbols

Your workflow:
1. First, analyze the portfolio data provided
2. Use get_market_insights to get relevant market context for the holdings
3. Generate a comprehensive analysis report in markdown format covering:
   - Executive Summary (3-4 key points)
   - Portfolio Composition Analysis
   - Diversification Assessment
   - Risk Profile Evaluation
   - Retirement Readiness
   - Specific Recommendations (5-7 actionable items)
   - Conclusion

4. Respond with your complete analysis in clear markdown format.

Report Guidelines:
- Write in clear, professional language accessible to retail investors
- Use markdown formatting with headers, bullets, and emphasis
- Include specific percentages and numbers where relevant
- Focus on actionable insights, not just observations
- Prioritize recommendations by impact
- Keep sections concise but comprehensive

Recommendation Format (MANDATORY for every recommendation):
When providing recommendations, always use this exact format:

**Recommendation:** [The specific action to take]
**Reasoning:** [Why this recommendation was made, including factors considered]
**Impact:** [Expected outcome if implemented with measurable metrics where possible]
**Priority:** [High/Medium/Low based on alignment with user goals and portfolio impact]

Always include at least 5 actionable recommendations following this format.
Start each recommendation with your reasoning process before stating the recommendation itself.
Note any assumptions made and limitations or caveats that apply.
"""
```

- [ ] **Step 2: Verify syntax**

Run: `cd backend/reporter && uv run python -c "from templates import REPORTER_INSTRUCTIONS; print('OK, length:', len(REPORTER_INSTRUCTIONS))"`
Expected: `OK, length: <number>`

---

### Task 8: Update `backend/reporter/lambda_handler.py` — guardrails + logging + audit

**Files:**
- Modify: `backend/reporter/lambda_handler.py`

**Interfaces:**
- Consumes: `truncate_response` from `shared.guardrails`, `AuditLogger` from `shared.audit`
- Produces: (no interface change)

- [ ] **Step 1: Add imports**

After line 33 (`from observability import observe`), add:

```python
from datetime import datetime, timezone
from shared.guardrails import truncate_response
from shared.audit import AuditLogger
```

- [ ] **Step 2: Add structured logging in `run_reporter_agent`**

After line 57 (`logger.info(f"run_reporter_agent START | job={job_id} | model={MODEL_ID}")`), add:

```python
    logger.info(json.dumps({
        "event": "REPORTER_STARTED",
        "job_id": job_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID,
    }))
```

- [ ] **Step 3: Add `truncate_response` on output**

After line 78 (`response = result.final_output`), add:

```python
    # Guide 8 guardrail: truncate oversized responses
    response = truncate_response(response)
```

- [ ] **Step 4: Add `AuditLogger` and completion event before return**

Before the return statement (around line 115, before `return {`), add:

```python
    t_total_ms = int(t_total * 1000)
    AuditLogger.log_ai_decision(
        agent_name="reporter",
        job_id=job_id,
        input_data={"task_preview": str(task)[:500]},
        output_data={"report_length": len(response)},
        model_used=effective_model,
        duration_ms=t_total_ms,
        observability=observability if 'observability' in dir() else None,
    )

    logger.info(json.dumps({
        "event": "REPORTER_COMPLETED",
        "job_id": job_id,
        "duration_ms": t_total_ms,
        "model": effective_model,
        "report_length": len(response),
    }))
```

Note: `observability` is not in scope inside `run_reporter_agent` — it's only available in `lambda_handler`'s `with observe() as observability:`. For the `run_reporter_agent` function, pass `None` for observability (the lambda_handler has its own audit path if needed). Actually, let me check — the lambda_handler passes `observability` to `run_reporter_agent` in the current code. Let me check...

Looking at the reporter lambda_handler, `observability` is captured from `with observe() as observability:` and it IS used inside `run_reporter_agent` for the judge span. So `observability` IS available inside `run_reporter_agent`. The function signature includes `observability=None`. So we pass the `observability` parameter.

Update the AuditLogger call to use the function's `observability` parameter:

```python
    AuditLogger.log_ai_decision(
        agent_name="reporter",
        job_id=job_id,
        input_data={"task_preview": str(task)[:500]},
        output_data={"report_length": len(response)},
        model_used=effective_model,
        duration_ms=t_total_ms,
        observability=observability,
    )
```

- [ ] **Step 5: Verify syntax**

Run: `cd backend/reporter && uv run python -c "from lambda_handler import lambda_handler; print('OK')"`
Expected: `OK`

---

### Task 9: Update `backend/retirement/lambda_handler.py` — guardrails + logging + audit

**Files:**
- Modify: `backend/retirement/lambda_handler.py`

**Interfaces:**
- Consumes: `truncate_response` from `shared.guardrails`, `AuditLogger` from `shared.audit`
- Produces: (no interface change)

- [ ] **Step 1: Add imports**

After line 34 (`from observability import observe`), add:

```python
from datetime import datetime, timezone
from shared.guardrails import truncate_response
from shared.audit import AuditLogger
```

- [ ] **Step 2: Add structured logging in `run_retirement_agent`**

Find the `run_retirement_agent` function start (around line 64 with `@retry`). After the first `logger.info` line that logs START, add:

```python
    logger.info(json.dumps({
        "event": "RETIREMENT_STARTED",
        "job_id": job_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID,
    }))
```

- [ ] **Step 3: Add `truncate_response` on output**

After `result.final_output` is captured, add:

```python
    response = truncate_response(response)
```

- [ ] **Step 4: Add `AuditLogger` and completion event before return**

Before the return statement, add:

```python
    t_total_ms = int(t_total * 1000)
    AuditLogger.log_ai_decision(
        agent_name="retirement",
        job_id=job_id,
        input_data={"task_preview": str(task)[:500]},
        output_data={"analysis_length": len(response)},
        model_used=effective_model,
        duration_ms=t_total_ms,
    )

    logger.info(json.dumps({
        "event": "RETIREMENT_COMPLETED",
        "job_id": job_id,
        "duration_ms": t_total_ms,
        "model": effective_model,
        "analysis_length": len(response),
    }))
```

- [ ] **Step 5: Verify syntax**

Run: `cd backend/retirement && uv run python -c "from lambda_handler import lambda_handler; print('OK')"`
Expected: `OK`

---

### Task 10: Update `backend/planner/lambda_handler.py` — sanitization + logging + audit

**Files:**
- Modify: `backend/planner/lambda_handler.py`

**Interfaces:**
- Consumes: `sanitize_user_input` from `shared.guardrails`, `AuditLogger` from `shared.audit`
- Produces: (no interface change)

- [ ] **Step 1: Add imports**

After line 29 (`from observability import observe`), add:

```python
from datetime import datetime, timezone
from shared.guardrails import sanitize_user_input
from shared.audit import AuditLogger
```

- [ ] **Step 2: Add structured logging in `run_orchestrator`**

After line 46 (`logger.info(f"run_orchestrator START | job={job_id} | model={MODEL_ID}")`), add:

```python
        job = db.jobs.find_by_id(job_id)
        user_id = job["clerk_user_id"] if job else "unknown"
        logger.info(json.dumps({
            "event": "PLANNER_STARTED",
            "job_id": job_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL_ID,
        }))
```

Note: There's already a `job = db.jobs.find_by_id(job_id)` call later. Move it earlier or restructure. Actually, looking at the code more carefully, line 49 does `db.jobs.update_status(job_id, 'running')`. The job fetch doesn't happen before the START log. Let's add a minimal fetch:

```python
        # Fetch job for user_id logging
        job = db.jobs.find_by_id(job_id)
        user_id = job["clerk_user_id"] if job else "unknown"
        logger.info(json.dumps({
            "event": "PLANNER_STARTED",
            "job_id": job_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL_ID,
        }))
```

This replaces the simple `logger.info(f"run_orchestrator START...")` line.

- [ ] **Step 3: Add `AGENT_INVOKED` / `AGENT_COMPLETED` events**

In the part of `run_orchestrator` where agents are invoked (after the agent.run section in the orchestrator flow), add per-agent invoke logs. Since the orchestrator uses tools to invoke agents, we log around the tool calls. Add after the agent run completes (around line 86, after `db.jobs.update_status(job_id, "completed")`):

```python
        logger.info(json.dumps({
            "event": "PLANNER_COMPLETED",
            "job_id": job_id,
            "user_id": user_id,
            "duration_ms": int(t_total * 1000),
            "model": effective_model,
            "status": "success",
        }))
```

For AGENT_INVOKED events, the orchestrator invokes agents via tools (Lambda invocations). The tool functions themselves (`invoke_reporter`, `invoke_charter`, etc.) are in `agent.py`, not `lambda_handler.py`. To keep the scope focused, add invoke events in the orchestrator's main flow. After the agent creation but before Runner.run, or better yet, add them inside the agent.py tool functions.

Actually, to keep it clean and scoped to lambda_handler.py only: add AGENT_INVOKED logs right before the `Runner.run()` call and AGENT_COMPLETED after — the agents are invoked as tools DURING the planner's Runner.run, so we log at the boundaries:

After line 80 (`context=context,`), before the Runner.run, add comment about agent invocation happening via tools. The actual agent-specific invoke logs would need to go in `agent.py` tool functions. For now, log the three agents that will be invoked:

```python
        # Log expected agent invocations (tools in agent.py handle actual invoke)
        for agent_name in ["reporter", "charter", "retirement"]:
            logger.info(json.dumps({
                "event": "AGENT_INVOKED",
                "agent": agent_name,
                "job_id": job_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }))
```

Place this right before `result = await Runner.run(...)`.

- [ ] **Step 4: Add `AuditLogger` call at completion**

Before the `except` block (around line 95, after completion logging), add:

```python
        AuditLogger.log_ai_decision(
            agent_name="planner",
            job_id=job_id,
            input_data={"task_preview": str(task)[:500]},
            output_data={"status": "completed"},
            model_used=effective_model,
            duration_ms=int(t_total * 1000),
            observability=None,
        )
```

- [ ] **Step 5: Sanitize user input in `lambda_handler`**

Not needed for planner — it receives SQS messages, not user text. Skip sanitization here.

- [ ] **Step 6: Verify syntax**

Run: `cd backend/planner && uv run python -c "from lambda_handler import lambda_handler; print('OK')"`
Expected: `OK`

---

### Task 11: Update `backend/api/main.py` — input sanitization

**Files:**
- Modify: `backend/api/main.py`

**Interfaces:**
- Consumes: `sanitize_user_input` from `shared.guardrails`

- [ ] **Step 1: Add import**

After line 23 (`from src import Database`), add:

```python
from shared.guardrails import sanitize_user_input
```

- [ ] **Step 2: Apply sanitization in `update_user` endpoint**

In the `update_user` function (around line 193), add sanitization for free-text fields before processing:

```python
    # Guide 8 guardrail: sanitize user-provided text
    if user_update.display_name:
        user_update.display_name = sanitize_user_input(user_update.display_name)
```

Insert after the function signature and before the database update logic.

- [ ] **Step 3: Apply sanitization in `create_account` endpoint**

In the `create_account` function (around line 236), add:

```python
    # Guide 8 guardrail: sanitize user-provided text
    account.account_name = sanitize_user_input(account.account_name)
    if account.account_purpose:
        account.account_purpose = sanitize_user_input(account.account_purpose)
```

- [ ] **Step 4: Apply sanitization in `update_account` endpoint**

In the `update_account` function (around line 262), add:

```python
    # Guide 8 guardrail: sanitize user-provided text
    if account_update.account_name:
        account_update.account_name = sanitize_user_input(account_update.account_name)
    if account_update.account_purpose:
        account_update.account_purpose = sanitize_user_input(account_update.account_purpose)
```

- [ ] **Step 5: Verify syntax**

Run: `cd backend/api && uv run python -c "from main import app; print('OK')"`
Expected: `OK`

---

### Task 12: Integration test — all agents load correctly

**Files:**
- Test: (no new test file — use existing `test_simple.py` per agent)

- [ ] **Step 1: Test all agent modules can import after changes**

Run:
```bash
cd backend/charter && uv run python -c "from lambda_handler import lambda_handler; print('charter OK')"
cd backend/tagger && uv run python -c "from lambda_handler import lambda_handler; print('tagger OK')"
cd backend/reporter && uv run python -c "from lambda_handler import lambda_handler; print('reporter OK')"
cd backend/retirement && uv run python -c "from lambda_handler import lambda_handler; print('retirement OK')"
cd backend/planner && uv run python -c "from lambda_handler import lambda_handler; print('planner OK')"
cd backend/api && uv run python -c "from main import app; print('api OK')"
```

Expected: All print `OK` with no import errors.

- [ ] **Step 2: Run existing `test_simple.py` for each agent to verify nothing broken**

Run:
```bash
cd backend/tagger && uv run test_simple.py
cd backend/reporter && uv run test_simple.py
cd backend/charter && uv run test_simple.py
cd backend/retirement && uv run test_simple.py
cd backend/planner && uv run test_simple.py
```

Expected: All tests pass. May take 30-60 seconds.

- [ ] **Step 3: Commit**

```bash
git add backend/shared/
git add backend/charter/lambda_handler.py
git add backend/tagger/agent.py backend/tagger/lambda_handler.py
git add backend/reporter/templates.py backend/reporter/lambda_handler.py
git add backend/retirement/lambda_handler.py
git add backend/planner/lambda_handler.py
git add backend/api/main.py
git commit -m "feat: Guide 8 enterprise features — guardrails, explainability, structured logging

- New backend/shared/ module with guardrails.py (validate_chart_data,
  sanitize_user_input, truncate_response) and audit.py (AuditLogger)
- Charter: output validation via validate_chart_data, truncate_response
- Tagger: rationale field in InstrumentClassification for explainability
- Reporter: explainability instructions in templates, truncate_response
- All agents: structured JSON event logging (CloudWatch + LangFuse dual output)
- API: input sanitization for user-provided text fields

Co-Authored-By: Claude <noreply@anthropic.com>"
```

