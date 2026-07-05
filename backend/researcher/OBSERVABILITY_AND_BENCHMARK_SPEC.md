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

### Trạng thái hiện tại của structured logs

Slice đầu tiên của structured observability này đã được triển khai và verify trên deployed Lambda.

Hiện đã có các event:

- `phase_start`
- `phase_end`
- `request_end`

với các field chính:

- `run_id`
- `model`
- `topic`
- `phase`
- `status`
- `duration_ms`
- `outcome`
- `ingest_success`
- `degraded_reason`

Đã verify bằng CloudWatch rằng một run thực tế có cùng `run_id` xuyên suốt từ:

- `request_start`
- `browser_run`
- `request_end`

Ghi chú:

- `total_duration_ms` đã được sửa để dùng duration của `request_start`
- tránh double-count nested phase durations

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

### Trạng thái hiện tại của terminal classification

Trong pass hiện tại, `test_research.py` đã được nâng để in:

- `Model`
- `Topic`
- `Request Duration (ms)`
- `Outcome`
- `Degraded Signal`
- `Ingest Status`

Lưu ý quan trọng:

- đây là **terminal-side heuristic classification**
- chưa phải server-side structured outcome chính thức
- classification hiện phân loại:
  - `success_verified`
  - `success_fallback`

Rule hiện tại dựa trên response text, ví dụ:

- `Quick high-level note`
- `no web research`
- `page unavailable`
- `could not verify`

sẽ bị đánh dấu là `success_fallback`.

### False-positive fix đã được xác minh

Trong một run thực tế, `Tesla competitive advantages` từng bị gắn nhầm:

- `success_verified`

mặc dù response text có dấu hiệu degraded rõ ràng.

Sau đó heuristic đã được siết lại bằng các marker bổ sung như:

- `just a moment`
- `page not found`
- `404 / unavailable`
- `access-restricted`
- `usable direct article page`
- `couldn't reliably quote`

Verification sau fix trên deployed Lambda:

- `Tesla competitive advantages`
- `Microsoft cloud revenue growth`
- `NVIDIA AI datacenter demand`

Kết quả:

- cả 3 run đều bị gắn `success_fallback`
- không còn false-positive `success_verified` trong nhóm case degraded đã kiểm tra

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
3. `NVIDIA AI datacenter demand`
4. `Amazon advertising growth`
5. `Apple services revenue growth`

Mục tiêu của bộ topic này:

- dễ so sánh giữa các lần chạy
- có đủ đa dạng
- không làm benchmark quá dài và tốn chi phí
- ưu tiên các chủ đề có xác suất cao tìm được direct article page sạch hơn trong Lambda runtime hiện tại

## Bộ source ưu tiên cho benchmark stability

Để tránh đánh đồng lỗi source-access với lỗi model/runtime, benchmark vòng đầu nên ưu tiên:

1. `Investopedia`
2. `AP News`
3. `CNN Business`

`Reuters` chỉ nên dùng như nguồn phụ khi một direct article page tải sạch, không bị:

- captcha
- access restriction
- ad/interstitial churn

Không dùng homepage hoặc market portal làm điểm vào benchmark đầu vì chúng tạo quá nhiều nhiễu cho Lambda headless browser.

## Trạng thái xác minh hiện tại

Trong đợt kiểm tra ngày `2026-07-05`, source preference này đã được áp vào runtime và kiểm tra lại trên Lambda deploy thật.

Đã chạy:

- `Tesla competitive advantages`
- `Microsoft cloud revenue growth`
- `NVIDIA AI datacenter demand`

Kết quả xác minh:

- cả 3 request đều trả về `200 OK`
- CloudWatch cho thấy Researcher thực sự đã cố đi theo source set mới:
  - Investopedia cho Tesla
  - CNN article path cho NVIDIA
  - stable-source attempts cho Microsoft

Tuy nhiên, source set sạch hơn **chưa đủ** để biến browser path thành ổn định hoàn toàn.

Các failure mode vẫn còn thấy trong log:

- `about:blank` churn
- browser max-turn fallback
- direct article page mở được nhưng không luôn trích xuất được nội dung usable

Vì vậy spec benchmark hiện tại nên được hiểu như sau:

- bộ source này là **best-effort stable set**
- không phải bằng chứng rằng browser verification đã được giải quyết triệt để

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
