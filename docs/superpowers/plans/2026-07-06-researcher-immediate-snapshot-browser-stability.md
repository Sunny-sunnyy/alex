# Researcher Immediate-Snapshot Browser Stability — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Shorten the time window between browser_navigate and browser_snapshot to near-zero so article content is captured before JavaScript redirects drift the page into about:blank, about:srcdoc, or client-storage paths.

**Architecture:** Add a prompt-level constraint in context.py forcing the agent to snapshot immediately after any navigate. Add drift-detection logic and snapshot_page_url logging in server.py so CloudWatch shows whether snapshots captured real article pages or drifted content.

**Tech Stack:** Python 3.12, FastAPI, OpenAI Agents SDK, Playwright MCP, AWS Lambda Function URL, CloudWatch Logs

## Global Constraints

- Do not modify `guides/4_researcher.md`.
- Do not modify `mcp_servers.py` (no Playwright config changes).
- Do not modify `tools.py` (no ingest logic changes).
- Do not modify `test_research.py` unless existing fallback markers break.
- Keep verified-web-only gate unchanged — fallback notes must NOT be ingested.
- Keep the `/research` API contract unchanged.
- Follow existing code style: match surrounding patterns, no unrelated refactoring.

---

## File Structure

### Files to modify

- `backend/researcher/context.py` — Add immediate-snapshot prompt constraint, 3-source limit
- `backend/researcher/server.py` — Add drift detection helper, snapshot_page_url logging, article_captured/page_drifted status

### Files to inspect during verification

- `backend/researcher/test_research.py` — Verify existing fallback markers still work

---

### Task 1: Add Immediate-Snapshot Constraint and 3-Source Limit to Agent Prompt

**Files:**
- Modify: `backend/researcher/context.py`

**Interfaces:**
- Consumes: nothing new
- Produces: updated `get_agent_instructions()` return value with immediate-snapshot rule and 3-source limit

The prompt currently says "Use browser_snapshot only after confirming you are still on a real article page." This is too loose — it lets the agent take other actions between navigate and snapshot, which gives JavaScript time to redirect.

We replace that with a harder constraint and add an explicit 3-source limit.

- [ ] **Step 1: Replace the browser_snapshot rule and add 3-source limit**

Open `backend/researcher/context.py`. Find this block in `get_agent_instructions()`:

```python
       - Use browser_snapshot only after confirming you are still on a real article page
```

Replace it with:

```python
       - CRITICAL SNAPSHOT RULE: After calling browser_navigate to any article URL,
         your VERY NEXT action MUST be browser_snapshot. Do NOT click, scroll,
         type, or take any other action between navigate and snapshot. The page
         content may redirect or blank out quickly — capture it immediately.
```

Then find this block:

```python
       - If both allowed direct article attempts fail, stop and report that verified web content was not obtained
```

Replace it with:

```python
       - You may attempt up to 3 direct article sources (Investopedia -> AP News -> CNN Business)
       - After each navigate, snapshot immediately (see CRITICAL SNAPSHOT RULE above)
       - If a snapshot shows about:blank, about:srcdoc, client-storage, or non-article content, move to the next source
       - If all 3 sources fail, STOP browsing and report that verified web content was not obtained
```

- [ ] **Step 2: Verify syntax**

Run: `cd backend/researcher && UV_CACHE_DIR=/tmp/uv-cache uv run python -m py_compile context.py`

Expected: no output (success).

- [ ] **Step 3: Commit**

```bash
git add backend/researcher/context.py
git commit -m "feat: add immediate-snapshot prompt constraint and 3-source limit"
```

---

### Task 2: Add Drift Detection and Snapshot URL Logging in Server Runtime

**Files:**
- Modify: `backend/researcher/server.py`

**Interfaces:**
- Consumes: response text from `_run_research_query()` (browser_run phase)
- Produces: `snapshot_page_url` in CloudWatch logs, `article_captured`/`page_drifted` phase status

The runtime currently sets `browser_run` status to `"ok"` whenever the agent finishes without an exception. That is not precise enough — it hides the fact that the snapshot may have captured drifted content.

We add two things:
1. A helper to detect drift signatures in the response text
2. Improved status classification: `article_captured` vs `page_drifted` vs `max_turns` vs `error`

- [ ] **Step 1: Add `_detect_drifted_snapshot()` helper**

Open `backend/researcher/server.py`. Add this function after `_detect_degraded_reason()` (around line 202):

```python
def _detect_drifted_snapshot(response_text: str) -> bool | None:
    """Return True if response suggests the snapshot captured a drifted page.

    Drift signatures include about:blank, about:srcdoc, client-storage
    (Optimizely), and ad-tech iframe paths.  Returns None when the
    response does not contain any clear article-content evidence either
    way (inconclusive).
    """
    lowered = response_text.lower()
    drift_markers = [
        "about:blank",
        "about:srcdoc",
        "client-storage",
        "client_storage",
        "optimizely",
        "doubleclick",
        "googlesyndication",
    ]
    if any(marker in lowered for marker in drift_markers):
        return True
    return None
```

- [ ] **Step 2: Add `_extract_snapshot_url()` helper**

Add this function right after `_detect_drifted_snapshot()`:

```python
def _extract_snapshot_url(response_text: str) -> str | None:
    """Try to extract the article URL the agent claims it used.

    The agent is prompted to include 'Source URL: https://...' in its
    output when it actually used a clean article page.
    """
    lowered = response_text.lower()
    marker = "source url:"
    idx = lowered.find(marker)
    if idx == -1:
        return None
    remainder = response_text[idx + len(marker):].strip()
    url_end = remainder.find("\n")
    if url_end == -1:
        url_end = len(remainder)
    url = remainder[:url_end].strip()
    if url.startswith("http"):
        return url
    return None
```

- [ ] **Step 3: Update `browser_run` phase-end logic to classify article_captured vs page_drifted**

Find the `browser_run` success path in `run_research_agent()`. Currently it's:

```python
            _end_phase(trace_state, "browser_run", status="ok")
```

Replace that line (line 439) with drift-aware classification:

```python
            snapshot_url = _extract_snapshot_url(response_text)
            drifted = _detect_drifted_snapshot(response_text)
            if drifted is True:
                _end_phase(trace_state, "browser_run", status="page_drifted")
            elif snapshot_url:
                _end_phase(trace_state, "browser_run", status="article_captured")
            else:
                _end_phase(trace_state, "browser_run", status="ok")
```

Also add a `snapshot_page_url` field to the `phase_end` log for `browser_run`. Modify the `_end_phase` call or add an explicit log line. The cleanest approach: log `snapshot_page_url` as a separate info line after `_end_phase` when we have a URL. Add right after the three-way `_end_phase` block:

```python
            if snapshot_url:
                logger.info(
                    "research_run snapshot_page_url run_id=%s url=%s",
                    trace_state.run_id,
                    snapshot_url,
                )
```

- [ ] **Step 4: Apply same drift classification to `constrained_browser_run`**

Find the `constrained_browser_run` success path (around line 471):

```python
                _end_phase(trace_state, "constrained_browser_run", status="ok")
```

Replace with:

```python
                constrained_snapshot_url = _extract_snapshot_url(response_text)
                constrained_drifted = _detect_drifted_snapshot(response_text)
                if constrained_drifted is True:
                    _end_phase(trace_state, "constrained_browser_run", status="page_drifted")
                elif constrained_snapshot_url:
                    _end_phase(trace_state, "constrained_browser_run", status="article_captured")
                else:
                    _end_phase(trace_state, "constrained_browser_run", status="ok")
                if constrained_snapshot_url:
                    logger.info(
                        "research_run snapshot_page_url run_id=%s url=%s",
                        trace_state.run_id,
                        constrained_snapshot_url,
                    )
```

- [ ] **Step 5: Verify syntax**

Run: `cd backend/researcher && UV_CACHE_DIR=/tmp/uv-cache uv run python -m py_compile server.py`

Expected: no output (success).

- [ ] **Step 6: Commit**

```bash
git add backend/researcher/server.py
git commit -m "feat: add snapshot drift detection and page_url logging for browser phases"
```

---

### Task 3: Deploy and Verify on Live Lambda

**Files:**
- None modified (deploy only)
- Inspect: CloudWatch logs after benchmark

**Interfaces:**
- Consumes: deployed Lambda researcher
- Produces: benchmark evidence with `article_captured` / `page_drifted` status

- [ ] **Step 1: Deploy**

Run: `cd backend/researcher && uv run deploy.py`

Expected: Docker build succeeds, ECR push succeeds, Terraform apply succeeds, Lambda updates. If Terraform fails with "Plugin did not respond", fall back to:
```bash
aws lambda update-function-code --function-name alex-researcher --image-uri <ecr-image-uri> --region ap-southeast-1
```

- [ ] **Step 2: Verify health**

Run: `curl -m 30 -sS <researcher_url>/health`

Expected: `200 OK`, `researcher_model: openai/gpt-5.4-nano`.

- [ ] **Step 3: Run 5-topic benchmark**

```bash
cd backend/researcher
uv run test_research.py "Tesla competitive advantages"
uv run test_research.py "Microsoft cloud revenue growth"
uv run test_research.py "NVIDIA AI datacenter demand"
uv run test_research.py "Amazon advertising growth"
uv run test_research.py "Apple services revenue growth"
```

Expected: each run prints `RUN SUMMARY`. Record outcomes.

- [ ] **Step 4: Inspect CloudWatch for drift evidence**

Run: `aws logs tail /aws/lambda/alex-researcher --since 10m --region ap-southeast-1 | rg "snapshot_page_url|browser_run.*status=|constrained_browser_run.*status="`

Expected: see `snapshot_page_url` values and `article_captured` or `page_drifted` status labels.

- [ ] **Step 5: Evaluate success criteria**

Count:
- How many runs show `article_captured`
- How many runs show `page_drifted`

Success: at least 1-2/5 `article_captured`.

If 0/5 `article_captured`: the issue is deeper than prompt timing — JavaScript redirects fire before Playwright can snapshot regardless of agent behavior. The next step would be Playwright-level route interception (out of scope for this pass).

- [ ] **Step 6: Commit verification notes (if any)**

If code changes are needed based on evidence, commit them. Otherwise document findings in `BUG_AND_FIX.md`.

```bash
git add backend/researcher/BUG_AND_FIX.md
git commit -m "docs: record immediate-snapshot verification results"
```

---

### Task 4: Update README to Reflect New State

**Files:**
- Modify: `backend/researcher/README.md` (already dirty)

**Interfaces:**
- Consumes: verified state after Task 3
- Produces: updated README with immediate-snapshot behavior documented

- [ ] **Step 1: Update the "Trạng thái thực tế hiện tại" section**

Add a bullet noting the immediate-snapshot constraint is now active:

```markdown
- prompt đã được siết thêm `immediate-snapshot` constraint để giảm drift window
- `browser_run` status giờ phân loại `article_captured` / `page_drifted` thay vì chỉ `ok`
- có `snapshot_page_url` log trong CloudWatch để truy vết URL thực tế khi snapshot
```

- [ ] **Step 2: Commit**

```bash
git add backend/researcher/README.md
git commit -m "docs: update researcher README for immediate-snapshot behavior"
```

---

## Self-Review

### Spec coverage

- Prompt constraint (snapshot immediately after navigate): covered by Task 1.
- 3-source limit with explicit fail: covered by Task 1.
- Drift detection (article_captured vs page_drifted): covered by Task 2.
- snapshot_page_url logging: covered by Task 2.
- No changes to MCP, tools, test_research: verified by file list.
- verified-web-only gate unchanged: verified by file list (no tools.py changes).

### Placeholder scan

- No "TBD", "TODO", or incomplete code blocks.
- All code blocks are exact, copyable implementations.
- All commands have expected output.

### Type consistency

- `_detect_drifted_snapshot(response_text: str) -> bool | None` — consistent across all call sites.
- `_extract_snapshot_url(response_text: str) -> str | None` — consistent across all call sites.
- `snapshot_url` / `constrained_snapshot_url` variables used in the correct scopes.
- `article_captured` and `page_drifted` status strings match between `_end_phase` calls and verification steps.
