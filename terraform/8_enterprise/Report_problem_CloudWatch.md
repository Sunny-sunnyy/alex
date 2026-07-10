# Báo cáo sự cố CloudWatch Dashboard Part 8

## Bối cảnh

Alex Agent Orchestra chạy OpenAI qua LiteLLM, không còn dùng Bedrock/Nova. Ban đầu, Terraform Part 8 vẫn có dashboard theo dõi metric `AWS/Bedrock`, nên không phản ánh inference thực tế của năm Lambda agents.

Region triển khai: `ap-southeast-1`.

## Vấn đề gặp phải

### 1. Dashboard Bedrock không phù hợp runtime OpenAI

Dashboard `alex-ai-model-usage` chứa các widget Bedrock cho invocations, tokens và latency. Vì agents gọi OpenAI qua LiteLLM, các widget này không có dữ liệu hữu ích.

### 2. Logs Insights widgets chỉ hiển thị bảng log

Lần thay thế đầu tiên dùng widget `type = "log"` để hiển thị model, timing và errors. Đây là hành vi đúng của log widget: nó hiển thị bảng event logs, không phải metric chart.

### 3. Logs Insights time series không ổn định trên dashboard

Đã thử parse log `[TIMING] lambda_handler TOTAL` và aggregate theo `bin(5m)` để tạo time series.

- API `aws logs start-query` trả về 67 datapoints latency trong 72 giờ, chứng minh log và regex parse có dữ liệu.
- CloudWatch dashboard vẫn báo `This data is not suitable for visualizing`.
- Cú pháp `SOURCE logGroups(namePrefix: [...])` chạy qua `StartQuery` API nhưng dashboard báo `Invalid NamePrefix`.
- Cú pháp `SOURCE '/aws/lambda/...'` từng hiển thị bảng log trong dashboard, nhưng không giải quyết được việc visualizing latency ổn định.

Kết luận: không dùng Logs Insights widget để làm biểu đồ latency/model cho dashboard này.

### 4. Reporter Judge không có log runtime

Query trực tiếp 72 giờ trên `/aws/lambda/alex-reporter` không tìm thấy event chứa `Judge:`. Vì không có runtime event, widget `Reporter Judge Guardrail Logs` luôn hiển thị `No data found`.

### 5. Lỗi LiteLLM riêng biệt

CloudWatch có các lỗi từ Charter:

```text
RuntimeError: Queue ... is bound to a different event loop
```

Đây là lỗi runtime của LiteLLM `LoggingWorker`, không phải lỗi dashboard. Dashboard `Agent Error Count` hiện giúp quan sát lỗi này. Chưa thay đổi code Lambda để xử lý lỗi đó trong phạm vi Part 8.

## Giải pháp cuối cùng

Dashboard `alex-ai-model-usage` dùng các metric native `AWS/Lambda`, vì chúng luôn được CloudWatch cung cấp và hiển thị time series ổn định:

1. `OpenAI Agent Latency (Current Model Configuration)`
   - Metric: `AWS/Lambda` `Duration`
   - Statistic: `Average`
   - Labels hiển thị agent cùng model cấu hình hiện tại.

2. `Agent Error Count`
   - Giữ Logs Insights aggregation đang hoạt động.
   - Theo dõi `ERROR`, `FAILED`, và `Traceback` của năm agent.

3. `OpenAI Agent Invocations (Current Model Configuration)`
   - Metric: `AWS/Lambda` `Invocations`
   - Statistic: `Sum`
   - Labels hiển thị agent cùng model cấu hình hiện tại.

4. Giữ hai widget SageMaker endpoint để quan sát embedding service.

Lưu ý: label model trên Lambda charts là model configuration hiện tại, không phải dimension metric do AWS phát hành. Để có token usage, cost, latency chính xác theo từng OpenAI model, cần LangFuse/OpenAI observability hoặc custom CloudWatch metrics từ code Lambda.

## Files đã thay đổi

| File | Thay đổi |
| --- | --- |
| `main.tf` | Bỏ widgets Bedrock; thêm Lambda Duration/Invocations charts, Logs Insights error chart và giữ SageMaker widgets. |
| `variables.tf` | Bỏ `bedrock_region` và `bedrock_model_id`. |
| `terraform.tfvars.example` | Chỉ giữ `aws_region = "ap-southeast-1"`; không đưa OpenAI keys/model IDs vào Terraform. |
| `outputs.tf` | Cập nhật hướng dẫn dashboard theo OpenAI/LiteLLM. |
| `.terraform.lock.hcl` | Thêm checksum provider AWS khi chạy `terraform init` trên môi trường hiện tại. |
| `Report_problem_CloudWatch.md` | Báo cáo này. |

## Xác minh và triển khai

Các lệnh đã chạy trong `terraform/8_enterprise`:

```bash
terraform init
terraform validate
terraform plan
terraform apply -auto-approve
```

Kết quả cuối:

```text
Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
```

Hai dashboards hiện có:

- `alex-ai-model-usage`
- `alex-agent-performance`

Lần kiểm tra Terraform sau deploy trước đó báo `No changes`, xác nhận infrastructure khớp với configuration tại thời điểm kiểm tra.

## Giới hạn còn lại

- CloudWatch không có metric native cho OpenAI API calls qua LiteLLM.
- Lambda metric lịch sử có thể bao gồm invocation trước khi model configuration được đổi; labels dashboard mô tả configuration hiện tại.
- Reporter Judge chỉ nên được đưa trở lại dashboard khi Lambda runtime thực sự emit structured Judge logs.
- Lỗi LiteLLM event-loop cần được điều tra và xử lý riêng ở code/packaging của Charter.
