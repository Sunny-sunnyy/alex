# Researcher Service

`backend/researcher` is the application code for Alex Part 4. It runs the independent market-research agent that tries to gather verified web content, writes a concise investment note, and sends the note to the Part 3 ingest pipeline.

## Current Source Of Truth

The implementation in this repo uses:

- FastAPI application code in `server.py`
- Docker image built from `Dockerfile`
- AWS Lambda container image runtime
- Lambda Function URL as the public HTTPS endpoint
- ECR repository managed by `terraform/4_researcher`
- OpenAI Agents SDK with LiteLLM model selection
- Playwright MCP for browser access

Some older course text still mentions App Runner and Bedrock as the main Researcher runtime. For this repo state, treat Lambda Function URL and `openai/gpt-5.4-nano` as the current source of truth unless Terraform/runtime configuration explicitly changes it.

## Current Runtime State

As of 2026-07-06:

- Active deployed image tag: `deploy-1783329777`
- Current default model: `openai/gpt-5.4-nano`
- Benchmark model still to test: `openrouter/openai/gpt-oss-120b`
- Public service URL comes from `terraform/4_researcher` output `researcher_url`
- `/health` reports `researcher_model`
- `/research` enforces verified-web-only behavior
- Fallback notes are not allowed to be ingested
- Browser path has the first reproducible verified success, but it is not fully stable

Latest verified browser evidence:

- `NVIDIA AI datacenter demand` reached `success_verified` reproducibly 2/2 on 2026-07-06.
- Both passing NVIDIA runs used Investopedia article pages.
- Both passing NVIDIA runs logged `browser_run status=article_captured`.
- `Tesla competitive advantages`, `Microsoft cloud revenue growth`, `Amazon advertising growth`, and `Apple services revenue growth` still failed the verified-web gate in the same benchmark pass.

Current practical interpretation:

- Guide 4 Step 4 is pragmatically usable for demonstrating the system, but browser verification is only partially proven.
- Immediate-snapshot is a proven improvement, not a complete fix.
- Investopedia is the only currently proven source type.
- AP News and CNN Business are still unproven for clean article capture in this Lambda browser runtime.
- Reuters is only a secondary source when a direct article page loads cleanly.

## Verified-Web-Only Contract

The service now prioritizes correctness over always returning a note.

`/research` should return success only when:

- the agent obtains content from a real article page;
- the final note includes a clean `Source URL: https://...` line;
- `ingest_financial_document()` records a successful ingest with a clean `source_url`;
- the content is not a fallback/general-knowledge note.

`/research` should return `500` when:

- no verified article content was obtained;
- the page is unavailable, blocked, or drifted;
- the agent cannot record a clean source URL;
- the note looks like fallback/general knowledge;
- ingest refuses the document.

This behavior is intentional. A `500` can be a correct result when it prevents polluted content from entering S3 Vectors.

## Browser Strategy

The current browser strategy is immediate-snapshot:

1. Discover a real article URL through visible browser/search/navigation results.
2. Navigate to the article URL.
3. Immediately call `browser_snapshot`.
4. Do not click, scroll, type, or take other browser actions between navigate and snapshot.
5. If the page is `about:blank`, `about:srcdoc`, client-storage, ad-tech, interstitial, or non-article content, move to the next source.
6. Try at most three source types: Investopedia -> AP News -> CNN Business.
7. Stop if all three fail.

Why this exists:

- CloudWatch showed that pages could load briefly, then JavaScript redirected the browser into `about:blank`, `about:srcdoc`, client-storage, Optimizely, or ad-tech paths before snapshot.
- Immediate snapshot reduces that drift window.
- NVIDIA/Investopedia proved this can work in Lambda.

## Observability

`server.py` emits structured CloudWatch log lines with a shared `run_id` per request:

- `research_run phase_start`
- `research_run phase_end`
- `research_run snapshot_page_url`
- `research_run request_end`
- `research_ingest`

Important fields:

- `run_id`
- `model`
- `topic`
- `phase`
- `status`
- `duration_ms`
- `outcome`
- `ingest_success`
- `degraded_reason`
- `total_duration_ms`
- `source_url`
- `document_id`

Browser phase statuses:

- `article_captured`: response included a clean source URL and browser phase finished.
- `page_drifted`: response text contained drift markers such as `about:blank`, `about:srcdoc`, `client-storage`, `optimizely`, `doubleclick`, or `googlesyndication`.
- `ok`: browser phase completed, but runtime could not prove article capture from the phase status alone.
- `max_turns`: OpenAI Agents SDK hit turn limit.
- `error`: unexpected exception.

Request outcomes:

- `success_verified`: verified web content was ingested.
- `failed_browser`: browser or verification gate failed.
- `failed_ingest`: ingest tool returned failure.
- `failed_unknown`: classification was inconclusive.

Terminal output from `test_research.py` is a fast heuristic view. CloudWatch remains the production source of truth.

## Benchmark Topic Set

Use exactly this 5-topic set for the first model benchmark:

1. `Tesla competitive advantages`
2. `Microsoft cloud revenue growth`
3. `NVIDIA AI datacenter demand`
4. `Amazon advertising growth`
5. `Apple services revenue growth`

Do not substitute topics in the first benchmark pass. The point is to compare models against the same unstable browser/source conditions.

## Benchmark Result (2026-07-06)

The benchmark compared two models on the fixed 5-topic set under identical browser/runtime constraints:

- `openai/gpt-5.4-nano` (Model A)
- `openrouter/openai/gpt-oss-120b` (Model B)

**Recommended default: `openai/gpt-5.4-nano`**

Reason: Model A is 4.2x faster (median 26.9s vs 112.9s), verified more topics (2/5 vs 1/5), and fails cleanly with designed 500s rather than hard timeouts (0 vs 3/5). Model B's sole advantage — capturing an AP News article for the first time — does not justify its 60% timeout rate at the current Lambda 300s budget. The browser/source instability affects both models, but Model A handles it more gracefully and predictably.

Full benchmark results and CloudWatch evidence are recorded in:
`docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`

## Key Files

- `server.py`: FastAPI app, model setup, agent run orchestration, verified-web gate, phase logs.
- `context.py`: agent instructions, source preference, immediate-snapshot rule.
- `tools.py`: ingest tool, source URL validation, degraded-content rejection, ingest telemetry.
- `mcp_servers.py`: Playwright MCP setup and Chromium/container args.
- `test_research.py`: deployed end-to-end test script and terminal summary.
- `deploy.py`: Docker build, ECR push, Terraform apply, Lambda deployment.
- `Dockerfile`: Lambda container image with Playwright MCP, Chromium, uv, FastAPI, Lambda Web Adapter.
- `pyproject.toml`: uv project dependencies.

## Safe Commands

Run from `backend/researcher` unless stated otherwise.

Health check through test script:

```bash
uv run test_research.py "NVIDIA AI datacenter demand"
```

Run one benchmark topic:

```bash
uv run test_research.py "Tesla competitive advantages"
```

Deploy current code/config:

```bash
uv run deploy.py
```

Check recent Researcher logs:

```bash
aws logs tail /aws/lambda/alex-researcher --since 15m --region ap-southeast-1
```

Filter for benchmark evidence:

```bash
aws logs tail /aws/lambda/alex-researcher --since 15m --region ap-southeast-1 | rg "research_run|research_ingest|snapshot_page_url"
```

Check ingest/search after a verified success:

```bash
cd ../ingest
uv run test_search_s3vectors.py
```

Do not run `cleanup_s3vectors.py` as part of benchmark unless the user explicitly wants a clean vector store. Cleanup deletes all vectors in the index.

## Secrets And Config Safety

Do not print or summarize secret values from:

- `.env`
- `terraform.tfvars`
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `ALEX_API_KEY`

It is safe to verify non-secret fields through targeted commands, for example:

```bash
aws lambda get-function-configuration \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Environment.Variables.RESEARCHER_MODEL' \
  --output text
```

Avoid dumping full Lambda environment variables because that can expose keys.

## Known Operational Notes

- `uv run deploy.py` usually works, but Terraform AWS provider has sometimes crashed with `Plugin did not respond`.
- If Terraform crashes after image push, the known fallback is direct Lambda image update with `aws lambda update-function-code --image-uri ...`.
- Docker must be running for image build/deploy.
- The repo may contain local dirty Terraform changes. Do not overwrite them unless the user explicitly asks.
- The current scheduler interval in Terraform may differ from older guide text; scheduler behavior is not part of the model benchmark.
