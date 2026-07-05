# Researcher Observability, Stability Fix, and Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Researcher instability observable and classifiable, fix the current “runs sometimes work, sometimes fail” bug based on evidence, then benchmark `openrouter` `gpt-oss-120b` vs `openai/gpt-5.4-nano` using fixed topics on deployed Lambda runtime.

**Architecture:** Add a small observability layer inside `backend/researcher/server.py` that emits structured phase logs and normalized outcomes without redesigning the API. Improve `backend/researcher/test_research.py` so terminal output becomes human-readable for each run, then use those signals plus CloudWatch/OpenAI traces to isolate and fix the instability before running a disciplined two-model benchmark.

**Tech Stack:** Python 3.12, FastAPI, OpenAI Agents SDK, LiteLLM, Playwright MCP, AWS Lambda Function URL, CloudWatch Logs, Terraform, `uv`

## Status Update - 2026-07-05

Current verified state before the broader observability work:

- deployed Researcher is Lambda Function URL based, not App Runner
- active runtime model is `openai/gpt-5.4-nano`
- deployment drift was previously confirmed and corrected by redeploying the current image
- latest reproduced deployed runs returned `200 OK` for:
  - `Tesla competitive advantages`
  - `Bitcoin ETF inflows`
- CloudWatch still shows browser instability via captcha, ad/tracker churn, and access-restricted pages
- current primary risk is result quality consistency, not total availability

Validated commands used for this status:

- `uv run backend/researcher/test_research.py "Tesla competitive advantages"`
- `uv run backend/researcher/test_research.py "Bitcoin ETF inflows"`
- `aws logs tail /aws/lambda/alex-researcher --since 5m --region ap-southeast-1`

Operational choice for the next stable benchmark pass:

- bias topics toward large-cap equity and mainstream business themes
- bias browsing toward direct article pages from Investopedia, AP News, and CNN Business
- use Reuters only when a direct article page loads cleanly without captcha

Execution update after this decision:

- prompt/query source bias was implemented in:
  - `backend/researcher/context.py`
  - `backend/researcher/server.py`
- manual deployment was used because `uv run deploy.py` still failed on Terraform AWS provider initialization
- deployed image tag advanced to `deploy-1783240866`

Verification commands run after the source-bias change:

- `curl -m 30 -sS https://u7lbfi3ovnkij7hwffzv7ehqxm0kzvbo.lambda-url.ap-southeast-1.on.aws/health`
- `uv run backend/researcher/test_research.py "Tesla competitive advantages"`
- `uv run backend/researcher/test_research.py "Microsoft cloud revenue growth"`
- `uv run backend/researcher/test_research.py "NVIDIA AI datacenter demand"`
- `aws logs tail /aws/lambda/alex-researcher --since 5m --region ap-southeast-1`

Observed outcome:

- all three deployed tests returned `200 OK`
- Tesla and NVIDIA ended in useful browserless fallback notes
- Microsoft returned a constrained note after failing to verify clean direct article pages
- CloudWatch confirmed the new source preference was actually exercised:
  - Investopedia pages for Tesla
  - CNN article path for NVIDIA
- CloudWatch also confirmed instability still remains in the browser path:
  - `about:blank` churn
  - browser max-turn fallback
  - no reliable clean-article extraction yet

Additional execution update:

- `backend/researcher/test_research.py` now prints a compact `RUN SUMMARY`
- the script now surfaces:
  - active model
  - topic
  - request duration
  - heuristic outcome
  - degraded signal
  - assumed ingest status

Verification after this script change:

- `uv run backend/researcher/test_research.py "Tesla competitive advantages"`
- `uv run backend/researcher/test_research.py "Microsoft cloud revenue growth"`

Observed terminal classification:

- both runs printed `Outcome: success_fallback`
- degraded signals were visible directly in terminal without opening CloudWatch
- no `success_verified` run was observed in this verification pass

Follow-up fix after user validation:

- a real deployed `Tesla competitive advantages` run exposed a false-positive `success_verified`
- root cause was incomplete terminal fallback markers in `test_research.py`
- heuristic was tightened with deployed-output phrases such as:
  - `just a moment`
  - `page not found`
  - `404 / unavailable`
  - `access-restricted`
  - `usable direct article page`
  - `couldn't reliably quote`

Re-verification after the heuristic fix:

- `uv run backend/researcher/test_research.py "Tesla competitive advantages"`
- `uv run backend/researcher/test_research.py "Microsoft cloud revenue growth"`
- `uv run backend/researcher/test_research.py "NVIDIA AI datacenter demand"`

Observed outcome after the fix:

- all three runs printed `Outcome: success_fallback`
- the known false-positive `success_verified` case was removed
- terminal output is now reliable enough to finish `Task 0.5` before moving to server-side observability

Task 1 execution update:

- first server-side structured observability slice is now implemented in `backend/researcher/server.py`
- added:
  - request-scoped `run_id`
  - `phase_start`
  - `phase_end`
  - `request_end`
  - degraded reason detection
  - basic ingest success inference
  - normalized runtime outcome logging

Deployed verification for this slice:

- built and pushed a new image
- updated Lambda directly with AWS CLI
- final verified image tag: `deploy-1783246453`

Verification commands:

- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m py_compile server.py`
- `uv run backend/researcher/test_research.py "Tesla competitive advantages"`
- `aws logs tail /aws/lambda/alex-researcher --since 2m --region ap-southeast-1 | rg "research_run"`

Observed result:

- deployed request still returned `200 OK`
- CloudWatch showed one shared `run_id`
- CloudWatch showed:
  - `phase_start`
  - `phase_end`
  - `request_end`
- `request_end total_duration_ms` was corrected to match the outer request duration rather than double-count nested phases

Task 2 execution update:

- added request-scoped ingest telemetry in `backend/researcher/tools.py`
- added tool-level structured log event:
  - `research_ingest`
- `server.py` now resolves `ingest_success` by preferring tool-level observation over response-text heuristics
- API contract for `/research` remains unchanged

Deployment/verification notes for Task 2:

- `uv run deploy.py` successfully built and pushed image tag `deploy-1783260341`
- Terraform apply failed again with:
  - `Plugin did not respond`
- manual deployment path was used to finish verification:
  - `aws lambda update-function-code --function-name alex-researcher --image-uri 487592470523.dkr.ecr.ap-southeast-1.amazonaws.com/alex-researcher:deploy-1783260341 --region ap-southeast-1`

Verification commands:

- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m py_compile server.py tools.py`
- `uv run backend/researcher/test_research.py "Tesla competitive advantages"`
- `aws logs tail /aws/lambda/alex-researcher --since 2m --region ap-southeast-1 | rg "research_run|research_ingest"`

Observed result for Task 2:

- deployed request returned `200 OK`
- terminal summary still classified the run as:
  - `Outcome: success_fallback`
  - `Degraded Signal: page unavailable`
- CloudWatch now showed exact ingest evidence tied to the same request:
  - `research_ingest run_id=5b463b99-e175-41f1-9191-fb3650c606c5 success=True ... document_id=1dd66a7f-6f56-469e-bd43-8a84dcd6121b`
  - `research_run request_end run_id=5b463b99-e175-41f1-9191-fb3650c606c5 ... ingest_success=True degraded_reason=page_unavailable ...`

Conclusion after Task 2:

- ingest outcome is now explicit enough for server-side failure classification
- `request_end ingest_success` is no longer only a heuristic when the tool actually ran
- plan can move to `Task 4` or return to any remaining observability gaps with a stronger evidence base

## Global Constraints

- Fix bug instability before benchmarking models.
- Do not modify `guides/4_researcher.md` in this phase.
- Keep CloudWatch as the production source of truth.
- Add terminal-friendly observability in `backend/researcher/test_research.py`.
- Benchmark only on deployed Lambda runtime, not local-only runs.
- Compare exactly two models first: `openrouter` `gpt-oss-120b` and `openai/gpt-5.4-nano`.
- Use exactly 5 fixed topics for the first benchmark round.
- Prefer direct article pages from Investopedia, AP News, and CNN Business during the first stable benchmark round.
- Avoid redesigning the `/research` API contract unless strictly required by evidence.

---

## File Structure

### Existing files to modify

- `backend/researcher/server.py`
  - Add run-level and phase-level observability.
  - Normalize outcome classification.
  - Add evidence needed to debug instability before changing behavior.
- `backend/researcher/tools.py`
  - Surface ingest timing/result details clearly enough for classification.
  - Only modify if server-side instrumentation cannot observe ingest outcome cleanly without it.
- `backend/researcher/test_research.py`
  - Print terminal-friendly summaries for each deployed run.
  - Show model, timing, outcome, and degraded/fallback signals.
- `backend/researcher/BUG_AND_FIX.md`
  - Append the verified root cause and fix once the instability bug is actually proven and resolved.

### New files to create

- `backend/researcher/BENCHMARK_RUNBOOK.md`
  - Human-facing instructions for running the benchmark, collecting logs, and comparing the two models.

### Files to inspect during implementation/testing

- `backend/researcher/OBSERVABILITY_AND_BENCHMARK_SPEC.md`
- `backend/researcher/mcp_servers.py`
- `backend/researcher/context.py`
- `terraform/4_researcher/variables.tf`
- `terraform/4_researcher/main.tf`

## Task 1: Add Structured Run and Phase Observability

**Files:**
- Modify: `backend/researcher/server.py`
- Inspect: `backend/researcher/tools.py`, `backend/researcher/mcp_servers.py`
- Test: manual run via `uv run test_research.py`

**Interfaces:**
- Consumes:
  - `run_research_agent(topic: str | None) -> str`
  - `_run_research_query(query: str, model: LitellmModel, *, max_turns: int, use_browser: bool) -> str`
- Produces:
  - Structured log events with fields:
    - `run_id: str`
    - `model: str`
    - `topic: str`
    - `phase: str`
    - `status: str`
    - `duration_ms: int`
    - `outcome: str | None`
    - `ingest_success: bool | None`
    - `error_type: str | None`

- [ ] **Step 1: Add a small observability design note at the top of `server.py` implementation area**

```python
# Observability model for each /research run:
# - one run_id per request
# - one start/end record per major phase
# - one normalized outcome per completed request
# This is used to debug instability before benchmarking models.
```

- [ ] **Step 2: Add helper functions for timing and structured logging**

```python
import time
import uuid
from dataclasses import dataclass, field


@dataclass
class PhaseRecord:
    name: str
    started_at: float
    duration_ms: int | None = None
    status: str = "started"
    error_type: str | None = None


@dataclass
class RunTrace:
    run_id: str
    topic: str
    model: str
    phases: dict[str, PhaseRecord] = field(default_factory=dict)
    outcome: str | None = None
    ingest_success: bool | None = None
    degraded_reason: str | None = None


def _now_ms() -> int:
    return int(time.perf_counter() * 1000)


def _start_phase(trace: RunTrace, phase: str) -> None:
    trace.phases[phase] = PhaseRecord(name=phase, started_at=time.perf_counter())
    logger.info(
        "research_run phase_start run_id=%s model=%s topic=%s phase=%s",
        trace.run_id,
        trace.model,
        trace.topic,
        phase,
    )


def _end_phase(trace: RunTrace, phase: str, *, status: str, error_type: str | None = None) -> None:
    record = trace.phases[phase]
    record.duration_ms = int((time.perf_counter() - record.started_at) * 1000)
    record.status = status
    record.error_type = error_type
    logger.info(
        "research_run phase_end run_id=%s model=%s topic=%s phase=%s status=%s duration_ms=%s error_type=%s",
        trace.run_id,
        trace.model,
        trace.topic,
        phase,
        status,
        record.duration_ms,
        error_type,
    )
```

- [ ] **Step 3: Add a normalized outcome classifier**

```python
def _classify_outcome(*, used_browser: bool, used_fallback: bool, ingest_success: bool, degraded_reason: str | None) -> str:
    if not ingest_success:
        return "failed_ingest"
    if degraded_reason:
        return "success_fallback"
    if used_browser:
        return "success_verified"
    if used_fallback:
        return "success_fallback"
    return "failed_unknown"
```

- [ ] **Step 4: Thread a `RunTrace` through `run_research_agent()`**

```python
async def run_research_agent(topic: str = None) -> tuple[str, RunTrace]:
    normalized_topic = topic or "agent_choice"
    model_name = _get_researcher_model_name()
    trace = RunTrace(
        run_id=str(uuid.uuid4()),
        topic=normalized_topic,
        model=model_name,
    )
    ...
    return response_text, trace
```

- [ ] **Step 5: Instrument each research phase without changing the external behavior yet**

```python
_start_phase(trace, "browser_run")
try:
    response = await _run_research_query(query, model, max_turns=15, use_browser=True)
    _end_phase(trace, "browser_run", status="ok")
except MaxTurnsExceeded:
    _end_phase(trace, "browser_run", status="max_turns", error_type="MaxTurnsExceeded")
    ...
except Exception as exc:
    _end_phase(trace, "browser_run", status="error", error_type=type(exc).__name__)
    raise
```

- [ ] **Step 6: Detect degraded placeholder/fallback output conservatively**

```python
def _detect_degraded_reason(response_text: str) -> str | None:
    lowered = response_text.lower()
    if "placeholder" in lowered:
        return "placeholder_result"
    if "couldn’t complete the browse step reliably" in lowered or "couldn't complete the browse step reliably" in lowered:
        return "browse_step_unreliable"
    if "read-only filesystem" in lowered or "erofs" in lowered:
        return "read_only_filesystem"
    return None
```

- [ ] **Step 7: Log request_end with total duration and normalized outcome**

```python
total_duration_ms = sum(
    phase.duration_ms or 0 for phase in trace.phases.values()
)
trace.degraded_reason = _detect_degraded_reason(response_text)
trace.outcome = _classify_outcome(
    used_browser=True,
    used_fallback=trace.degraded_reason is not None,
    ingest_success=bool(trace.ingest_success),
    degraded_reason=trace.degraded_reason,
)
logger.info(
    "research_run request_end run_id=%s model=%s topic=%s outcome=%s ingest_success=%s degraded_reason=%s total_duration_ms=%s",
    trace.run_id,
    trace.model,
    trace.topic,
    trace.outcome,
    trace.ingest_success,
    trace.degraded_reason,
    total_duration_ms,
)
```

- [ ] **Step 8: Run a single deployed request and verify the new logs exist**

Run: `cd backend/researcher && uv run test_research.py "Tesla competitive advantages"`

Expected:
- Terminal still gets a response.
- CloudWatch now contains `phase_start`, `phase_end`, and `request_end` lines with one `run_id`.

- [ ] **Step 9: Commit**

```bash
git add backend/researcher/server.py
git commit -m "feat: add structured observability for researcher runs"
```

## Task 2: Make Ingest Outcome Explicit Enough to Classify Failures

**Files:**
- Modify: `backend/researcher/tools.py`
- Inspect: `backend/researcher/server.py`
- Test: manual run via `uv run test_research.py`

**Interfaces:**
- Consumes:
  - `ingest_financial_document(topic: str, analysis: str) -> Dict[str, Any]`
- Produces:
  - Ingest result payload that consistently contains:
    - `success: bool`
    - `document_id: str | None`
    - `error: str | None`

- [ ] **Step 1: Confirm the current tool already returns normalized fields**

```python
@function_tool
def ingest_financial_document(topic: str, analysis: str) -> Dict[str, Any]:
    ...
    return {
        "success": True,
        "document_id": result.get("document_id"),
        "message": f"Successfully ingested analysis for {topic}"
    }
```

Run: `sed -n '1,220p' backend/researcher/tools.py`
Expected: verify no schema change is needed before touching code.

- [ ] **Step 2: Only if needed, add a tiny helper to keep ingest result shape stable**

```python
def _normalize_ingest_result(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": bool(result.get("success")),
        "document_id": result.get("document_id"),
        "error": result.get("error"),
        "message": result.get("message"),
    }
```

- [ ] **Step 3: If Step 2 was needed, route the return path through the helper**

```python
        result = ingest_with_retries(document)
        return _normalize_ingest_result(
            {
                "success": True,
                "document_id": result.get("document_id"),
                "message": f"Successfully ingested analysis for {topic}",
            }
        )
```

- [ ] **Step 4: Wire `server.py` to infer ingest_success from the final output evidence only if the tool result is not otherwise exposed**

```python
trace.ingest_success = "successfully ingested" in response_text.lower() if trace.ingest_success is None else trace.ingest_success
```

- [ ] **Step 5: Run a single deployed request and inspect whether failed ingest is now distinguishable from browser degradation**

Run: `cd backend/researcher && uv run test_research.py "Microsoft cloud revenue growth"`

Expected:
- Terminal and logs clearly distinguish `ingest_success=True/False`.

- [ ] **Step 6: Commit**

```bash
git add backend/researcher/tools.py backend/researcher/server.py
git commit -m "feat: normalize ingest outcome for researcher classification"
```

## Task 3: Improve Terminal-Friendly Output in `test_research.py`

**Files:**
- Modify: `backend/researcher/test_research.py`
- Test: manual runs with one and multiple fixed topics

**Interfaces:**
- Consumes:
  - `POST /research` current response body
  - `GET /health` response body
- Produces:
  - Terminal summary showing:
    - `model`
    - `topic`
    - `request_duration_ms`
    - `outcome_guess`
    - `degraded_signal`

- [ ] **Step 1: Add total request timing around the `/research` call**

```python
import time

request_started = time.perf_counter()
response = requests.post(
    research_url,
    json=payload,
    timeout=180,
)
request_duration_ms = int((time.perf_counter() - request_started) * 1000)
```

- [ ] **Step 2: Read the active model from `/health` so terminal logs are tagged correctly**

```python
health_payload = response.json()
active_model = health_payload.get("researcher_model", "unknown")
```

- [ ] **Step 3: Add a local degraded-result detector for console summaries**

```python
def classify_terminal_result(result_text: str) -> tuple[str, str | None]:
    lowered = result_text.lower()
    if "placeholder" in lowered:
        return "success_fallback", "placeholder_result"
    if "read-only filesystem" in lowered or "erofs" in lowered:
        return "success_fallback", "read_only_filesystem"
    if "couldn’t complete the browse step reliably" in lowered or "couldn't complete the browse step reliably" in lowered:
        return "success_fallback", "browse_step_unreliable"
    return "success_verified", None
```

- [ ] **Step 4: Print a compact benchmark-ready summary before the long body**

```python
print("\nRUN SUMMARY")
print("=" * 60)
print(f"Model: {active_model}")
print(f"Topic: {display_topic}")
print(f"Request duration: {request_duration_ms} ms")
print(f"Outcome: {outcome}")
print(f"Degraded signal: {degraded_signal or 'none'}")
print("=" * 60)
```

- [ ] **Step 5: Preserve the full research body below the summary for manual inspection**

```python
print("\nRESEARCH RESULT:")
print("=" * 60)
print(result)
print("=" * 60)
```

- [ ] **Step 6: Run one known-good and one degraded topic to verify readability**

Run:
- `cd backend/researcher && uv run test_research.py "NVIDIA AI chip demand"`
- `cd backend/researcher && uv run test_research.py "Bitcoin ETF inflows"`

Expected:
- Each run prints model + duration + outcome clearly before the full body.

- [ ] **Step 7: Commit**

```bash
git add backend/researcher/test_research.py
git commit -m "feat: add terminal-friendly researcher run summaries"
```

## Task 4: Use the New Observability to Prove the Current Instability Root Cause

**Files:**
- Modify: `backend/researcher/BUG_AND_FIX.md`
- Inspect: `backend/researcher/server.py`, `backend/researcher/mcp_servers.py`
- Evidence source: terminal output, CloudWatch logs, OpenAI traces

**Interfaces:**
- Consumes:
  - Structured `research_run` log lines
  - Terminal summaries from `test_research.py`
- Produces:
  - A verified instability diagnosis with exact failure signatures and impacted phases

- [ ] **Step 1: Run the fixed 5-topic set once on the currently deployed model to gather evidence**

Run:
```bash
cd backend/researcher
uv run test_research.py "Tesla competitive advantages"
uv run test_research.py "Microsoft cloud revenue growth"
uv run test_research.py "NVIDIA AI datacenter demand"
uv run test_research.py "Amazon advertising growth"
uv run test_research.py "Apple services revenue growth"
```

Expected:
- At least one run pattern should reveal whether degradation clusters around browser, fallback, or ingest.

- [ ] **Step 2: Pull the matching CloudWatch logs using the visible run metadata**

Run:
```bash
aws logs tail /aws/lambda/alex-researcher --since 10m --region ap-southeast-1
```

Expected:
- Lines containing the same model/topic window and phase timings from the terminal runs.

- [ ] **Step 3: Create a short evidence table in `BUG_AND_FIX.md`**

```md
| Topic | Model | Outcome | Degraded Signal | Failing Phase | Evidence |
|-------|-------|---------|-----------------|--------------|----------|
| Tesla competitive advantages | openai/gpt-5.4-nano | success_fallback | read_only_filesystem | browser_run | CloudWatch + terminal |
```

- [ ] **Step 4: State a single root-cause hypothesis based on the evidence**

```md
Hypothesis: `browser_snapshot` in Lambda is intermittently attempting a write on a non-writable path, which causes degraded browser runs and pushes the agent into fallback or placeholder output.
```

- [ ] **Step 5: Commit the evidence-only update before implementing a fix**

```bash
git add backend/researcher/BUG_AND_FIX.md
git commit -m "docs: record researcher instability evidence before fix"
```

## Task 5: Implement the Minimal Fix for the Proven Instability

**Files:**
- Modify: `backend/researcher/mcp_servers.py`
- Modify: `backend/researcher/server.py`
- Test: repeated deployed runs on the same topic set

**Interfaces:**
- Consumes:
  - Verified instability hypothesis from Task 4
- Produces:
  - A narrower, evidence-driven mitigation for the browser/file-system failure mode

- [ ] **Step 1: Write down the exact failure to target before changing code**

```md
Target failure to fix: browser-related degraded runs caused by write attempts outside `/tmp`, resulting in `EROFS` / read-only filesystem errors and placeholder output.
```

- [ ] **Step 2: Apply the smallest config/code change that forces all writable browser artifacts into `/tmp`**

```python
params = {
    "command": "playwright-mcp",
    "args": args,
    "env": {
        "DEBUG": "pw:api,pw:browser*",
        "HOME": "/tmp",
        "TMPDIR": "/tmp",
        "XDG_CACHE_HOME": "/tmp/.cache",
    },
}
```

- [ ] **Step 3: If needed, add a guard log proving the writable paths being used**

```python
logger.info(
    "Playwright writable env HOME=%s TMPDIR=%s XDG_CACHE_HOME=%s",
    params["env"].get("HOME"),
    params["env"].get("TMPDIR"),
    params["env"].get("XDG_CACHE_HOME"),
)
```

- [ ] **Step 4: Re-run the same topic set on the currently deployed model**

Run:
```bash
cd backend/researcher
uv run test_research.py "Tesla competitive advantages"
uv run test_research.py "Microsoft cloud revenue growth"
uv run test_research.py "NVIDIA AI chip demand"
uv run test_research.py "Oil price outlook"
uv run test_research.py "Bitcoin ETF inflows"
```

Expected:
- Fallback/degraded rate should drop, or the failure mode should become narrower and more explicit.

- [ ] **Step 5: Update `BUG_AND_FIX.md` with the confirmed fix outcome**

```md
Result after fix:
- `EROFS` no longer appears in browser-related degraded runs
- placeholder rate dropped from X/5 to Y/5
- remaining failures are now concentrated in ...
```

- [ ] **Step 6: Commit**

```bash
git add backend/researcher/mcp_servers.py backend/researcher/server.py backend/researcher/BUG_AND_FIX.md
git commit -m "fix: reduce researcher browser instability in lambda runtime"
```

## Task 6: Write the Benchmark Runbook

**Files:**
- Create: `backend/researcher/BENCHMARK_RUNBOOK.md`
- Inspect: `backend/researcher/OBSERVABILITY_AND_BENCHMARK_SPEC.md`

**Interfaces:**
- Consumes:
  - Finalized observability fields and benchmark topic list
- Produces:
  - Human-readable benchmark procedure that anyone can run after deployment

- [ ] **Step 1: Create the runbook with the fixed 5-topic benchmark set**

```md
# Researcher Benchmark Runbook

## Fixed Topics
1. Tesla competitive advantages
2. Microsoft cloud revenue growth
3. NVIDIA AI datacenter demand
4. Amazon advertising growth
5. Apple services revenue growth
```

- [ ] **Step 2: Document the exact model-by-model workflow**

```md
## Procedure
1. Set `RESEARCHER_MODEL` for model A.
2. Deploy with `uv run deploy.py`.
3. Run the 5 fixed topics.
4. Save terminal output and matching CloudWatch logs.
5. Repeat for model B.
```

- [ ] **Step 3: Add the comparison table template**

```md
| Model | Topic | Request Duration (ms) | Outcome | Degraded Signal | Ingest Success |
|------|------|------------------------|---------|-----------------|----------------|
```

- [ ] **Step 4: Add instructions for where to look when a run degrades**

```md
If a run is `success_fallback` or placeholder-like:
- check terminal summary first
- then inspect CloudWatch by model/topic/time window
- then compare with OpenAI traces for the same run
```

- [ ] **Step 5: Commit**

```bash
git add backend/researcher/BENCHMARK_RUNBOOK.md
git commit -m "docs: add researcher benchmark runbook"
```

## Task 7: Run the Production Benchmark for `gpt-5.4-nano`

**Files:**
- Modify: none required unless evidence reveals defects
- Test: deployed Lambda researcher

**Interfaces:**
- Consumes:
  - `RESEARCHER_MODEL=openai/gpt-5.4-nano`
  - Fixed topic set
- Produces:
  - First benchmark record set for `gpt-5.4-nano`

- [ ] **Step 1: Ensure `RESEARCHER_MODEL` is set to `openai/gpt-5.4-nano`**

Run:
```bash
cd terraform/4_researcher
sed -n '1,220p' terraform.tfvars
sed -n '1,220p' researcher.auto.tfvars.json
```

Expected:
- Confirm deployment inputs before redeploying.

- [ ] **Step 2: Deploy the model**

Run:
```bash
cd backend/researcher
uv run deploy.py
```

Expected:
- Lambda updates successfully and prints the Function URL.

- [ ] **Step 3: Run the 5 fixed topics and save outputs**

Run:
```bash
cd backend/researcher
uv run test_research.py "Tesla competitive advantages"
uv run test_research.py "Microsoft cloud revenue growth"
uv run test_research.py "NVIDIA AI datacenter demand"
uv run test_research.py "Amazon advertising growth"
uv run test_research.py "Apple services revenue growth"
```

Expected:
- Five terminal summaries tagged with `openai/gpt-5.4-nano`.

- [ ] **Step 4: Commit notes if code changed during evidence gathering**

```bash
git status
```

Expected:
- Usually no code changes here; if none, skip commit.

## Task 8: Run the Production Benchmark for `gpt-oss-120b` via OpenRouter

**Files:**
- Modify: configuration only if needed for deployment input
- Test: deployed Lambda researcher

**Interfaces:**
- Consumes:
  - `RESEARCHER_MODEL` value for the OpenRouter-backed `gpt-oss-120b`
  - Same fixed topic set
- Produces:
  - Second benchmark record set for `gpt-oss-120b`

- [ ] **Step 1: Set the model configuration for OpenRouter-backed `gpt-oss-120b`**

```bash
# Example only — use the exact final model string agreed in config
RESEARCHER_MODEL=openrouter/openai/gpt-oss-120b
```

- [ ] **Step 2: Deploy the model**

Run:
```bash
cd backend/researcher
uv run deploy.py
```

Expected:
- Lambda updates successfully and prints the Function URL.

- [ ] **Step 3: Run the same 5 fixed topics**

Run:
```bash
cd backend/researcher
uv run test_research.py "Tesla competitive advantages"
uv run test_research.py "Microsoft cloud revenue growth"
uv run test_research.py "NVIDIA AI datacenter demand"
uv run test_research.py "Amazon advertising growth"
uv run test_research.py "Apple services revenue growth"
```

Expected:
- Five terminal summaries tagged with the OpenRouter-backed model string.

## Task 9: Compare the Two Models and Record Findings

**Files:**
- Modify: `backend/researcher/BENCHMARK_RUNBOOK.md` or add a short findings section there
- Inspect: terminal outputs, CloudWatch logs, OpenAI traces

**Interfaces:**
- Consumes:
  - Two complete 5-topic benchmark runs
- Produces:
  - Comparison summary of speed, reliability, and fallback behavior

- [ ] **Step 1: Fill the comparison table**

```md
| Model | Topic | Request Duration (ms) | Outcome | Degraded Signal | Ingest Success |
|------|------|------------------------|---------|-----------------|----------------|
```

- [ ] **Step 2: Add a short findings summary**

```md
## Findings
- Faster model:
- More stable model:
- Lower fallback rate:
- Lower degraded/placeholder rate:
- Recommended default model for current Lambda runtime:
```

- [ ] **Step 3: Commit the benchmark documentation**

```bash
git add backend/researcher/BENCHMARK_RUNBOOK.md backend/researcher/BUG_AND_FIX.md
git commit -m "docs: record researcher benchmark findings"
```

## Self-Review

### Spec coverage

- Fix instability before benchmark: covered by Tasks 1-5.
- Add service observability: covered by Task 1.
- Add terminal-friendly output: covered by Task 3.
- Keep guide unchanged: no task modifies `guides/4_researcher.md`.
- Benchmark two deployed models with 5 fixed topics: covered by Tasks 6-9.

### Placeholder scan

- No `TODO`, `TBD`, or “similar to previous task” placeholders remain.
- OpenRouter model string is intentionally called out as “use the exact final model string agreed in config” because the exact provider path must match deployment reality; validate that string before Task 8 execution.

### Type consistency

- `run_research_agent()` changes from returning `str` to `tuple[str, RunTrace]`; all call sites in `server.py` must be updated consistently.
- Normalized outcome strings stay fixed across Tasks 1, 3, 4, and 9.
