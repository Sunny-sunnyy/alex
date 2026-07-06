# Researcher Model Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILLS: Start with `using-superpowers` and `brainstorming` to confirm scope. Then use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Use `verification-before-completion` before claiming any task is complete.

**Goal:** Benchmark deployed Researcher behavior for `openai/gpt-5.4-nano` versus `openrouter/openai/gpt-oss-120b` on the fixed 5-topic set without changing browser strategy or verified-web-only enforcement.

**Architecture:** Use existing Terraform/Lambda model configuration to deploy one model at a time. For each model, run the same 5 topics through `backend/researcher/test_research.py`, collect terminal summaries and CloudWatch `research_run`/`research_ingest` evidence, then document the comparison in the benchmark files.

**Tech Stack:** Python 3.12, uv, FastAPI, OpenAI Agents SDK, LiteLLM, Playwright MCP, AWS Lambda Function URL, ECR, Terraform, CloudWatch Logs, S3 Vectors

## Global Constraints

- Use `using-superpowers` and `brainstorming` before execution.
- Do not modify `guides/4_researcher.md`.
- Do not modify browser strategy during the benchmark.
- Do not weaken verified-web-only enforcement.
- Do not allow fallback/general-knowledge notes into S3 Vectors.
- Do not change the `/research` API contract.
- Benchmark only on deployed Lambda runtime.
- Use exactly these two model strings unless evidence proves one is invalid: `openai/gpt-5.4-nano`, `openrouter/openai/gpt-oss-120b`.
- Use exactly the fixed 5-topic set from the spec.
- Do not print `.env`, full `terraform.tfvars`, full Lambda environment variables, API keys, or secret values.
- Do not touch pre-existing dirty Terraform scheduler changes unless explicitly asked.
- Do not delete or modify untracked `startup_prompt.md` unless explicitly asked.
- Do not run `cleanup_s3vectors.py` unless explicitly asked.

---

## File Structure

### Files already updated before benchmark execution

- `backend/researcher/README.md`
  - Current source of truth for runtime state and operational notes.
- `docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md`
  - Benchmark design and constraints.
- `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`
  - This execution plan.

### Files to modify during benchmark execution

- `docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md`
  - Only update if execution discovers a design-level fact that changes assumptions.
- `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`
  - Add benchmark results and findings sections.
- `backend/researcher/README.md`
  - Add final recommended model after benchmark.

### Files to inspect but not dump fully

- `terraform/4_researcher/variables.tf`
- `terraform/4_researcher/main.tf`
- `terraform/4_researcher/outputs.tf`
- `terraform/4_researcher/researcher.auto.tfvars.json`

Do not print `terraform/4_researcher/terraform.tfvars`.

---

## Benchmark Constants

Models:

```text
openai/gpt-5.4-nano
openrouter/openai/gpt-oss-120b
```

Topics:

```text
Tesla competitive advantages
Microsoft cloud revenue growth
NVIDIA AI datacenter demand
Amazon advertising growth
Apple services revenue growth
```

CloudWatch filter:

```bash
aws logs tail /aws/lambda/alex-researcher --since 15m --region ap-southeast-1 | rg "research_run|research_ingest|snapshot_page_url"
```

Safe active-model check:

```bash
aws lambda get-function-configuration \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Environment.Variables.RESEARCHER_MODEL' \
  --output text
```

---

## Task 1: Preflight Current Benchmark Readiness

**Files:**
- Inspect: `backend/researcher/README.md`
- Inspect: `docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md`
- Inspect: `terraform/4_researcher/variables.tf`
- Inspect: `terraform/4_researcher/researcher.auto.tfvars.json`
- Modify: none

**Interfaces:**
- Consumes: repo state, Terraform variable definitions, current deployed image URI
- Produces: preflight evidence that benchmark can proceed safely

- [ ] **Step 1: Confirm working tree status without changing files**

Run:

```bash
git status --short
```

Expected:

- It may show existing dirty Terraform scheduler files and `startup_prompt.md`.
- Do not modify or revert those files.

- [ ] **Step 2: Confirm current image tag without exposing secrets**

Run:

```bash
sed -n '1,80p' terraform/4_researcher/researcher.auto.tfvars.json
```

Expected:

- Shows `researcher_image_uri`.
- Current known active tag before benchmark is `deploy-1783329777`, but accept a newer tag if already deployed by the user.

- [ ] **Step 3: Confirm Terraform supports model and OpenRouter variables**

Run:

```bash
rg "researcher_model|openrouter_api_key|RESEARCHER_MODEL|OPENROUTER_API_KEY" terraform/4_researcher
```

Expected:

- `variables.tf` defines `researcher_model`.
- `variables.tf` defines `openrouter_api_key`.
- `main.tf` passes both into Lambda environment.

- [ ] **Step 4: Confirm currently deployed model safely**

Run:

```bash
aws lambda get-function-configuration \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Environment.Variables.RESEARCHER_MODEL' \
  --output text
```

Expected:

- Usually `openai/gpt-5.4-nano`.
- If this command fails because Lambda is missing or region differs, stop and diagnose deployment/region before benchmarking.

- [ ] **Step 5: Confirm service health through test script path**

Run:

```bash
cd backend/researcher
uv run test_research.py "NVIDIA AI datacenter demand"
```

Expected:

- Either `success_verified` or designed `500`.
- If it returns `success_verified`, this is a useful warm-up datapoint but do not count it in the benchmark table unless it is part of the official model run.
- If it returns designed `500`, benchmark can still proceed.

---

## Task 2: Verify Benchmark Results Template

**Files:**
- Inspect: `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`

**Interfaces:**
- Consumes: fixed model/topic set
- Produces: confirmation that benchmark result tables are ready for later execution tasks

- [ ] **Step 1: Confirm the `Benchmark Results` section exists at the end of this plan**

Run:

```bash
sed -n '/^## Benchmark Results$/,$p' docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md | grep -n '^## Benchmark Results$\|^### Model A:\|^### Model B:\|^### Comparison Summary$'
```

Expected:

- One `## Benchmark Results` section.
- One Model A table.
- One Model B table.
- One `Comparison Summary` section.

- [ ] **Step 2: Verify the template has no incomplete-work markers**

Run:

```bash
rg "UNRESOLVED_MARKER" docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md
```

Expected:

- No output.

---

## Task 3: Deploy And Verify Model A `openai/gpt-5.4-nano`

**Files:**
- Modify: config only if `researcher_model` is not already `openai/gpt-5.4-nano`
- Do not print: `terraform/4_researcher/terraform.tfvars`

**Interfaces:**
- Consumes: Terraform Part 4 model configuration
- Produces: deployed Lambda with Model A active

- [ ] **Step 1: Check active model safely**

Run:

```bash
aws lambda get-function-configuration \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Environment.Variables.RESEARCHER_MODEL' \
  --output text
```

Expected:

- `openai/gpt-5.4-nano`.

- [ ] **Step 2: If active model is not Model A, update config without printing secrets**

Use Cursor or an editor to set only this value in `terraform/4_researcher/terraform.tfvars`:

```hcl
researcher_model = "openai/gpt-5.4-nano"
```

Do not paste the whole file into terminal or chat.

- [ ] **Step 3: Deploy Model A**

Run:

```bash
cd backend/researcher
uv run deploy.py
```

Expected:

- Docker build succeeds.
- ECR push succeeds.
- Terraform apply updates Lambda.
- Script prints Function URL.

- [ ] **Step 4: If Terraform provider crashes after image push, use direct Lambda image fallback**

Only use this if `uv run deploy.py` already built and pushed an image but Terraform failed with provider/plugin errors.

Run with the exact pushed image URI from deploy output or `researcher.auto.tfvars.json`:

```bash
aws lambda update-function-code \
  --function-name alex-researcher \
  --image-uri <ecr-image-uri> \
  --region ap-southeast-1
```

Then wait:

```bash
aws lambda get-function \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Configuration.[State,LastUpdateStatus]' \
  --output text
```

Expected:

- `Active Successful`.

- [ ] **Step 5: Verify `/health` reports Model A**

Run:

```bash
cd backend/researcher
uv run test_research.py "NVIDIA AI datacenter demand"
```

Expected:

- `RUN SUMMARY` shows `Model: openai/gpt-5.4-nano`.
- This warm-up run is not part of the official Model A table unless you intentionally start the 5-topic sequence here.

---

## Task 4: Run Official 5-Topic Benchmark For Model A

**Files:**
- Modify: `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`

**Interfaces:**
- Consumes: deployed Model A Lambda
- Produces: Model A benchmark table rows

- [ ] **Step 1: Run all five topics in fixed order**

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

- Some requests may return designed `500`.
- Do not treat designed `500` as benchmark failure.
- Record terminal duration/outcome when available.

- [ ] **Step 2: Collect matching CloudWatch evidence**

Run immediately after the 5-topic sequence:

```bash
aws logs tail /aws/lambda/alex-researcher --since 20m --region ap-southeast-1 | rg "research_run|research_ingest|snapshot_page_url"
```

Expected:

- Matching events for all five topics.
- At least one `request_end` per request.

- [ ] **Step 3: Fill Model A table**

For each topic, fill:

- `HTTP Result`: `200`, `500 verified-web gate`, `timeout`, or specific error.
- `Terminal Duration (ms)`: from `RUN SUMMARY` if request reached summary; otherwise approximate from script output or `n/a`.
- `Terminal Outcome`: `success_verified`, `unexpected_200_nonverified`, `n/a on 500`, or actual terminal classification.
- `Degraded Signal`: terminal degraded marker or HTTP detail.
- `CloudWatch Outcome`: from `request_end outcome=...`.
- `Ingest Success`: from `request_end ingest_success=...` or `research_ingest success=...`.
- `Browser Statuses`: e.g. `browser_run=article_captured`, `browser_run=ok`, `constrained_browser_run=max_turns`.
- `Snapshot URL`: URL from `snapshot_page_url`, if present.
- `Notes`: short evidence note.

- [ ] **Step 4: Do not change code based on Model A results**

If Model A has poor browser success, record it. Do not patch prompt/browser/model behavior during the benchmark.

---

## Task 5: Deploy And Verify Model B `openrouter/openai/gpt-oss-120b`

**Files:**
- Modify: config only
- Do not print: `terraform/4_researcher/terraform.tfvars`

**Interfaces:**
- Consumes: OpenRouter key configured in Terraform/Lambda
- Produces: deployed Lambda with Model B active

- [ ] **Step 1: Confirm OpenRouter variable wiring without printing secrets**

Run:

```bash
rg "openrouter_api_key|OPENROUTER_API_KEY" terraform/4_researcher/variables.tf terraform/4_researcher/main.tf
```

Expected:

- `variables.tf` defines `openrouter_api_key`.
- `main.tf` passes `OPENROUTER_API_KEY` into Lambda.

- [ ] **Step 2: Set model config to Model B**

Use Cursor or an editor to set only this value in `terraform/4_researcher/terraform.tfvars`:

```hcl
researcher_model = "openrouter/openai/gpt-oss-120b"
```

Do not print the file.

- [ ] **Step 3: Deploy Model B**

Run:

```bash
cd backend/researcher
uv run deploy.py
```

Expected:

- Docker build succeeds.
- ECR push succeeds.
- Lambda updates.

- [ ] **Step 4: Use Lambda image fallback only if needed**

If Terraform fails after image push:

```bash
aws lambda update-function-code \
  --function-name alex-researcher \
  --image-uri <ecr-image-uri> \
  --region ap-southeast-1
```

Then verify:

```bash
aws lambda get-function \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Configuration.[State,LastUpdateStatus]' \
  --output text
```

Expected:

- `Active Successful`.

- [ ] **Step 5: Verify Model B is active safely**

Run:

```bash
aws lambda get-function-configuration \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Environment.Variables.RESEARCHER_MODEL' \
  --output text
```

Expected:

- `openrouter/openai/gpt-oss-120b`.

- [ ] **Step 6: Smoke test Model B with one request**

Run:

```bash
cd backend/researcher
uv run test_research.py "NVIDIA AI datacenter demand"
```

Expected:

- If it fails with an auth/model-string error, stop and record the exact error.
- If LiteLLM reports invalid model string, ask the user before substituting a different string.
- If it returns designed verified-web `500`, Model B can still proceed to official benchmark.

---

## Task 6: Run Official 5-Topic Benchmark For Model B

**Files:**
- Modify: `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`

**Interfaces:**
- Consumes: deployed Model B Lambda
- Produces: Model B benchmark table rows

- [ ] **Step 1: Run all five topics in fixed order**

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

- Same interpretation as Model A.
- Designed verified-web `500` is valid evidence.

- [ ] **Step 2: Collect matching CloudWatch evidence**

Run:

```bash
aws logs tail /aws/lambda/alex-researcher --since 20m --region ap-southeast-1 | rg "research_run|research_ingest|snapshot_page_url"
```

Expected:

- Matching events for all Model B topics.

- [ ] **Step 3: Fill Model B table**

Use the same columns and rules as Task 4.

- [ ] **Step 4: Keep benchmark conditions unchanged**

Do not patch source preference, prompt, max turns, browser args, or ingest gate during Model B collection.

---

## Task 7: Compare Models And Record Findings

**Files:**
- Modify: `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`
- Modify: `backend/researcher/README.md`

**Interfaces:**
- Consumes: completed Model A and Model B tables
- Produces: recommendation and operational notes

- [ ] **Step 1: Count core metrics for each model**

For each model, compute:

```text
verified_success_count = count rows with CloudWatch Outcome success_verified
clean_failure_count = count rows with HTTP 500 verified-web gate or CloudWatch failed_browser
unexpected_200_nonverified_count = count rows with terminal unexpected_200_nonverified
max_turn_count = count rows with browser status max_turns
page_drift_count = count rows with browser status page_drifted
median_duration_ms = median terminal duration where available
```

- [ ] **Step 2: Fill `Comparison Summary`**

Use evidence-backed statements only:

```markdown
### Comparison Summary

- Faster model: `<model>` because median duration was `<x>` ms vs `<y>` ms.
- More verified model: `<model>` because verified success count was `<x>/5` vs `<y>/5`.
- Cleaner-failing model: `<model>` because it produced fewer unexpected 200 nonverified responses.
- Lower max-turn model: `<model>` because max-turn count was `<x>` vs `<y>`.
- Recommended default model: `<model>`.
- Reasoning: `<2-5 sentences separating model behavior from browser/source instability.>`
```

- [ ] **Step 3: Update README pending-work/current recommendation**

In `backend/researcher/README.md`, update:

```markdown
## Pending Work
```

Replace benchmark pending text with the completed recommendation:

```markdown
## Benchmark Result

The benchmark compared:

- `openai/gpt-5.4-nano`
- `openrouter/openai/gpt-oss-120b`

Recommended default: `<model>`

Reason: `<short evidence-backed reason>`
```

- [ ] **Step 4: Verify the consolidated markdown file set**

Run:

```bash
find backend/researcher docs/superpowers -maxdepth 3 -type f -name '*.md' | sort
```

Expected:

- Only `backend/researcher/README.md`, the model benchmark spec, the model benchmark plan, and unrelated `README.md` files if present.

---

## Task 8: Restore Preferred Model If Needed

**Files:**
- Modify: config only if the recommended model is not the currently deployed model or the user wants default restored

**Interfaces:**
- Consumes: benchmark recommendation
- Produces: Lambda deployed with desired final model

- [ ] **Step 1: Ask the user before changing the final active model**

Ask:

```text
Benchmark complete. Recommended default is <model>. Do you want the live Lambda left on this model, or restored to openai/gpt-5.4-nano?
```

- [ ] **Step 2: If user chooses a final model, set `researcher_model` config**

Use Cursor/editor to update only:

```hcl
researcher_model = "<chosen-model>"
```

- [ ] **Step 3: Deploy final model**

Run:

```bash
cd backend/researcher
uv run deploy.py
```

Use the known Lambda image fallback only if Terraform crashes after push.

- [ ] **Step 4: Verify final active model safely**

Run:

```bash
aws lambda get-function-configuration \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Environment.Variables.RESEARCHER_MODEL' \
  --output text
```

Expected:

- Matches user-chosen final model.

---

## Task 9: Final Verification And Commit

**Files:**
- `backend/researcher/README.md`
- `docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md`
- `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`
- Deleted old researcher markdown files

**Interfaces:**
- Consumes: final docs, git diff, verification output
- Produces: committed benchmark documentation

- [ ] **Step 1: Verify file set is consolidated**

Run:

```bash
find backend/researcher docs/superpowers -maxdepth 3 -type f -name '*.md' | sort
```

Expected:

- `backend/researcher/README.md`
- `docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md`
- `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`
- Other `README.md` files are allowed.
- Old researcher incident/spec/plan files should be gone.

- [ ] **Step 2: Review diff without exposing secrets**

Run:

```bash
git diff -- backend/researcher docs/superpowers
```

Expected:

- Only documentation consolidation and benchmark result updates.
- No secrets.

- [ ] **Step 3: Check status**

Run:

```bash
git status --short
```

Expected:

- Includes docs changes.
- May still include pre-existing Terraform scheduler changes and `startup_prompt.md`; do not include those unless user asked.

- [ ] **Step 4: Commit only benchmark docs and README changes**

Run:

```bash
git add backend/researcher/README.md \
  docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md \
  docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md
git add -u backend/researcher docs/superpowers
git commit -m "docs: consolidate researcher benchmark handoff"
```

Expected:

- Commit succeeds.
- Pre-existing Terraform scheduler changes and `startup_prompt.md` remain uncommitted unless the user separately requests them.

---

## Self-Review

### Spec Coverage

- Uses current Lambda Function URL implementation: covered.
- Keeps verified-web-only gate: covered.
- Uses fixed 5-topic set: covered.
- Benchmarks both requested models: covered.
- Avoids secrets: covered.
- Preserves dirty unrelated Terraform changes: covered.
- Leaves browser/source strategy unchanged: covered.

### Placeholder Scan

- The plan contains no incomplete-work markers.
- Blank result table cells are intentional execution fields.
- `<ecr-image-uri>` and `<chosen-model>` are explicit runtime values the executor must obtain from deploy output or user choice.

### Type And Name Consistency

- Model strings match spec.
- Topic strings match spec.
- CloudWatch fields match current `server.py` log names.
- File paths are exact.

## Benchmark Results

### Model A: `openai/gpt-5.4-nano`

| Topic | HTTP Result | Terminal Duration (ms) | Terminal Outcome | Degraded Signal | CloudWatch Outcome | Ingest Success | Browser Statuses | Snapshot URL | Notes |
|-------|-------------|------------------------|------------------|-----------------|-------------------|----------------|------------------|--------------|-------|
| Tesla competitive advantages | | | | | | | | | |
| Microsoft cloud revenue growth | | | | | | | | | |
| NVIDIA AI datacenter demand | | | | | | | | | |
| Amazon advertising growth | | | | | | | | | |
| Apple services revenue growth | | | | | | | | | |

### Model B: `openrouter/openai/gpt-oss-120b`

| Topic | HTTP Result | Terminal Duration (ms) | Terminal Outcome | Degraded Signal | CloudWatch Outcome | Ingest Success | Browser Statuses | Snapshot URL | Notes |
|-------|-------------|------------------------|------------------|-----------------|-------------------|----------------|------------------|--------------|-------|
| Tesla competitive advantages | | | | | | | | | |
| Microsoft cloud revenue growth | | | | | | | | | |
| NVIDIA AI datacenter demand | | | | | | | | | |
| Amazon advertising growth | | | | | | | | | |
| Apple services revenue growth | | | | | | | | | |

### Comparison Summary

- Faster model:
- More verified model:
- Cleaner-failing model:
- Lower max-turn model:
- Recommended default model:
- Reasoning:
