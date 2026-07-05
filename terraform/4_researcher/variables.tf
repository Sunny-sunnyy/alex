# File này khai báo toàn bộ input variables cho Part 4.
# Các biến ở đây điều khiển region, secret, model, image URI và scheduler behavior.
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
}

# API key này chủ yếu phục vụ OpenAI Agents tracing và các runtime OpenAI model.
variable "openai_api_key" {
  description = "OpenAI API key for the researcher agent"
  type        = string
  sensitive   = true
}

# Endpoint ingest từ Part 3 để researcher có thể lưu kết quả vào knowledge base.
variable "alex_api_endpoint" {
  description = "Alex API endpoint from Part 3"
  type        = string
}

# Biến này giữ chỗ cho cấu hình OpenRouter nếu muốn dùng provider đó về sau.
variable "openrouter_api_key" {
    description = "OpenRouter API key for the researcher agent"
    type        = string
    sensitive   = true
  }

# API key này dùng để gọi API Gateway ingest của Part 3.
variable "alex_api_key" {
  description = "Alex API key from Part 3"
  type        = string
  sensitive   = true
}

# Cờ này bật hoặc tắt automated research theo lịch.
variable "scheduler_enabled" {
  description = "Enable automated research scheduler"
  type        = bool
  default     = false
}

# Image URI là tín hiệu để Terraform biết researcher image đã được build/push xong.
variable "researcher_image_uri" {
  description = "Full ECR image URI for the researcher Lambda container"
  type        = string
  default     = ""
}

# Biến này giữ region inference cho nhánh Bedrock hoặc môi trường AWS liên quan.
variable "bedrock_region" {
  description = "AWS region used for Bedrock model inference"
  type        = string
  default     = "ap-southeast-1"
}

# Đây là model researcher hiện tại hoặc model override từ môi trường deploy.
variable "researcher_model" {
  description = "Bedrock model identifier used by the researcher"
  type        = string
  default     = "openai/gpt-5.4-nano"
}

# MCP logging dùng kiểu string để khớp với logic runtime hiện tại.
variable "mcp_logging" {
  description = "Set to exact string True to enable researcher MCP logging"
  type        = string
  default     = "False"
}
