# Researcher Observability, Stability Fix, and Model Benchmark Spec

## Mục tiêu

Spec này mô tả hướng cải tiến cho Researcher ở Part 4 theo thứ tự ưu tiên đúng:

1. **Fix bug instability trước**
2. **Thêm observability để đo được vấn đề**
3. **Sau đó mới benchmark model**

Vấn đề hiện tại không chỉ là chậm hay nhanh.
Vấn đề cốt lõi là:

- Researcher chạy **lúc được lúc không**
- cùng một flow nhưng có lúc:
  - research thành công
  - fallback
  - placeholder
  - hoặc fail do browser/tool/filesystem

Vì vậy benchmark model chỉ có ý nghĩa sau khi:

- có khả năng quan sát rõ từng phase
- phân loại đúng outcome
- và có đủ evidence để biết lỗi nằm ở đâu

## Phạm vi của giai đoạn này

Giai đoạn này **không sửa** `guides/4_researcher.md`.

Giai đoạn này tập trung vào:

- instrumentation trong service
- terminal-friendly output trong script test
- quy trình benchmark có kỷ luật
- tài liệu hướng dẫn cách chạy và cách đọc kết quả

## Kết quả mong muốn

Sau giai đoạn này, mỗi lần chạy Researcher cần trả lời được các câu hỏi:

1. Run này đang dùng model nào?
2. Topic nào đang được chạy?
3. Tổng thời gian mất bao lâu?
4. Từng phase mất bao lâu?
5. Run này là:
   - success thật
   - success fallback
   - degraded placeholder
   - hay fail
6. Ingest có thành công không?
7. Nếu fail, fail ở:
   - browser
   - agent
   - ingest
   - hay lỗi khác

## Nguyên tắc thực hiện

### 1. Stability-first

Mọi thay đổi phải phục vụ việc trả lời câu hỏi:

- vì sao Researcher lúc được lúc không?

Không đi thẳng vào tối ưu benchmark trước khi biết:

- run nào là run tốt
- run nào là degraded
- run nào fail thật

### 2. Observability-first

CloudWatch là nguồn production quan trọng, nhưng không đủ tiện để quan sát nhanh.

Vì vậy cần hai lớp quan sát song song:

- **CloudWatch structured logs**
- **Terminal-friendly output** trong `test_research.py`

### 3. Benchmark only after observability

So sánh `gpt-oss-120b` và `gpt-5.4-nano` chỉ bắt đầu sau khi:

- instrumentation đã có
- outcome đã được chuẩn hóa
- terminal output đủ rõ để nhìn run nào tốt/xấu

## Thiết kế observability

## 1. Structured logs trong service

Thêm structured logging vào `backend/researcher/server.py`.

Mỗi run cần có:

- `run_id`
- `model`
- `topic`
- `phase`
- `status`
- `duration_ms`
- `outcome`
- `ingest_success`
- `error_type`

### Phase chuẩn hóa

Các phase giai đoạn đầu:

- `request_start`
- `browser_run`
- `constrained_browser_run`
- `browserless_fallback_run`
- `ingest_attempt`
- `request_end`

### Outcome chuẩn hóa

Các outcome giai đoạn đầu:

- `success_verified`
- `success_fallback`
- `failed_browser`
- `failed_ingest`
- `failed_agent`
- `failed_unknown`

Ghi chú:

- `success_verified` dùng cho run có research usable theo flow chính
- `success_fallback` dùng cho run phải đi qua fallback nhưng vẫn lưu được kết quả
- placeholder note hoặc degraded content cần được nhận diện rõ để không bị hiểu nhầm là success chất lượng cao

## 2. Terminal-friendly output

`backend/researcher/test_research.py` sẽ được cải tiến để hiển thị rõ hơn.

Mục tiêu:

- không cần mở CloudWatch vẫn hiểu được run vừa rồi có đáng tin không

Script cần in rõ:

- service URL
- model đang chạy
- topic đang test
- total duration
- outcome cuối
- ingest success hay không
- ghi chú nếu đây là fallback/degraded result

Terminal output phải giúp phân biệt nhanh:

- run thành công thật
- run thành công nhưng fallback
- run thành công nhưng nội dung placeholder
- run fail

## 3. Quan hệ giữa terminal logs và CloudWatch

Terminal là nơi quan sát nhanh.

CloudWatch là nơi kiểm tra sâu hơn khi cần evidence production.

Nguyên tắc đọc:

- terminal dùng để biết ngay run nào đáng xem
- CloudWatch dùng để soi phase cụ thể và tìm root cause

Người dùng có thể gửi lại:

- terminal output
- CloudWatch logs
- OpenAI traces

để phân tích tiếp.

## Thiết kế fix bug trước benchmark

## Bug cần xử lý trước

Vấn đề bắt buộc ưu tiên là:

- Researcher chạy lúc được lúc không

Biểu hiện đã quan sát:

- browser loop
- `MaxTurnsExceeded`
- captcha/interstitial/ad noise
- placeholder result
- `EROFS` / read-only filesystem trong browser snapshot path

### Mục tiêu của fix giai đoạn đầu

Chưa nhất thiết phải giải quyết triệt để mọi nguyên nhân ngay trong bước đầu.

Mục tiêu trước tiên là:

1. xác định run nào fail do browser
2. xác định run nào đi fallback
3. xác định run nào placeholder/degraded
4. xác định run nào ingest fail
5. xác định run nào success thật

Sau khi đã quan sát được rõ, mới bắt đầu sửa root cause theo evidence.

### Thứ tự ưu tiên xử lý

1. làm rõ failure taxonomy
2. đo thời gian từng phase
3. nhận diện placeholder/degraded result
4. gom evidence đủ để truy ra root cause
5. sửa bug instability
6. chỉ sau đó mới benchmark model nghiêm túc

## Thiết kế benchmark model

Benchmark được thực hiện **sau khi** observability đã đủ dùng.

## Cách benchmark

Chọn cách:

- deploy từng model riêng
- rồi chạy cùng một bộ topic cố định

Lý do:

- sát production Lambda runtime nhất
- công bằng hơn local benchmark
- phản ánh đúng điều kiện có browser/MCP/fallback thật

## Models cần so sánh

Giai đoạn đầu tập trung vào:

- `openrouter` với `gpt-oss-120b`
- `openai/gpt-5.4-nano`

## Bộ topic cố định

Chạy 5 topic ngắn, thực dụng:

1. `Tesla competitive advantages`
2. `Microsoft cloud revenue growth`
3. `NVIDIA AI chip demand`
4. `Oil price outlook`
5. `Bitcoin ETF inflows`

Mục tiêu của bộ topic này:

- dễ so sánh giữa các lần chạy
- có đủ đa dạng
- không làm benchmark quá dài và tốn chi phí

## Chỉ số so sánh vòng đầu

Giai đoạn benchmark đầu chỉ cần các chỉ số đủ dùng:

- total duration
- phase durations
- success rate
- fallback rate
- degraded/placeholder rate
- ingest success rate

Không cần đánh giá chất lượng nội dung quá sâu ở vòng đầu.

Mục tiêu trước tiên là:

- tốc độ
- độ ổn định
- hành vi fallback

## Các file dự kiến bị ảnh hưởng

### Application code

- `backend/researcher/server.py`
- `backend/researcher/test_research.py`
- có thể thêm một file markdown hướng dẫn benchmark trong `backend/researcher`

### Tài liệu

- thêm file markdown này
- có thể thêm một file hướng dẫn chạy benchmark riêng nếu cần

## Những gì chưa làm trong giai đoạn này

Các việc sau chưa nằm trong scope hiện tại:

- sửa `guides/4_researcher.md`
- redesign API `/research`
- làm streaming response
- tạo persistence layer riêng cho benchmark results
- xây full experiment dashboard

## Hướng implementation kế tiếp

Sau khi spec này được duyệt, bước tiếp theo là lập implementation plan theo thứ tự:

1. thêm structured logs và phase timings
2. thêm terminal-friendly output
3. chuẩn hóa outcome classification
4. xác nhận observability đủ để đọc instability
5. fix bug instability theo evidence
6. deploy model A
7. chạy benchmark 5 topic
8. deploy model B
9. chạy lại benchmark 5 topic
10. tổng hợp so sánh

## Tóm tắt quyết định đã chốt

- Hướng chính: `Observability-first`
- Mức đo: `Step-level tracing`
- Guide 4: **giữ nguyên**, chưa sửa
- Tài liệu giai đoạn này: viết trong `backend/researcher`
- Observability:
  - CloudWatch
  - terminal-friendly logs
- Benchmark:
  - deploy từng model riêng
  - dùng bộ 5 topic cố định
- Ưu tiên cao nhất:
  - **fix bug instability trước**
  - benchmark sau
