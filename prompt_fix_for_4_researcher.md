Tôi là sinh viên đang học khóa học "AI in Production", và chúng ta đang làm việc trong repo của khóa học Alex.

Bạn là agent mới được giao thực hiện benchmark model cho Researcher. Trước khi làm bất kỳ thay đổi nào, hãy đọc kỹ context và tuân thủ đúng specs/plans đã chuẩn bị.

## Bắt buộc dùng superpowers

Luôn bắt đầu bằng:

- `using-superpowers`
- `brainstorming`

Sau khi đã đọc đủ context và xác nhận scope:

- Nếu thực hiện theo từng task trong plan, dùng `executing-plans` hoặc `subagent-driven-development`.
- Trước khi nói hoàn thành, dùng `verification-before-completion`.
- Nếu gặp lỗi runtime/deploy, dùng `systematic-debugging`, không đoán.

Không dùng `rich-elicitation` trừ khi còn ít nhất 2 chiều mơ hồ quan trọng, mỗi chiều có ít nhất 3 hướng hợp lý.

Hỏi tối đa 3 câu hỏi quan trọng mỗi lượt. Chỉ hỏi nếu câu trả lời làm thay đổi scope, design, test, hoặc implementation plan.

## Ngôn ngữ và phong cách

- Trả lời bằng tiếng Việt.
- Giữ technical terms bằng English khi rõ hơn.
- Không dùng emoji.
- Không in hoặc tóm tắt secret.
- Không nói "xong/pass" nếu chưa có verification mới.

## Bắt buộc đọc trước

Đọc các file sau theo thứ tự:

1. `gameplan.md`
2. `guides/architecture.md`
3. `guides/agent_architecture.md`
4. `guides/1_permissions.md`
5. `guides/2_sagemaker.md`
6. `guides/3_ingest.md`
7. `guides/4_researcher.md`
8. `backend/ingest/README.md`
9. `backend/researcher/README.md`
10. `docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md`
11. `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`

Sau đó inspect code/hạ tầng liên quan khi cần:

- `backend/researcher/server.py`
- `backend/researcher/context.py`
- `backend/researcher/tools.py`
- `backend/researcher/mcp_servers.py`
- `backend/researcher/test_research.py`
- `backend/researcher/deploy.py`
- `backend/researcher/Dockerfile`
- `terraform/4_researcher/variables.tf`
- `terraform/4_researcher/main.tf`
- `terraform/4_researcher/outputs.tf`
- `terraform/4_researcher/researcher.auto.tfvars.json`

Không đọc/in toàn bộ:

- `.env`
- `terraform/4_researcher/terraform.tfvars`
- Lambda environment variables đầy đủ
- API keys hoặc secret values

## Source of truth hiện tại

Các file source of truth cho Researcher benchmark hiện chỉ còn:

- `backend/researcher/README.md`
- `docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md`
- `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`

Các file cũ như `BUG_AND_FIX.md`, `OBSERVABILITY_AND_BENCHMARK_SPEC.md`, `session_handoff.md`, và các old researcher superpowers plan/spec đã bị xóa có chủ ý để tránh context drift.

Commit docs mới nhất đã push:

- `57d0bcd Update specs, plans researcher for gpt oss 120b`

## Trạng thái Researcher hiện tại

Tôi đang ở `guides/4_researcher.md`, Step 4: Test the Complete System.

Implementation thực tế:

- Researcher dùng Lambda Function URL, không phải App Runner.
- Researcher chạy FastAPI trong Lambda container image.
- Docker image được push lên ECR.
- Deploy script chính là `backend/researcher/deploy.py`.
- Active deployed image trước benchmark: `deploy-1783329777`.
- Model default hiện tại: `openai/gpt-5.4-nano`.
- Model cần benchmark thêm: `openrouter/openai/gpt-oss-120b`.

Browser/source state:

- Investopedia đã pass verified-web gate.
- AP News chưa pass.
- CNN Business chưa pass.
- Reuters chỉ là nguồn phụ nếu direct article page load sạch.

Benchmark topic set cố định:

1. `Tesla competitive advantages`
2. `Microsoft cloud revenue growth`
3. `NVIDIA AI datacenter demand`
4. `Amazon advertising growth`
5. `Apple services revenue growth`

Verified evidence quan trọng:

- `NVIDIA AI datacenter demand` đã có `success_verified` reproducible 2/2 ngày 2026-07-06.
- Cả 2 run dùng Investopedia article.
- Cả 2 run có `browser_run status=article_captured`.
- 4 topic còn lại vẫn fail verified-web gate như thiết kế.

## Behavior contract phải giữ nguyên

Không được thay đổi các contract này khi benchmark:

- Verified-web-only gate phải giữ nguyên.
- Fallback/general-knowledge notes không được ingest vào S3 Vectors.
- `/research` được phép trả `500` nếu không có verified web content.
- `500` do `Verified web content not obtained...` là clean failure, không phải tự động là bug.
- Không đổi source preference.
- Không đổi prompt/browser strategy.
- Không đổi max-turn strategy.
- Không đổi `/research` API contract.

Immediate-snapshot strategy hiện tại:

- Sau `browser_navigate` phải `browser_snapshot` ngay.
- Không có click/scroll/type/hành động trung gian.
- 3-source limit: Investopedia -> AP News -> CNN Business.
- Drift detection: `_detect_drifted_snapshot()` phát hiện `about:blank`, `about:srcdoc`, client-storage/ad-tech paths.
- URL extraction: `_extract_snapshot_url()` trích xuất `Source URL: https://...`.
- Browser status: `article_captured`, `page_drifted`, `ok`, `max_turns`, `error`.
- CloudWatch có `snapshot_page_url`.

## Observability cần dùng

Terminal:

- `backend/researcher/test_research.py` in `RUN SUMMARY` với `Model`, `Topic`, `Request Duration (ms)`, `Outcome`, `Degraded Signal`, `Ingest Status`.
- Terminal classifier chỉ là heuristic nhanh.

CloudWatch là source of truth:

- `research_run phase_start`
- `research_run phase_end`
- `research_run snapshot_page_url`
- `research_run request_end`
- `research_ingest`

Quan trọng nhất khi phân tích:

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

## Nhiệm vụ của bạn

Thực hiện đúng plan:

- `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`

Bắt đầu từ:

- Task 1: Preflight Current Benchmark Readiness

Sau đó tiếp tục tuần tự:

- Task 2: Verify Benchmark Results Template
- Task 3: Deploy And Verify Model A `openai/gpt-5.4-nano`
- Task 4: Run Official 5-Topic Benchmark For Model A
- Task 5: Deploy And Verify Model B `openrouter/openai/gpt-oss-120b`
- Task 6: Run Official 5-Topic Benchmark For Model B
- Task 7: Compare Models And Record Findings
- Task 8: Restore Preferred Model If Needed
- Task 9: Final Verification And Commit

Nếu có blocker thật sự, dừng và hỏi tôi trước khi sửa code/config.

## Scope rules

Được phép sửa:

- `docs/superpowers/plans/2026-07-06-researcher-model-benchmark.md`
- `docs/superpowers/specs/2026-07-06-researcher-model-benchmark-design.md` nếu phát hiện assumption benchmark sai
- `backend/researcher/README.md` để ghi final benchmark result
- `terraform/4_researcher/terraform.tfvars` chỉ để đổi `researcher_model`, nhưng không bao giờ in file này ra

Không được sửa nếu không hỏi tôi trước:

- `backend/researcher/server.py`
- `backend/researcher/context.py`
- `backend/researcher/tools.py`
- `backend/researcher/mcp_servers.py`
- `backend/researcher/test_research.py`
- `guides/4_researcher.md`
- `terraform/4_researcher/main.tf`
- `terraform/4_researcher/outputs.tf`
- `startup_prompt.md`

Lưu ý worktree hiện có thể vẫn dirty ngoài scope:

- `terraform/4_researcher/main.tf`
- `terraform/4_researcher/outputs.tf`
- `startup_prompt.md`

Không revert, không commit, không sửa các file đó trừ khi tôi yêu cầu.

## Secrets safety

Không chạy các lệnh có thể in secret như:

```bash
cat .env
cat terraform/4_researcher/terraform.tfvars
aws lambda get-function-configuration --function-name alex-researcher
```

Các lệnh safe để check model:

```bash
aws lambda get-function-configuration \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Environment.Variables.RESEARCHER_MODEL' \
  --output text
```

Các lệnh safe để check image:

```bash
sed -n '1,80p' terraform/4_researcher/researcher.auto.tfvars.json
```

## Commands chuẩn

Chạy test researcher:

```bash
cd backend/researcher
uv run test_research.py "NVIDIA AI datacenter demand"
```

Deploy researcher:

```bash
cd backend/researcher
uv run deploy.py
```

Nếu `uv run deploy.py` đã build/push image nhưng Terraform AWS provider crash với `Plugin did not respond`, dùng fallback theo plan:

```bash
aws lambda update-function-code \
  --function-name alex-researcher \
  --image-uri <ecr-image-uri> \
  --region ap-southeast-1
```

Sau đó verify Lambda:

```bash
aws lambda get-function \
  --function-name alex-researcher \
  --region ap-southeast-1 \
  --query 'Configuration.[State,LastUpdateStatus]' \
  --output text
```

Collect CloudWatch evidence:

```bash
aws logs tail /aws/lambda/alex-researcher --since 20m --region ap-southeast-1 | rg "research_run|research_ingest|snapshot_page_url"
```

## Kỳ vọng phản hồi đầu tiên của bạn

Trước khi thực hiện benchmark/deploy, hãy trả lời ngắn gọn:

1. Xác nhận bạn đã đọc source-of-truth docs.
2. Tóm tắt current runtime reality trong 5 bullet.
3. Nêu bạn sẽ bắt đầu từ Task nào trong plan.
4. Nêu blocker nếu có, tối đa 3 câu hỏi quan trọng.

Nếu không có blocker, bắt đầu Task 1 trong plan và thực hiện theo từng bước, có verification sau mỗi bước quan trọng.
