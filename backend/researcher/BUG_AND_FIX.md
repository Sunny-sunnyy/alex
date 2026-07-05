# Alex Researcher: Incident Notes and Current State

This file records what happened while debugging `backend/researcher` during Guide 4, what was changed, why it was changed, how it was deployed, and what is still true about the current system.

The goal of this document is continuity: if this repository is reopened in a new session, this file should be enough to quickly reload the relevant context.

## Scope

This note is specifically about the Researcher service in:

- `backend/researcher`
- `terraform/4_researcher`

At the time of this incident:

- the project was following the **Lambda Function URL** implementation, not App Runner;
- the Researcher model in use was **`openai/gpt-5.4-nano`**;
- Bedrock Nova was not available to the student because of access restrictions.

## User Context at the Time

The student was at:

- `guides/4_researcher.md`
- Step 4: `Test the Complete System`

The failing command was:

```bash
uv run test_research.py
```

Observed error:

```text
500 Server Error: Internal Server Error for url: https://...lambda-url.../research
Error details: {'detail': 'Max turns (15) exceeded'}
```

The student also reported that OpenAI traces were still appearing, which was expected because the service still used OpenAI Agents SDK tracing with `OPENAI_API_KEY`.

## Important Architecture Reality

There is a mismatch between the course guide and the repository implementation:

- `guides/4_researcher.md` still describes App Runner in many places.
- the actual implementation in this repository uses:
  - **Lambda container image**
  - **Lambda Function URL**
  - **ECR**

The key infrastructure file reflecting reality is:

- `terraform/4_researcher/main.tf`

The key deploy script reflecting reality is:

- `backend/researcher/deploy.py`

This mismatch matters during debugging because some guide expectations do not match the current runtime behavior.

## What We Observed First

The first health check was successful:

- `/health` returned `200 OK`

That proved:

- the Function URL existed;
- the Lambda container booted successfully;
- FastAPI was reachable.

So the problem was not:

- missing Lambda URL;
- missing function deployment;
- basic FastAPI startup failure.

The failure happened only when calling:

- `POST /research`

## Root Cause Investigation

### Step 1: Read the Researcher code

The initial behavior in `backend/researcher/server.py` was:

- build a query from either:
  - `DEFAULT_RESEARCH_PROMPT`, or
  - `Research this investment topic: {topic}`
- create a Playwright MCP server;
- create an `Agent` with:
  - `gpt-5.4-nano`
  - `ingest_financial_document`
  - Playwright MCP server
- run:

```python
result = await Runner.run(
    agent,
    input=query,
    max_turns=15,
)
```

That meant any looping behavior in tool usage would terminate with:

- `MaxTurnsExceeded`

### Step 2: Confirm with CloudWatch logs

CloudWatch logs for:

- `/aws/lambda/alex-researcher`

showed that the service was not failing in model initialization or ingest setup. Instead, it was getting trapped in repeated MCP browsing/tool activity.

### First proven loop pattern

In the first failing run, the browser went to Yahoo Finance and then drifted into ad/tracker pages such as:

- Yahoo ad/tracker pages
- `doubleclick`
- `googlesyndication`
- blank tabs / `about:blank`

This caused repeated `browserBackend.callTool` activity until the agent hit:

- `Max turns (15) exceeded`

### Second proven loop pattern

After the first prompt-tightening fix, Yahoo was avoided, but Reuters and MarketWatch were still problematic in Lambda headless runtime.

The logs then showed pages redirecting into:

- `geo.captcha-delivery.com`
- Reuters captcha/interstitial pages
- MarketWatch noisy/ad-heavy navigation

This proved a more specific root cause:

## Proven Root Cause

The Researcher was not failing because of Lambda Function URL, FastAPI, OpenAI tracing, or ingest configuration.

It was failing because:

1. the browser-based research path depended on external news/finance sites;
2. inside Lambda headless runtime, those sites often redirected to:
   - trackers,
   - ad pages,
   - captchas,
   - consent/interstitial pages;
3. the agent kept using MCP browser tools trying to recover;
4. the run exhausted `max_turns=15`;
5. FastAPI then returned:

```text
500 Internal Server Error
detail: Max turns (15) exceeded
```

This was demonstrated by direct evidence in CloudWatch logs, not by guesswork.

## What Was Not the Root Cause

The following were investigated and ruled out as the primary issue:

- Lambda Function URL misconfiguration
- missing `/health` endpoint
- basic container boot failure
- missing OpenAI trace configuration
- missing `ALEX_API_ENDPOINT`
- missing `ALEX_API_KEY`
- basic `gpt-5.4-nano` model invocation failure

Later verification also showed that ingest worked once a result was actually produced.

## Code Changes Made

### Files changed

The following code files were changed:

- `backend/researcher/context.py`
- `backend/researcher/server.py`

No other code files in `backend/researcher` were modified during the fix.

### Folder/file added for documentation

This file was added:

- `backend/researcher/README.md`

## Detailed Changes vs Original Code

### 1. Prompt hardening in `context.py`

Original idea:

- browse Yahoo Finance or MarketWatch;
- use 1-2 pages;
- be concise.

Problem:

- those sites were too noisy in Lambda headless runtime;
- the agent could be dragged into trackers/captcha/interstitial flows.

Change made:

- updated instructions to prefer cleaner sources first:
  - Reuters
  - AP News
  - direct MarketWatch article pages
- explicitly told the agent to avoid:
  - finance homepages when noisy
  - ad links
  - trackers
  - consent pages
  - blank tabs
- instructed the agent to stop and switch to a cleaner source if redirections became noisy.

Reason:

- reduce the chance of MCP browser tool loops before they start.

### 2. Query builder extracted in `server.py`

Original behavior:

- query construction was inline and minimal.

Change made:

- added `_build_research_query(topic, constrained=False)`

This function now supports:

- the normal default query;
- a narrower constrained fallback query;
- topic-specific or topic-free execution.

Reason:

- centralize query generation;
- enable staged fallback logic without duplicating ad hoc strings.

### 3. Browser-aware runner extracted in `server.py`

Original behavior:

- one path only:
  - always create Playwright MCP server,
  - always run in browser mode.

Change made:

- added `_run_research_query(...)`
- this runner supports:
  - `use_browser=True`
  - `use_browser=False`

In browser mode:

- agent is created with:
  - `tools=[ingest_financial_document]`
  - `mcp_servers=[playwright_mcp]`

In browserless mode:

- agent is created with:
  - `tools=[ingest_financial_document]`
  - no MCP server

Reason:

- allow graceful degradation instead of hard failure when browser research becomes unreliable.

### 4. Added `MaxTurnsExceeded` recovery logic

Original behavior:

- if `Runner.run(..., max_turns=15)` exceeded the limit, the exception propagated;
- FastAPI returned `500`.

Change made:

- imported:

```python
from agents.exceptions import MaxTurnsExceeded
```

- wrapped the browser run in recovery logic.

New logic:

1. try normal browser-based research
2. if it exceeds max turns:
   - retry with a more constrained browser query
3. if that also exceeds max turns:
   - switch to browserless fallback

Reason:

- avoid returning `500` when the browser layer is the unreliable part.

### 5. Added browserless fallback query

New function:

- `_build_browserless_fallback_query(topic)`

Behavior:

- tells the model to create a short note from general knowledge;
- explicitly instructs:
  - do not browse the web;
  - keep output short;
  - call `ingest_financial_document` immediately.

Reason:

- if browsing is blocked by captcha/interstitial behavior, the system should still produce a useful note and store it instead of failing the entire request.

### 6. Runtime behavior after the final change

Current staged execution:

1. normal browser-based research
2. constrained browser-based research
3. browserless fallback note

This means the endpoint prioritizes real browsing when possible, but no longer depends on it for success.

## Final Effective Behavior

After the final fix, the following happened on test:

1. `/health` succeeded
2. `/research` started in browser mode
3. browser mode still encountered Reuters captcha/interstitial behavior
4. constrained browser mode also exceeded max turns
5. the new browserless fallback activated
6. the endpoint returned `200 OK`
7. the note was ingested into the vector store successfully

The successful returned result looked like:

- a concise high-level investment note
- in the verified test run, the note was about `NVDA`

## Verification Performed

### Verification 1: Researcher endpoint

Command:

```bash
uv run test_research.py
```

Result after fix:

- success
- `200 OK`
- returned a research note
- no `Max turns (15) exceeded` in the HTTP response

### Verification 2: CloudWatch logs

CloudWatch logs showed:

- browser path still encountered problematic site behavior
- then the warning:

```text
Browser-based fallback also exceeded max turns; retrying without browser access.
```

- final result:

```text
"POST /research HTTP/1.1" 200 OK
```

This confirmed the recovery path was actually exercised in production runtime.

### Verification 3: Vector store ingest

Command:

```bash
cd ../ingest
uv run test_search_s3vectors.py
```

Result:

- the vector store contained the newly created note;
- semantic search returned the ingested content.

This confirmed:

- the fix was not only returning a response;
- it was also successfully persisting the result into the knowledge base.

## Deployment Notes

### Important infrastructure problem encountered

During deployment, `terraform/4_researcher` repeatedly failed with AWS provider/plugin errors such as:

- `Plugin did not respond`
- `Failed to load plugin schemas`

This was a separate infrastructure issue and not the application bug itself.

Because of that, the final deploy path used AWS CLI directly for the Lambda image update.

### What was deployed

The Researcher container image was rebuilt and pushed to ECR manually.

Then the Lambda image was updated directly with:

- `aws lambda update-function-code --function-name alex-researcher --image-uri ...`

This means:

- the running Lambda is updated and working;
- but `terraform/4_researcher` may still have drift or unresolved provider issues.

## Current Known State

### Working

- `backend/researcher` is working through Lambda Function URL
- `gpt-5.4-nano` remains the active researcher model
- `/health` works
- `/research` works
- result ingestion into S3 vectors works

### Still imperfect

- browser-based research is still unreliable in Lambda because Reuters/MarketWatch can still trigger captcha/interstitial/ad behavior
- the service succeeds because of fallback, not because headless browsing became fully reliable
- `terraform/4_researcher` currently has provider/plugin instability and was not cleanly used for the final deploy
- `/health` still reports:

```json
"bedrock_model": "bedrock/amazon.nova-pro-v1:0"
```

This field is misleading because the current runtime model is:

- `openai/gpt-5.4-nano`

That health field was not fixed during this incident because it did not block Step 4 testing.

## Why OpenAI traces still appeared

The student reported still seeing traces in OpenAI.

That is expected because:

- the service still uses OpenAI Agents SDK tracing;
- `OPENAI_API_KEY` is still configured;
- changing the model or fallback logic did not remove trace instrumentation.

So the presence of traces does not imply that Bedrock was being used.

## Summary of Changes

### Application code changed

- `backend/researcher/context.py`
- `backend/researcher/server.py`

### Documentation added

- `backend/researcher/README.md`

### Application behavior change

Before:

- browser failure -> tool loop -> `MaxTurnsExceeded` -> HTTP 500

After:

- browser failure -> constrained retry -> browserless fallback -> HTTP 200 + ingest success

## Additional Follow-up Change

After the incident fix, the `/health` endpoint still reported a misleading hard-coded field:

```json
"bedrock_model": "bedrock/amazon.nova-pro-v1:0"
```

That was inaccurate because the actual runtime model remained:

- `openai/gpt-5.4-nano`

### What was changed

In `backend/researcher/server.py`:

- added `_get_researcher_model_name()`
- changed the main runtime path to use that helper when creating the model
- changed `/health` to report:

```json
"researcher_model": "openai/gpt-5.4-nano"
```

or whatever value is currently supplied via:

- `RESEARCHER_MODEL`

### Why this change matters

This removes drift between:

- the actual model used by `run_research_agent()`
- the model reported by `/health`

That makes future debugging more reliable, especially when the student is not using Bedrock and is instead running:

- `openai/gpt-5.4-nano`

## New Incident After Health Fix

After the `/health` fix, `uv run test_research.py` returned a different degraded result.

### Observed behavior

The command:

```bash
uv run test_research.py
```

returned:

- successful service discovery
- successful `/health` response
- successful `POST /research` response
- successful ingest into the knowledge base

but the research content itself was only a placeholder explanation rather than a real verified market note.

The returned message said the browse step could not be completed reliably because:

- `browser_snapshot` failed with a read-only filesystem error:
  - `EROFS`
- other sources produced noisy/blocked/404 outcomes

### What this means

This is not the same failure mode as the earlier:

- `Max turns exceeded`

That earlier failure was primarily an agent/tool-loop problem.

The new behavior indicates:

- the service is up
- the endpoint returns `200 OK`
- the fallback path still allows a result to be stored
- but browser-based verification inside Lambda is still not reliable

So this is a:

- successful infrastructure response
- degraded research result

not a full successful researcher run for Guide 4 Step 4.

### Current interpretation

The current likely issue is:

- some Playwright MCP or `browser_snapshot` behavior is trying to write outside writable Lambda storage

In AWS Lambda container runtime:

- most of the filesystem is read-only
- `/tmp` is the primary writable location

So `EROFS` strongly suggests an attempt to write to a non-writable path.

### Important note

At this stage, that filesystem explanation is still a working hypothesis inferred from the returned error text.

It has **not yet been fully proven** in this incident note by CloudWatch evidence.

The correct next debugging step is:

1. inspect CloudWatch logs for `alex-researcher`
2. identify the exact failing tool/action/path
3. confirm whether the write target is outside `/tmp`
4. then apply a minimal fix

## Recommended Next Steps

If this repository is reopened in a new session, the next likely tasks are:

1. decide whether the browserless fallback is acceptable long-term for the course project;
2. optionally improve browser source strategy further:
   - direct article URLs,
   - less protected domains,
   - stronger tool constraints;
3. investigate and clean up the Terraform provider/plugin issue in:
   - `terraform/4_researcher`

## Quick Restart Context

If a new session needs the shortest useful summary, use this:

- We are using Lambda Function URL, not App Runner.
- Researcher model is `openai/gpt-5.4-nano`.
- The original `uv run test_research.py` failure was caused by MCP browser loops and captchas, not by Lambda URL or model auth.
- We proved this with CloudWatch logs.
- We changed `context.py` and `server.py`.
- We added staged recovery:
  - normal browser run
  - constrained browser retry
  - browserless fallback
- The current deployed Lambda now returns `200 OK` and ingests the result successfully.
- Terraform in `terraform/4_researcher` still has provider/plugin issues and was bypassed for the final deploy using direct AWS Lambda image update.
