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

## Task 4 Evidence Pass - 2026-07-05

After the newer observability work, I ran the fixed 5-topic benchmark set on the deployed Lambda runtime to refresh the diagnosis with current evidence rather than relying on older hypotheses.

### Fixed topic set executed

- `Tesla competitive advantages`
- `Microsoft cloud revenue growth`
- `NVIDIA AI datacenter demand`
- `Amazon advertising growth`
- `Apple services revenue growth`

### Commands used

- `uv run test_research.py "Tesla competitive advantages"`
- `uv run test_research.py "Microsoft cloud revenue growth"`
- `uv run test_research.py "NVIDIA AI datacenter demand"`
- `uv run test_research.py "Amazon advertising growth"`
- `uv run test_research.py "Apple services revenue growth"`
- `aws logs tail /aws/lambda/alex-researcher --since 15m --region ap-southeast-1 | rg "research_run|research_ingest|mcp:stderr|Error calling tool"`

### What the terminal runs showed

All 5 runs returned:

- HTTP `200 OK`
- non-empty output
- `Outcome: success_fallback`

No `success_verified` run appeared in this 5-topic pass.

### Evidence table

| Topic | Run ID | Terminal Outcome | Degraded Signal | Phase Pattern | Ingest Evidence | Notes |
|-------|--------|------------------|-----------------|---------------|-----------------|-------|
| Tesla competitive advantages | `83a1c05b-e31e-429a-9e6e-71f5a32d7c51` | `success_fallback` | `no web research` | `browser_run max_turns` -> `constrained_browser_run max_turns` -> `browserless_fallback_run ok` | `research_ingest success=True`, but `request_end ingest_success=None` | strong browser loop/fallback evidence |
| Microsoft cloud revenue growth | `5a9e661c-cb95-40e1-b5cd-8b7b8850349b` | `success_fallback` | `page not found` | `browser_run ok` | `research_ingest success=True`, but `request_end ingest_success=None` | output degraded due inaccessible article pages, not max turns |
| NVIDIA AI datacenter demand | `633c89b8-7075-4cdd-b8df-a425a6bafc7e` | `success_fallback` | `page not found` | `browser_run ok` | no `research_ingest` line seen in filtered window; `request_end ingest_success=None` | response text mentioned tooling/storage error while trying Reuters snapshot |
| Amazon advertising growth | `4944fbca-f75f-430c-a215-f6638ecca4f4` | `success_fallback` | `page unavailable` | `browser_run ok` | no `research_ingest` line seen in filtered window; `request_end ingest_success=None` | degraded due inaccessible direct pages |
| Apple services revenue growth | `8eb7ea80-2ecc-46ce-8e6e-abf1a652b59a` | `success_fallback` | `quick high-level note` | `browser_run max_turns` -> `constrained_browser_run max_turns` -> `browserless_fallback_run ok` | `research_ingest success=True`, but `request_end ingest_success=None` | second strong browser loop/fallback case |

### What this evidence weakens

This pass does **not** provide strong current evidence that the main instability is:

- Lambda Function URL availability
- FastAPI startup
- Bedrock/OpenAI authentication
- a dominant `EROFS` / read-only filesystem failure mode

That does not prove those issues cannot happen.
It means the latest 5-topic benchmark does not support them as the primary diagnosis right now.

### Current best-supported hypothesis

The current primary instability is:

1. browser-based research remains unreliable on the allowed direct-source set;
2. some runs degrade after blocked/unusable direct article pages but still finish inside `browser_run`;
3. some runs loop long enough to hit `MaxTurnsExceeded` twice and fall back to browserless output;
4. therefore the system is usable mainly because fallback behavior rescues the request, not because browser verification is stable.

### Important secondary finding

This evidence pass also showed that the newer ingest observability is useful but still incomplete:

- some runs emitted `research_ingest success=True`
- the same run still ended with `request_end ingest_success=None`

So any earlier statement that request-end ingest classification was fully solved is too strong.

What is true now:

- tool-level ingest evidence is better than before
- request-level ingest classification is still incomplete in some runs
- there is likely a context propagation gap between tool execution and request-final classification

### Updated conclusion after Task 4

At the end of this evidence pass, the honest system state is:

- browser stability is still the primary production problem
- the latest evidence supports `browser/content-access instability`, not `EROFS`, as the main root-cause direction
- ingest observability improved, but request-end ingest certainty still needs follow-up
- the next fix should target browser instability first, while keeping the ingest telemetry gap on the follow-up list

## Task 5 Fix Pass - 2026-07-05

Based on the Task 4 evidence, I did **not** pursue the older `/tmp` / `EROFS` theory as the next main fix.

Instead, I applied a smaller behavior fix aimed at the actual current failure pattern:

- blocked/unusable direct article pages
- browser loops consuming too many turns
- degraded outputs that ended by asking the user for another link/source

### Files changed

- `backend/researcher/context.py`
- `backend/researcher/server.py`
- `backend/researcher/test_research.py`

### What changed

In `context.py`:

- told the agent that if both allowed direct article attempts fail, it must:
  - stop browsing
  - switch to a short fallback note from general market knowledge
  - not ask the user for another link/source/retry choice

In `server.py`:

- strengthened topic-specific query strings with the same fallback rule
- reduced browser turn limits for topic-driven runs:
  - browser run: `15 -> 10`
  - constrained browser run: `12 -> 8`
- later extended degraded-result markers to catch newer fallback phrasings such as:
  - `quick high-level fallback`
  - `web sources blocked`
  - `no clean direct article found`
  - `browsing blocked`

In `test_research.py`:

- updated terminal fallback markers to match the new fallback phrasing so terminal summaries would not over-report `success_verified`

### Deployment result

Unlike earlier sessions, `uv run deploy.py` succeeded end-to-end for this fix pass.

This matters because:

- the live Lambda was updated through the normal repo deployment path
- no manual `aws lambda update-function-code` fallback was required for this Task 5 code push

Deployed image sequence during this pass:

- `deploy-1783261751`
- `deploy-1783262258`
- `deploy-1783262370`

### 5-topic verification after the main Task 5 behavior fix

I reran the fixed benchmark set:

- `Tesla competitive advantages`
- `Microsoft cloud revenue growth`
- `NVIDIA AI datacenter demand`
- `Amazon advertising growth`
- `Apple services revenue growth`

#### Before Task 5

Task 4 benchmark had:

- 5/5 `success_fallback`
- repeated `MaxTurnsExceeded` on some topics
- multiple degraded outputs that ended by asking the user to supply another source/link

#### After Task 5 behavior fix

Observed improvements:

- the “ask the user for another link” style degraded output disappeared in the benchmark rerun
- outputs shifted toward **usable fallback notes** instead of deferring the work back to the user
- no `browser_run max_turns` appeared in the first full 5-topic rerun after deployment
- request durations dropped materially for several topics:
  - `Tesla`: from about `104s` to about `37s`
  - `Microsoft`: from about `54s` to about `11s`
  - `Apple`: from about `112s` to about `64s` in the immediate 5-topic rerun, then about `18s` on a later representative rerun

CloudWatch from the first Task 5 5-topic rerun showed:

- `browser_run status=ok` for all five benchmark topics

This is the strongest sign that the fix reduced the previous browser-loop burn.

### Remaining issues after Task 5

Task 5 improved behavior substantially, but it did **not** fully finish the area.

Remaining issues:

1. fallback is still common
   - usable fallback output improved
   - but browser-verified direct-source success is still not consistently proven

2. ingest request-end summary still has gaps
   - some runs still showed:
     - `research_ingest success=True`
     - but `request_end ingest_success=None`

3. classification drift reappeared when fallback phrasing changed
   - I patched both terminal-side and server-side markers
   - then redeployed the marker fix

### Current conclusion after Task 5

Task 5 should be considered a **meaningful stability improvement**, not a full browser-success proof.

What is now true:

- browser loops are less dominant than before
- fallback output is more usable and less likely to bounce work back to the user
- the normal deployment path (`uv run deploy.py`) is currently working again

What is still true:

- fallback-heavy behavior remains
- request-end ingest certainty still needs another follow-up
- there is still room to tighten fallback classification and define what counts as true `success_verified`
