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
- `research_ingest`

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
- `document_id`
- `error`

Đã verify bằng CloudWatch rằng một run thực tế có cùng `run_id` xuyên suốt từ:

- `request_start`
- `browser_run`
- `request_end`

Ghi chú:

- `total_duration_ms` đã được sửa để dùng duration của `request_start`
- tránh double-count nested phase durations

### Trạng thái hiện tại của ingest observability

Trong pass `Task 2`, ingest outcome không còn chỉ phụ thuộc vào response-text heuristic.

Hiện runtime đã có thêm:

- tool-level structured log `research_ingest`
- cùng `run_id` với `research_run`
- kết quả ingest cuối được giữ lại trong request context để `request_end ingest_success=...` ưu tiên dùng dữ liệu thật từ tool nếu có

Điều này quan trọng vì trước đó:

- `request_end ingest_success` chủ yếu suy luận từ final response text
- nếu agent không nhắc rõ ingest trong output thì classification có thể thiếu chắc chắn

Sau pass này:

- `tools.py` log trực tiếp:
  - `run_id`
  - `success`
  - `topic`
  - `document_id`
  - `error`
- `server.py` chỉ fallback về text heuristic khi request không có ingest observation thực sự

Verification trên deployed Lambda ngày `2026-07-05` với topic:

- `Tesla competitive advantages`

CloudWatch đã cho thấy chuỗi khớp nhau:

- `research_ingest run_id=... success=True ... document_id=...`
- `research_run request_end run_id=... outcome=success_fallback ingest_success=True degraded_reason=page_unavailable ...`

Kết luận:

- tool-level ingest evidence tốt hơn trước
- nhưng benchmark 5-topic sau đó đã cho thấy `request_end ingest_success` vẫn có thể là `None` dù cùng run có `research_ingest success=True`

Vì vậy trạng thái chính xác hiện tại là:

- `research_ingest` là evidence mạnh
- `request_end ingest_success` đã được cải thiện nhưng **chưa hoàn toàn đáng tin trong mọi run**
- vẫn còn một gap cần follow-up trong cách request-final summary đọc lại ingest observation

## Benchmark evidence update - 2026-07-05

Trong benchmark 5 topic cố định:

- `Tesla competitive advantages`
- `Microsoft cloud revenue growth`
- `NVIDIA AI datacenter demand`
- `Amazon advertising growth`
- `Apple services revenue growth`

kết quả mới nhất là:

- 5/5 trả về `200 OK`
- 5/5 bị phân loại `success_fallback`
- 0/5 chứng minh được `success_verified`

CloudWatch pattern quan trọng:

- `Tesla` và `Apple`:
  - `browser_run max_turns`
  - `constrained_browser_run max_turns`
  - `browserless_fallback_run ok`
- `Microsoft`, `NVIDIA`, `Amazon`:
  - `browser_run ok`
  - nhưng output vẫn degraded vì direct article pages không usable

Điều này làm rõ rằng:

- browser instability hiện tại không chỉ là `MaxTurnsExceeded`
- còn có một nhóm run "browser technically completed but content quality still unusable"

Kết luận benchmark-level hiện tại:

- browser/content-access instability là root-cause direction mạnh nhất
- `EROFS` hiện chưa có evidence mới đủ mạnh để giữ làm giả thuyết chính

## Task 5 update - 2026-07-05

Trong pass `Task 5`, hướng fix được đổi sang:

- giảm browser loop pressure
- cấm degraded output kiểu đẩy việc ngược lại cho user
- ưu tiên fallback note usable hơn khi direct article pages không sạch

### Thay đổi chính

- prompt/query builder giờ bắt agent:
  - nếu 2 direct-article attempts đều fail
  - thì dừng browse
  - viết fallback note ngắn
  - ingest ngay
  - không yêu cầu user đưa link/source khác

- browser turn limits cho topic-driven run được siết:
  - `browser_run`: `15 -> 10`
  - `constrained_browser_run`: `12 -> 8`

### Kết quả quan sát được

Trong lần rerun 5 topic đầu tiên sau fix:

- CloudWatch cho thấy `browser_run status=ok` ở cả 5 topic benchmark
- không còn chain `browser_run max_turns` + `constrained_browser_run max_turns` trong sample đó
- output degraded kiểu “hãy đưa tôi link khác” biến mất
- nhiều case chuyển sang fallback note usable hơn

### Ghi chú quan trọng về classification

Task 5 tạo phrasing fallback mới như:

- `quick high-level fallback`
- `web sources blocked`
- `no clean direct article found`

nên heuristic cũ lại sinh false-positive ở vài run.

Việc này đã được vá tiếp trong:

- `server.py`
- `test_research.py`

và redeploy lại.

### Trạng thái đúng sau Task 5

- Task 5 là một cải thiện stability có ý nghĩa
- nhưng chưa phải bằng chứng rằng browser-verifiable success đã ổn định
- fallback vẫn là đường cứu chính của hệ thống

## Follow-up update: request-end ingest propagation

Sau Task 5, có một follow-up nhỏ đã được làm để xử lý đúng phần observability còn hở:

- một số run từng có:
  - `research_ingest success=True`
  - nhưng `request_end ingest_success=None`

### Fix đã áp dụng

Thay vì giữ ingest observation trong `ContextVar` kết quả cuối, runtime giờ dùng:

- map toàn cục theo `run_id`
- lock-protected read/write
- cleanup sau `request_end`

### Verification mới nhất

Run xác minh:

- `Microsoft cloud revenue growth`

CloudWatch cho cùng `run_id`:

- `research_ingest success=True`
- `request_end ingest_success=True`

### Kết luận cập nhật

Hiện tại:

- tool-level ingest evidence vẫn là source mạnh nhất
- `request_end ingest_success` đã khớp lại đúng với tool result trong run verify mới nhất
- phần observability gap này đã được thu hẹp đáng kể

## Remaining browser-content gap to carry into the next session

Verification mới nhất cho:

- `Microsoft cloud revenue growth`

cho thấy một vấn đề còn lại cần ghi rõ cho session sau:

- browser run có thể hoàn thành với `status=ok`
- nhưng vẫn không lấy được **usable article content**

CloudWatch đã cho thấy browser đi qua các path như:

- direct Investopedia URL
- `about:blank`
- CNN URL
- `about:srcdoc`
- Optimizely client-storage URL

Điều này gợi ý rằng pha cần xử lý tiếp không chỉ là:

- timeout
- fallback
- ingest

mà còn là:

- article-page validation
- redirect / interstitial / client-storage detection
- chỉ snapshot khi URL/page state vẫn còn là một article page thật

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
