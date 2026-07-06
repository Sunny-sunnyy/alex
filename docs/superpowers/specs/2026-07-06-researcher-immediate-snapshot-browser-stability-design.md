# Researcher Immediate-Snapshot Browser Stability — Design

Date: 2026-07-06

## Context

Researcher (Guide 4 Step 4) is pragmatically passing: `200 OK`, usable notes, ingest works. But browser-based `success_verified` has never been proven stable on Lambda headless runtime.

### Root Cause (proven by CloudWatch evidence)

The browser successfully navigates to article pages (Investopedia, CNN, AP News), but JavaScript on those pages has time to redirect the page into `about:blank`, `about:srcdoc`, `client-storage` (Optimizely), or ad-tech paths BEFORE the agent calls `browser_snapshot`. The agent then sees blank/noise pages and reports "page not found" or "page unavailable."

This is NOT a browser startup failure, NOT a `MaxTurnsExceeded` loop, and NOT an `EROFS` filesystem issue.

### Goal

Shorten the time window between `browser_navigate` and `browser_snapshot` to near-zero, so content is captured before JavaScript drift occurs.

## Design

### 1. Prompt Constraint: Snapshot Immediately After Navigate

**File:** `backend/researcher/context.py`

Add a hard constraint to the agent's browsing instructions:

```
CRITICAL RULE: After calling browser_navigate to any article URL, your
VERY NEXT action MUST be browser_snapshot. Do NOT click, scroll, type,
or take any other action between navigate and snapshot. The page content
may redirect or blank out quickly — capture it immediately.
```

This applies to all three preferred sources: Investopedia, AP News, CNN Business.

### 2. Three-Source Limit with Explicit Fail

**File:** `backend/researcher/context.py`

Agent is allowed up to 3 direct-article attempts (one per preferred source). After each navigate, it must snapshot immediately. If the snapshot shows `about:blank`, noise, redirect, or non-article content:

- Move to the next preferred source
- After 3 sources all fail: STOP browsing, report failure explicitly
- Do NOT keep browsing or trying additional URLs

The existing verified-web-only gate in `server.py` stays unchanged — no fallback note ingestion.

### 3. Runtime Snapshot URL Logging

**File:** `backend/researcher/server.py`

Add one observability field during `browser_run` phase:
- `snapshot_page_url` — logs the actual page URL at the moment `browser_snapshot` returned content

Add new `browser_run` status values:
- `article_captured` — snapshot returned clean article body from a real article URL
- `page_drifted` — snapshot captured `about:blank`, `about:srcdoc`, or client-storage page
- `max_turns` — unchanged, MaxTurnsExceeded
- `error` — unchanged, unexpected exception

### How to detect article_captured vs page_drifted

After `browser_run` completes, inspect the response text for drift signatures:
- `about:blank`, `about:srcdoc`, `optimizely`, `client_storage`, `doubleclick`, `googlesyndication` → `page_drifted`
- Otherwise, if response contains substantive financial analysis → `article_captured`

This detection runs in `_end_phase` logic within `server.py`, not in the agent prompt.

## Behavior Contract (unchanged)

- `/research` still requires verified web content
- Fallback notes still NOT ingested into S3 Vectors
- `500` returned when no verified content obtained
- `MaxTurnsExceeded` recovery path preserved

## Verification Plan

After deployment:

1. Run 5-topic benchmark:
   - `Tesla competitive advantages`
   - `Microsoft cloud revenue growth`
   - `NVIDIA AI datacenter demand`
   - `Amazon advertising growth`
   - `Apple services revenue growth`

2. Inspect CloudWatch for `snapshot_page_url` and `browser_run status`
3. Success criteria: at least 1-2/5 runs achieve `article_captured`
4. If 0/5 still drift → evidence that the issue requires Playwright-level interception (blocking redirects at the browser engine level), which is out of scope for this pass

## Files Modified

- `backend/researcher/context.py` — prompt constraint + 3-source limit
- `backend/researcher/server.py` — `snapshot_page_url` log + status classification
- `backend/researcher/README.md` — update current state (already dirty)

## Files NOT Modified

- `backend/researcher/mcp_servers.py` — no Playwright config changes
- `backend/researcher/tools.py` — no ingest logic changes
- `backend/researcher/test_research.py` — existing fallback markers should still work
- `terraform/4_researcher/` — no infrastructure changes
