
# Mục đích file:
# File này khai báo các giá trị Terraform sẽ in ra sau khi deploy xong.
# Các output này giúp bạn lấy nhanh thông tin quan trọng mà không cần mở AWS Console.

# Chức năng:
# Output này trả về tên endpoint vừa tạo.
# Đây là giá trị quan trọng nhất để copy vào file .env cho các bước tiếp theo.
output "sagemaker_endpoint_name" {
  description = "Name of the SageMaker endpoint"
  # Tên endpoint này sẽ được copy vào file .env để backend dùng ở các bước sau.
  value       = aws_sagemaker_endpoint.embedding_endpoint.name
}

# Chức năng:
# Output này trả về ARN đầy đủ của endpoint.
# Thường dùng khi debug, audit, hoặc cần tham chiếu chính xác resource trong AWS.
output "sagemaker_endpoint_arn" {
  description = "ARN of the SageMaker endpoint"
  # ARN hữu ích khi cần debug trên AWS Console hoặc tham chiếu qua CLI.
  value       = aws_sagemaker_endpoint.embedding_endpoint.arn
}

# Chức năng:
# Output này chỉ in ra một đoạn hướng dẫn ngắn sau khi apply thành công.
# Nó không tạo resource nào, chỉ giúp người học nhớ bước tiếp theo cần làm.
output "setup_instructions" {
  description = "Instructions for setting up environment variables"
  # Output này chỉ để nhắc việc sau deploy; không ảnh hưởng tới resource AWS nào.
  value = <<-EOT
    
    ✅ SageMaker endpoint deployed successfully!
    
    Follow the instructions in the guide to update your .env file and test the endpoint.
  EOT
}
