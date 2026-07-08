# Part 6 README Design Spec

## Mục tiêu

Tạo bộ README tiếng Việt cho các folder chính thuộc `guides/6_agents.md` để người học có thể đọc code trước khi học guide chính thức. Bộ tài liệu phải phản ánh trung thực implementation hiện tại của repo, đồng thời bổ sung hướng dẫn rõ ràng về cách chuyển từ cấu hình Bedrock hiện tại sang OpenAI models như `openai/gpt-5.4-nano` và `openai/gpt-5.4-mini`.

Phạm vi của đợt tài liệu này chỉ là document. Không sửa code, không sửa Terraform, không đổi env thật trong repo ở bước này.

## Phạm vi

Sẽ tạo README cho đúng 6 folder:

1. `backend/tagger`
2. `backend/reporter`
3. `backend/charter`
4. `backend/retirement`
5. `backend/planner`
6. `terraform/6_agents`

Ngoài ra, các file cross-cutting ở `backend/`:

- `package_docker.py`
- `deploy_all_lambdas.py`
- `test_simple.py`
- `test_full.py`
- `test_multiple_accounts.py`
- `test_scale.py`
- `watch_agents.py`

sẽ chỉ được mô tả tập trung trong `backend/planner/README.md` như folder đại diện, thay vì tách thêm README khác.

## Source Of Truth

Khi guide text và code lệch nhau, bộ README này sẽ lấy:

1. code hiện tại trong `backend/*`
2. README cục bộ hiện có nếu còn đúng
3. Terraform hiện tại trong `terraform/6_agents`

làm source of truth chính.

Guide `6_agents.md` chỉ được dùng để bổ sung bối cảnh học tập, không được phép ghi đè implementation thực tế.

## Bối cảnh kỹ thuật đã xác nhận

- Part 6 hiện triển khai 5 agent Lambda: planner, tagger, reporter, charter, retirement.
- `terraform/6_agents` vẫn đặt biến và env theo naming Bedrock như `BEDROCK_MODEL_ID` và `BEDROCK_REGION`.
- Các agent Part 6 hiện khởi tạo model qua `LitellmModel(model=f"bedrock/{model_id}")`.
- `OPENAI_API_KEY` hiện đã có trong Terraform/Lambda env nhưng chủ yếu phục vụ observability và LangFuse export, không phải luồng model chính.
- Người dùng muốn README giải thích rõ cách chuyển provider/model sang OpenAI, nhưng chưa muốn sửa source thật.

## Mục tiêu nội dung của từng README

### 1. README cho từng backend agent

Mỗi file sẽ bám `prompt_readme_backend.md` và phải có:

- vai trò của folder trong Alex và trong Part 6
- cây thư mục ASCII
- sơ đồ kiến trúc mermaid
- mô tả file-by-file, ưu tiên file core và test
- sequence diagram cho luồng xử lý chính
- sơ đồ import/call giữa các file
- quan hệ với folder khác và các part trước liên quan trực tiếp
- cách chạy test/build/deploy nhanh
- bảng tóm tắt file

### 2. README cho `terraform/6_agents`

File này sẽ bám `prompt_readme_terraform.md` và phải có:

- sơ đồ tài nguyên AWS
- bảng tài nguyên chi tiết
- tổng hợp IAM role/policy
- tổng hợp environment variables
- outputs
- variables cần điền trong `terraform.tfvars`
- version constraints
- quan hệ với các part khác
- cách dùng nhanh
- checklist tài nguyên cuối file

## Chiến lược trình bày migration sang OpenAI models

Mỗi README backend và README Terraform sẽ có một section riêng:

`Cách chuyển sang OpenAI models`

Section này phải tuân theo các nguyên tắc sau:

1. Không giả vờ repo đã migrate.
2. Nêu rõ current state đang là Bedrock-centric.
3. Chỉ ra đúng file nào cần đổi nếu người dùng muốn migrate thật.
4. Tạm giữ tên biến cũ như `BEDROCK_MODEL_ID` và `BEDROCK_REGION` để giảm churn, đúng theo quyết định của user.
5. Phân biệt rõ:
   - đổi provider/model trong code
   - đổi giá trị env trong Lambda/Terraform
   - đổi narrative trong docs để tránh hiểu nhầm

## Mapping model đề xuất trong README

README sẽ khuyến nghị model theo nhiệm vụ như sau:

| Folder | Model khuyến nghị | Lý do |
|---|---|---|
| `backend/tagger` | `openai/gpt-5.4-mini` | Structured classification, scope hẹp, cần ổn định |
| `backend/reporter` | `openai/gpt-5.4-nano` | Có tool usage và viết report, ưu tiên cost trước; có thể nâng lên `mini` nếu chất lượng chưa đủ |
| `backend/charter` | `openai/gpt-5.4-mini` | Tạo JSON chart payload có cấu trúc, cần output ổn định |
| `backend/retirement` | `openai/gpt-5.4-mini` | Reasoning và khuyến nghị tài chính phức tạp hơn |
| `backend/planner` | `openai/gpt-5.4-mini` | Orchestration quan trọng, cần quyết định ổn định hơn `nano` |

`terraform/6_agents/README.md` sẽ tổng hợp mapping này ở góc nhìn hạ tầng/env.

## Phạm vi hướng dẫn migrate trong README

README sẽ chỉ rõ, ở mức document, các điểm đổi sau nếu migrate:

### Backend

- các file `agent.py` của từng agent:
  - cách đổi `LitellmModel(model=f"bedrock/{model_id}")`
  - cách xử lý nếu chuyển sang model string trực tiếp như `openai/gpt-5.4-mini`
  - cách xem lại logic `AWS_REGION_NAME` khi không còn dùng Bedrock
- các file hỗ trợ như `judge.py` của reporter nếu có dùng model riêng
- các test nếu đang in/log thông tin Bedrock

### Terraform

- `terraform/6_agents/main.tf`
  - environment variables hiện inject cho từng Lambda
  - chỗ nào vẫn đang assume Bedrock
  - IAM policy Bedrock có thể bỏ hoặc giữ tạm
- `terraform/6_agents/variables.tf`
  - các biến như `bedrock_model_id`, `bedrock_region`, `openai_api_key`
- `terraform/6_agents/outputs.tf`
  - kiểm tra xem output nào cần đổi narrative theo provider mới
- `terraform/6_agents/terraform.tfvars.example`
  - cách đổi giá trị mẫu sang OpenAI-centric nhưng vẫn giữ tên biến cũ ở giai đoạn đầu

## Cách chia trọng tâm giữa các README

Để tránh lặp quá nhiều:

- `backend/planner/README.md` sẽ là README backend đầy đủ nhất, vì:
  - planner là orchestrator
  - planner đại diện giải thích các script cross-cutting ở `backend/`
  - planner là nơi phù hợp nhất để neo tổng quan Part 6
- các README agent còn lại vẫn tự chứa, nhưng phần cross-cutting sẽ chỉ link sang README planner
- `terraform/6_agents/README.md` sẽ là nơi giải thích migration ở tầng infra tập trung nhất

## Giới hạn độ dài

Mục tiêu mặc định:

- mỗi README dưới 600 dòng
- nếu có folder quá nặng, ưu tiên cô đọng bằng bảng và diagram thay vì kéo dài prose

Kỳ vọng thực tế:

- `backend/planner/README.md` có nguy cơ dài nhất nhưng vẫn phải cố giữ dưới 600 dòng
- `terraform/6_agents/README.md` có thể dài do nhiều resource, nhưng sẽ gom resource phụ thành bảng tổng hợp

Nếu trong quá trình viết có README vượt 600 dòng mà không thể rút thêm mà vẫn giữ giá trị học tập, sẽ dừng lại xin phép user trước khi ghi file đó.

## Trình tự thực hiện ở pha implementation

1. Đọc toàn bộ code trong từng folder backend Part 6 theo prompt.
2. Đọc `terraform/6_agents/*`.
3. Đọc các part trước có dependency trực tiếp:
   - guide 3, 4, 5, 6
   - `backend/database`
   - `backend/ingest`
   - `backend/researcher`
   - `terraform/3_ingestion`
   - `terraform/4_researcher`
   - `terraform/5_database`
4. Xác định biến môi trường, entry points, workflow, dependency graph.
5. Soạn từng README bằng tiếng Việt.
6. Tự kiểm tra line count, consistency, placeholder, và độ trung thực với code.

## Ngoài phạm vi

Những việc sau chưa nằm trong đợt này:

- sửa code để dùng OpenAI thật
- sửa Terraform để đổi provider thật
- chạy test xác minh migration OpenAI
- cập nhật guide `6_agents.md`
- tạo README cho folder ngoài 6 folder đã chốt

## Tiêu chí hoàn thành

Đợt này được coi là hoàn thành khi:

- có spec được user review và chấp thuận
- sau đó mới bắt đầu tạo README
- mỗi README phản ánh đúng current state
- mỗi README có section migration sang OpenAI models
- `backend/planner/README.md` bao phủ luôn các script cross-cutting ở `backend/`
- `terraform/6_agents/README.md` chỉ rõ phần backend nào nó deploy và các env/IAM/resource liên quan
