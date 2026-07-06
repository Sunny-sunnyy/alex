# Researcher Model Benchmark Design

Date: 2026-07-06

## Required Worker Process

Any agent implementing this spec must begin with:

- `using-superpowers`
- `brainstorming`

If the implementation agent is following the plan directly, it should use `brainstorming` only to confirm scope and blockers, not to redesign the benchmark unless new evidence changes the scope.

For execution, use one of:

- `subagent-driven-development` for one task per fresh agent
- `executing-plans` for inline execution

Before claiming completion, use:

- `verification-before-completion`

## Context

Researcher is currently at Guide 4 Step 4. The real implementation is Lambda Function URL, not App Runner.

The current default model is:

- `openai/gpt-5.4-nano`

The model still to benchmark is:

- `openrouter/openai/gpt-oss-120b`

The browser path has improved but is not fully stable:

- immediate-snapshot strategy has produced a reproducible `success_verified` case;
- only `NVIDIA AI datacenter demand` has passed reproducibly so far;
- Investopedia is the only source type proven to pass the verified-web gate;
- AP News and CNN Business are still unproven;
- the other four benchmark topics fail the verified-web gate by design.

This benchmark is not intended to fix browser retrieval. It is intended to compare whether the model affects stability, speed, and verified-web success under the same browser/runtime constraints.

## Problem Statement

Tasks 1-5 from the older observability/stability plan are complete:

- structured CloudWatch observability
- terminal run summary
- ingest telemetry propagation
- verified-web-only enforcement
- immediate-snapshot browser stability pass

Tasks 6-9 remain:

1. write a benchmark runbook;
2. run deployed benchmark for `openai/gpt-5.4-nano`;
3. run deployed benchmark for `openrouter/openai/gpt-oss-120b`;
4. compare results and record findings.

The old docs were split across multiple incident/spec/plan files. This spec replaces those files and becomes the benchmark design source of truth.

## Goals

The benchmark must answer:

- Which model is faster on deployed Lambda runtime?
- Which model reaches `success_verified` more often?
- Which model fails cleanly more often when verified web content is unavailable?
- Which model causes fewer browser loops or max-turn failures?
- Which model is the better default for the current Lambda Function URL implementation?

## Non-Goals

This benchmark must not:

- redesign the browser source strategy;
- weaken verified-web-only enforcement;
- allow fallback notes into S3 Vectors;
- change `/research` API response contract;
- change the benchmark topic set;
- rewrite `guides/4_researcher.md`;
- run local-only model comparisons and call them production results;
- dump secrets from `.env`, `terraform.tfvars`, Lambda environment variables, or API keys.

## Current Architecture

Runtime flow:

```text
test_research.py
  -> Terraform output researcher_url
  -> Lambda Function URL /health
  -> Lambda Function URL /research
  -> FastAPI server.py
  -> OpenAI Agents SDK Runner
  -> LiteLLM model selected by RESEARCHER_MODEL
  -> Playwright MCP browser
  -> ingest_financial_document tool
  -> API Gateway ingest endpoint
  -> alex-ingest Lambda
  -> SageMaker embedding endpoint
  -> S3 Vectors index
```

Deployment flow:

```text
backend/researcher/deploy.py
  -> ensure ECR prerequisites through Terraform
  -> docker buildx build linux/amd64
  -> docker tag
  -> docker push
  -> write terraform/4_researcher/researcher.auto.tfvars.json
  -> terraform apply
  -> wait for Lambda active
```

Known deploy fallback:

```text
if Terraform provider crashes after image push:
  aws lambda update-function-code --function-name alex-researcher --image-uri <image-uri> --region ap-southeast-1
```

## Model Configuration

`terraform/4_researcher/main.tf` passes these environment variables into Lambda:

- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `ALEX_API_ENDPOINT`
- `ALEX_API_KEY`
- `BEDROCK_REGION`
- `RESEARCHER_MODEL`
- `MCP_LOGGING`

`server.py` reads the active model through:

```python
def _get_researcher_model_name() -> str:
    return os.environ.get("RESEARCHER_MODEL", "openai/gpt-5.4-nano")
```

The benchmark must switch models through Terraform/Lambda configuration, not by editing `server.py`.

Required model strings:

- Model A: `openai/gpt-5.4-nano`
- Model B: `openrouter/openai/gpt-oss-120b`

If OpenRouter requires a different LiteLLM model string in this environment, pause and confirm before running Model B. Do not silently substitute a model.

## Benchmark Topic Set

Use exactly these topics:

1. `Tesla competitive advantages`
2. `Microsoft cloud revenue growth`
3. `NVIDIA AI datacenter demand`
4. `Amazon advertising growth`
5. `Apple services revenue growth`

Reasons:

- They are already used in prior evidence.
- They cover large-cap equity/business themes.
- They preserve comparability with immediate-snapshot verification.
- One topic has a known reproducible success case, which gives a sanity check.

## Source Preference

Keep the current source preference unchanged:

1. Investopedia
2. AP News
3. CNN Business
4. Reuters only if a direct article page loads cleanly

The benchmark should measure current behavior, not optimize sources mid-run.

## Outcome Taxonomy

Use server-side CloudWatch evidence as the source of truth.

Primary outcome values:

- `success_verified`: verified article-derived content was ingested with clean `source_url`.
- `failed_browser`: browser or verified-web gate failed.
- `failed_ingest`: ingest tool rejected or failed the document.
- `failed_unknown`: request failed but classification is inconclusive.

Useful phase statuses:

- `article_captured`: browser phase captured a clean article URL.
- `page_drifted`: browser phase saw drift markers.
- `ok`: browser finished but capture quality is inconclusive.
- `max_turns`: browser/agent exhausted turn budget.
- `error`: unexpected exception.

Terminal-side outcomes are only quick hints:

- `success_verified`
- `unexpected_200_nonverified`
- HTTP 500 with `Verified web content not obtained...`

Do not treat the terminal success banner alone as proof of verified success.

## Metrics To Collect

For each model/topic run, collect:

- model
- topic
- HTTP outcome
- terminal request duration in ms
- terminal outcome
- terminal degraded signal
- CloudWatch `run_id`
- CloudWatch `request_end outcome`
- CloudWatch `ingest_success`
- CloudWatch `degraded_reason`
- CloudWatch `total_duration_ms`
- browser phase statuses
- `snapshot_page_url` if present
- `research_ingest success`
- `document_id` if present

Derived model-level metrics:

- verified success count out of 5
- clean failure count out of 5
- unexpected 200 nonverified count out of 5
- max-turn count out of 5
- page-drift count out of 5
- median terminal request duration
- fastest topic
- slowest topic

## Success Criteria

The benchmark is complete when:

- both models have been deployed separately to the same Lambda service;
- `/health` confirms the active model before each 5-topic run;
- all 10 topic requests have terminal output recorded;
- matching CloudWatch evidence has been collected for all 10 requests or explicitly marked missing;
- findings recommend one default model for the current runtime;
- findings distinguish model behavior from browser/source instability.

The benchmark is still valid if many runs fail verified-web-only. Clean failure is part of the measured behavior.

## Safety Requirements

Do not print:

- `.env`
- full `terraform.tfvars`
- full Lambda environment variables
- API keys
- OpenAI/OpenRouter keys
- API Gateway key values

Safe checks:

```bash
aws lambda get-function-configuration \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Environment.Variables.RESEARCHER_MODEL' \
  --output text
```

Unsafe checks:

```bash
aws lambda get-function-configuration --function-name alex-researcher
cat terraform.tfvars
cat .env
```

## Handling Existing Dirty Files

At the time this spec was created, these files were dirty before benchmark work:

- `terraform/4_researcher/main.tf`
- `terraform/4_researcher/outputs.tf`
- untracked `startup_prompt.md`

The observed Terraform diff changed scheduler wording from 2 hours to 12 hours. This is unrelated to the benchmark. Do not revert, modify, or commit those changes unless the user explicitly asks.

Do not delete `startup_prompt.md` unless the user confirms it is disposable.

## Documentation Consolidation

This spec replaces the old researcher incident/spec docs that were split across several researcher markdown files and older superpowers handoff files. Those files were intentionally removed so future agents have one README, one spec, and one plan to read.

The remaining source-of-truth docs are:

- `backend/researcher/README.md`
- `docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md`
- `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`

## Open Questions For Executor

Ask before execution only if one of these blocks the benchmark:

- Is `OPENROUTER_API_KEY` configured in `terraform/4_researcher/terraform.tfvars` or Lambda environment?
- Does LiteLLM accept `openrouter/openai/gpt-oss-120b` in this environment?
- Should the vector store be cleaned before benchmarking?

Recommended defaults:

- Do not print secrets while checking OpenRouter availability.
- Use `openrouter/openai/gpt-oss-120b` unless a real runtime error proves the string is invalid.
- Do not clean S3 Vectors before benchmarking.
