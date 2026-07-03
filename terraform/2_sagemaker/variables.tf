# Mục đích file:
# File này khai báo các biến đầu vào dùng cho folder 2_sagemaker.
# Nó giúp tách phần "giá trị có thể thay đổi theo người dùng/region"
# ra khỏi phần logic hạ tầng trong main.tf.

# Chức năng:
# Biến này xác định AWS region sẽ dùng để tạo resource.
# Hầu hết các lỗi deploy trong guide này đều nên bắt đầu bằng việc kiểm tra region này.
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
}

# Chức năng:
# Biến này chứa URI của Hugging Face inference container trên Amazon ECR.
# Đây là container mà SageMaker sẽ chạy để phục vụ inference.
# Không nên nhầm biến này với tên model trên Hugging Face.
variable "sagemaker_image_uri" {
  description = "URI of the SageMaker container image"
  type        = string
  # Lưu ý:
  # - Giá trị này phải trùng region với aws_region.
  # - Hiện tại default đang để sẵn cho ap-southeast-1.
  # - Nếu đổi sang region khác, hãy override trong terraform.tfvars.
  #
  # Ví dụ nếu deploy ở us-east-1:
  # sagemaker_image_uri = "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
  default     = "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
}

# Chức năng:
# Biến này chỉ định model embedding cụ thể sẽ được tải từ Hugging Face Hub.
# Trong guide này, model được chọn là all-MiniLM-L6-v2 vì nhẹ, rẻ và đủ tốt cho bài học.
variable "embedding_model_name" {
  description = "Name of the HuggingFace model to use"
  type        = string
  # all-MiniLM-L6-v2 tạo vector 384 chiều, nhẹ và hợp với bài này.
  default     = "sentence-transformers/all-MiniLM-L6-v2"
}
