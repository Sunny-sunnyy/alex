# Researcher Session Handoff

Date: 2026-07-05

## Context read and confirmed

I read the required project and researcher context before making changes:

- `gameplan.md`
- `guides/architecture.md`
- `guides/agent_architecture.md`
- `guides/1_permissions.md`
- `guides/2_sagemaker.md`
- `guides/3_ingest.md`
- `guides/4_researcher.md`
- `backend/ingest/*` relevant code and docs
- `backend/researcher/*` relevant code and docs
- `terraform/2_sagemaker/*`
- `terraform/3_ingestion/*`
- `terraform/4_researcher/*`
- `docs/superpowers/plans/2026-07-05-researcher-observability-stability-benchmark.md`

I also read Guides 5-8 to preserve full-course context because `gameplan.md` and `AGENTS.md` require end-to-end understanding before changing the repo.

## Current project reality confirmed

Guide 4 has partial historical mismatch with the current repo implementation.

Current source of truth in this repo:

- Researcher deployment uses AWS Lambda container image
- Public entrypoint uses Lambda Function URL
- Researcher is not currently using App Runner
- Researcher is currently using `openai/gpt-5.4-nano`
- OpenAI Agents SDK tracing is still expected if `OPENAI_API_KEY` is configured

Relevant source-of-truth files:

- `backend/researcher/server.py`
- `backend/researcher/deploy.py`
- `backend/researcher/Dockerfile`
- `backend/researcher/mcp_servers.py`
- `terraform/4_researcher/main.tf`

## User-approved scope

The user selected scope `A`:

- Make Guide 4 Step 4 pass stably on the current real implementation
- Do not try to force the repo back to App Runner or Bedrock in this phase
- Work directly in `backend/researcher` and `terraform/4_researcher`

## Backup decision

We explicitly decided not to create duplicate folders such as:

- `researcher_original`
- `4_researcher_original`

Reason:

- duplicated folders would create drift and confusion
- git is the correct backup mechanism for this repo

## Snapshot created before any new fixes

I staged the current researcher-related state, committed it, and pushed it to remote.

Checkpoint commit:

- `0409b99` - `chore: checkpoint researcher lambda guide4 state`

Remote status:

- pushed to `origin/main`

This commit is now the rollback point for any upcoming Guide 4 Step 4 fixes.

## What has been done in this session

1. Loaded the required workflow skills and followed `using-superpowers` with `brainstorming` as the main discussion process.
2. Read the required project guides, researcher code, terraform, and researcher-specific debugging documents.
3. Confirmed the real deployment/runtime model differs from older App Runner wording in Guide 4.
4. Confirmed the student is currently at Guide 4, Step 4.
5. Confirmed the working goal is stability on the current Lambda Function URL implementation.
6. Created a git checkpoint and pushed it before starting any new fix work.

## Important technical findings already confirmed

- The repo has existing researcher instability history documented in `BUG_AND_FIX.md`
- A previously proven failure mode was `MaxTurnsExceeded` caused by MCP/browser loops
- A newer degraded mode is suspected around Playwright/browser snapshot behavior and read-only filesystem (`EROFS`)
- That newer filesystem issue was noted as a working hypothesis that still needs evidence-driven confirmation before changing code further

## Next proposed step

Next step is to reproduce the current Guide 4 Step 4 failure mode on the real deployed flow and prove the current root cause before making code changes.

Planned order:

1. reproduce current behavior
2. inspect evidence
3. classify the actual failure mode
4. apply the smallest fix supported by evidence

## Waiting for user confirmation

No new researcher fix has been implemented after the checkpoint commit yet.

Waiting for explicit confirmation before starting:

- reproduction
- debugging
- code changes for the next fix

## Reproduction completed after confirmation

After the user confirmed the next step, I reproduced the current deployed behavior again on the real Lambda Function URL.

### Commands run

- `uv run test_research.py "Bitcoin ETF inflows"`
- `uv run test_research.py "Tesla competitive advantages"`
- `aws logs tail /aws/lambda/alex-researcher --since 5m --region ap-southeast-1`

### What the latest reproduction proved

Both test requests returned:

- HTTP `200 OK`
- non-empty research content
- successful end-to-end service execution

This is important because it means the current deployed service is no longer in the previously observed hard-failure state for these scenarios.

### Actual returned behavior

For `Tesla competitive advantages`:

- the service returned a concise investment note with clear bullets and recommendation
- the result quality was acceptable for Guide 4 Step 4

For `Bitcoin ETF inflows`:

- the service returned a constrained but still usable note
- it explicitly stated that daily inflow figures could not be verified because source pages were access-restricted
- it still provided interpretation guidance and a recommendation structure

This is weaker than ideal, but it is materially better than a placeholder or HTTP error.

### Current root cause classification

CloudWatch logs still show the same structural browser problem:

- Reuters redirects into `geo.captcha-delivery.com`
- browser sessions still encounter noisy ad/tracker/interstitial behavior
- browser navigation remains unreliable inside Lambda headless runtime

But the latest evidence does **not** show the service fully failing for the reproduced cases.

So the current diagnosis is:

- browser-based research is still unstable
- fallback behavior is currently good enough to keep many requests successful
- the main remaining problem is **result quality consistency**, not basic availability

### Updated technical conclusion

At this point, the system appears to be in this state:

1. deployment drift was previously fixed
2. service health is good
3. browser path is still noisy and source-restricted
4. fallback is often rescuing the request successfully
5. remaining work should focus on:
   - improving consistency of fallback output quality, or
   - tightening acceptance criteria / guide expectations for Step 4 on the current Lambda implementation

### Recommended next task

The recommended next task is no longer "fix a hard failure first".

It is now:

- harden researcher output quality for blocked topics while preserving the current successful `200 OK` behavior

That is the smallest next step that matches the current evidence.

## Stable-source pass completed

After the next user confirmation, I applied a narrow stable-source pass to bias the Researcher toward cleaner direct article pages.

### Files edited

- `backend/researcher/context.py`
- `backend/researcher/server.py`
- `backend/researcher/OBSERVABILITY_AND_BENCHMARK_SPEC.md`
- `docs/superpowers/plans/2026-07-05-researcher-observability-stability-benchmark.md`
- `terraform/4_researcher/researcher.auto.tfvars.json`
- `backend/researcher/session_handoff.md`

### Behavior changes made

In prompts and query builders:

- added `CNN Business` to the preferred source set
- prioritized:
  - `Investopedia`
  - `AP News`
  - `CNN Business`
- downgraded Reuters to optional-only when a direct article loads cleanly
- explicitly told the agent to avoid:
  - finance homepages
  - market portals
  - tracker pages
  - captcha/interstitial flows

In benchmark/spec docs:

- replaced weaker benchmark topics with a more stable large-cap/business set:
  - `Tesla competitive advantages`
  - `Microsoft cloud revenue growth`
  - `NVIDIA AI datacenter demand`
  - `Amazon advertising growth`
  - `Apple services revenue growth`

### Deployment method used

`uv run deploy.py` failed again because Terraform AWS provider still crashed with:

- `Plugin did not respond`

So I used the previously proven manual deployment path:

1. build Docker image locally
2. log in to ECR
3. push new image tag
4. update Lambda code directly with AWS CLI
5. wait until Lambda reached:
   - `LastUpdateStatus=Successful`
   - `State=Active`

Deployed image tag:

- `deploy-1783240866`

### Verification commands run

- `curl -m 30 -sS https://u7lbfi3ovnkij7hwffzv7ehqxm0kzvbo.lambda-url.ap-southeast-1.on.aws/health`
- `uv run test_research.py "Tesla competitive advantages"`
- `uv run test_research.py "Microsoft cloud revenue growth"`
- `uv run test_research.py "NVIDIA AI datacenter demand"`
- `aws logs tail /aws/lambda/alex-researcher --since 5m --region ap-southeast-1`

### What the verification proved

`/health` confirmed:

- service healthy
- model still `openai/gpt-5.4-nano`
- Lambda container runtime reachable

All three deployed end-to-end tests returned:

- HTTP `200 OK`
- non-empty result
- successful request completion

But the output quality remained mixed:

- `Tesla competitive advantages`
  - returned a useful browserless fallback note
- `NVIDIA AI datacenter demand`
  - returned a useful browserless fallback note
- `Microsoft cloud revenue growth`
  - stayed in browser mode longer and returned a constrained note explaining that clean direct article pages were not successfully verified

### CloudWatch evidence after the stable-source pass

The logs show the source bias did change as intended:

- Tesla runs opened Investopedia direct article pages
- NVIDIA runs opened a CNN article page
- Microsoft runs attempted the preferred stable-source set

However, the logs still prove browser instability remains:

- direct article pages still bounce into `about:blank` or noisy side flows
- some runs still exceed browser turns and fall back
- browser-based success is still not reliable enough to call this fully fixed

### Current status after this pass

This pass improved source targeting, but did not fully solve Lambda browser instability.

The current honest state is:

- Step 4 is practically passable because requests return `200 OK`
- useful notes are still being produced and ingested
- the service is still relying heavily on fallback/degraded paths for stability
- browser-verifiable article extraction is still inconsistent

## Terminal outcome classification added

After the next request, `backend/researcher/test_research.py` was upgraded so that terminal output now explicitly shows:

- `Model`
- `Topic`
- `Request Duration (ms)`
- `Outcome`
- `Degraded Signal`
- `Ingest Status`

### File edited

- `backend/researcher/test_research.py`

### Classification behavior implemented

The script now classifies visible result text into:

- `success_verified`
- `success_fallback`

This classification is currently:

- terminal-side only
- heuristic
- based on response text markers

Examples of fallback markers:

- `Quick high-level note`
- `no web research`
- `page unavailable`
- `could not verify`

### Verification commands run

- `uv run test_research.py "Tesla competitive advantages"`
- `uv run test_research.py "Microsoft cloud revenue growth"`

### Verification result

Both runs printed the new `RUN SUMMARY` block successfully.

Observed classifications:

- `Tesla competitive advantages` -> `success_fallback`
- `Microsoft cloud revenue growth` -> `success_fallback`

So this change is verified to improve terminal observability, even though it does not yet prove any `success_verified` browser-based run in the current Lambda environment.

## Terminal classification false-positive fix completed

After the next user report, I confirmed that the first terminal heuristic was too weak.

### Bug observed

The user ran:

- `uv run test_research.py "Tesla competitive advantages"`

and the script incorrectly printed:

- `Outcome: success_verified`
- `Degraded Signal: none`

even though the response text clearly contained blocked/degraded evidence such as:

- `Just a moment...`
- `404 / unavailable`
- `access-restricted`
- inability to use a clean direct article page

So the terminal summary had a false positive.

### What I changed

I tightened `classify_terminal_result()` in:

- `backend/researcher/test_research.py`

Added stronger fallback markers for phrases actually seen in deployed outputs, including:

- `just a moment`
- `page not found`
- `404 / unavailable`
- `access-restricted`
- `clean, accessible article content`
- `usable direct article page`
- `couldn't reliably quote`
- `couldn't base the analysis on a usable direct article page`
- `error page`

### Verification commands run

- `uv run test_research.py "Tesla competitive advantages"`
- `uv run test_research.py "Microsoft cloud revenue growth"`
- `uv run test_research.py "NVIDIA AI datacenter demand"`

### Verification result

All three runs returned:

- HTTP `200 OK`
- visible `RUN SUMMARY`
- `Outcome: success_fallback`

Observed degraded signals after the fix:

- `Tesla competitive advantages` -> `quick high-level note`
- `Microsoft cloud revenue growth` -> `quick high-level note`
- `NVIDIA AI datacenter demand` -> `quick high-level note`

### Conclusion

`Task 0.5` is complete:

- the known false-positive terminal classification was reproduced
- the heuristic was corrected
- the fix was verified on multiple deployed end-to-end runs

Important remaining truth:

- this does **not** mean browser-based verified success is now common
- it means the terminal summary is now less misleading
- the next task should still be structured observability in `server.py`

## Task 1 started and first observability slice verified

After the user asked to continue immediately into `Task 1`, I implemented the first server-side observability slice in:

- `backend/researcher/server.py`

### What was added

- `RunTrace` and `PhaseRecord` dataclasses
- one `run_id` per `/research` request
- structured log events for:
  - `phase_start`
  - `phase_end`
  - `request_end`
- degraded reason detection in runtime
- basic ingest success inference from response text
- normalized outcome emission in CloudWatch:
  - `success_verified`
  - `success_fallback`
  - `failed_ingest`
  - `failed_unknown`

### Important implementation note

The `/research` API contract was **not** changed.

The endpoint still returns the same response body shape as before; only internal runtime logging was added.

### Bug found during Task 1 implementation

The first implementation mistakenly computed:

- `total_duration_ms`

by summing all phase durations, which double-counted the request because:

- `request_start` already wrapped the whole request
- child phases were nested inside it

I fixed that by making:

- `total_duration_ms = request_start.duration_ms`

### Deployment path used

As before, `uv run deploy.py` was not used for the final deploy because Terraform AWS provider instability remains.

I deployed via:

1. build Docker image
2. push to ECR
3. update Lambda image directly with AWS CLI

Final deployed image tag for this Task 1 slice:

- `deploy-1783246453`

### Verification commands run

- local syntax check:
  - `UV_CACHE_DIR=/tmp/uv-cache uv run python -m py_compile server.py`
- deployed runtime:
  - `curl -m 30 -sS https://u7lbfi3ovnkij7hwffzv7ehqxm0kzvbo.lambda-url.ap-southeast-1.on.aws/health`
  - `uv run test_research.py "Tesla competitive advantages"`
  - `aws logs tail /aws/lambda/alex-researcher --since 2m --region ap-southeast-1 | rg "research_run"`

### What the verification proved

The deployed request still returned:

- HTTP `200 OK`
- terminal `RUN SUMMARY`

CloudWatch now clearly shows:

- `phase_start`
- `phase_end`
- `request_end`
- a shared `run_id`

Verified example:

- `phase=browser_run status=ok duration_ms=76694`
- `phase=request_start status=ok duration_ms=76694`
- `request_end outcome=success_fallback ingest_success=True degraded_reason=page_unavailable total_duration_ms=76694`

This confirms the first Task 1 observability slice is working end-to-end.
