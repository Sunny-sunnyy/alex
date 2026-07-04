# File output này in ra các giá trị quan trọng sau khi Part 3 deploy xong.
# Đây là nơi Terraform "bàn giao" thông tin để người học mang sang .env.
# Những output này cũng giúp kiểm tra nhanh deployment mà không cần mở AWS Console.
output "vector_bucket_name" {
  # Khai báo output tên vector_bucket_name để lộ ra tên bucket vừa tạo.
  description = "Name of the S3 Vectors bucket"
  # Mô tả ngắn gọn nội dung của output này.
  value       = aws_s3_bucket.vectors.id
  # Trả về id của bucket, thực tế cũng chính là bucket name trong resource này.
}

# URL này là endpoint hoàn chỉnh mà client có thể POST document vào.
output "api_endpoint" {
  # Khai báo output chứa URL ingest public sau khi stage prod được tạo.
  description = "API Gateway endpoint URL"
  # Mô tả rằng đây là endpoint của API Gateway.
  value       = "${aws_api_gateway_stage.api.invoke_url}/ingest"
  # Ghép invoke_url của stage prod với path /ingest để ra URL dùng thật.
}

# Output này cho ID của API key, thường dùng khi cần gọi lệnh AWS CLI để lấy value thật.
output "api_key_id" {
  # Khai báo output chứa ID của API key do API Gateway sinh ra.
  description = "API Key ID"
  # Mô tả ngắn gọn ý nghĩa của output.
  value       = aws_api_gateway_api_key.api_key.id
  # Trả về key id để người dùng có thể gọi aws apigateway get-api-key.
}

# API key value được đánh dấu sensitive để Terraform hạn chế in lộ ra ngoài một cách vô ý.
output "api_key_value" {
  # Khai báo output chứa giá trị key thật.
  description = "API Key value (sensitive)"
  # Mô tả đây là giá trị API key.
  value       = aws_api_gateway_api_key.api_key.value
  # Trả về key value do API Gateway quản lý.
  sensitive   = true
  # Đánh dấu output là sensitive để Terraform ẩn bớt khi hiển thị.
}

# Đây là output dạng "hướng dẫn thao tác tiếp theo".
# Nó rất hữu ích cho người học vì tổng hợp ngay các bước cần copy vào .env và lệnh test API.
output "setup_instructions" {
  # Khai báo output văn bản hướng dẫn sau triển khai.
  description = "Instructions for setting up environment variables"
  # Mô tả rằng output này mang tính hướng dẫn thao tác.
  value = <<-EOT
    # Bắt đầu heredoc nhiều dòng để Terraform in nguyên khối hướng dẫn.
    
    ✅ Ingestion pipeline deployed successfully!
    # Dòng xác nhận triển khai thành công.
    
    Add the following to your .env file:
    # Nhắc người học cập nhật các biến môi trường local.
    VECTOR_BUCKET=${aws_s3_bucket.vectors.id}
    # Chèn trực tiếp tên bucket vào hướng dẫn.
    ALEX_API_ENDPOINT=${aws_api_gateway_stage.api.invoke_url}/ingest
    # Chèn trực tiếp URL endpoint ingest vào hướng dẫn.
    
    To get your API key value:
    # Hướng dẫn cách lấy giá trị API key thật qua AWS CLI.
    aws apigateway get-api-key --api-key ${aws_api_gateway_api_key.api_key.id} --include-value --query 'value' --output text
    # Lệnh CLI dùng key id vừa tạo để lấy key value.
    
    Then add to .env:
    # Nhắc người học bổ sung key value vào .env.
    ALEX_API_KEY=<the-api-key-value>
    # Placeholder để người học tự thay bằng giá trị thật.
    
    Test the API:
    # Gợi ý một lệnh curl kiểm tra endpoint sau khi cấu hình xong.
    curl -X POST ${aws_api_gateway_stage.api.invoke_url}/ingest \
      -H "x-api-key: <your-api-key>" \
      -H "Content-Type: application/json" \
      -d '{"content": "Test document", "metadata": {"source": "test"}}'
    # Lệnh curl mẫu để gửi request kiểm tra luồng ingest.
  EOT
  # Kết thúc khối heredoc nhiều dòng.
}
