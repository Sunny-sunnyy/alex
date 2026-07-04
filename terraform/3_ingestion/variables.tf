# File này khai báo các input variable cho toàn bộ Part 3.
# Terraform không triển khai được nếu thiếu các đầu vào cơ bản này.
# Hai biến ở đây quyết định region hoạt động và endpoint embedding mà Lambda sẽ gọi tới.
variable "aws_region" {
  # Khai báo một biến đầu vào tên aws_region cho toàn module Terraform này.
  description = "AWS region for resources"
  # Mô tả biến để người đọc và Terraform UI hiểu mục đích sử dụng.
  type        = string
  # Ép kiểu dữ liệu của biến phải là chuỗi.
}

# Biến này là cầu nối giữa Part 2 và Part 3.
# Lambda ingest không tự biết endpoint embedding nào cần dùng.
# Vì vậy tên endpoint từ thư mục terraform/2_sagemaker phải được truyền vào đây.
variable "sagemaker_endpoint_name" {
  # Khai báo biến đầu vào chứa tên endpoint embedding đã deploy trước đó.
  description = "Name of the SageMaker endpoint from Part 2"
  # Mô tả rõ đây là endpoint đến từ Part 2.
  type        = string
  # Kiểu dữ liệu là chuỗi vì tên endpoint trong AWS là string.
}
