# Mục đích file:
# File này là trung tâm của folder 2_sagemaker.
# Nó định nghĩa toàn bộ hạ tầng AWS cần thiết để tạo một SageMaker Serverless Endpoint
# dùng cho việc sinh vector embedding từ văn bản.
# Nói ngắn gọn: file này tạo role, model, endpoint configuration và endpoint thực tế.

terraform {
  required_version = ">= 1.5"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
  
  # Dùng local backend - state sẽ được lưu trong terraform.tfstate ngay tại thư mục này.
  # File state này đã được gitignore tự động để tránh lộ thông tin nhạy cảm.
}

provider "aws" {
  # Tất cả resource trong folder này sẽ được tạo ở region này.
  # Region này phải khớp với aws_region trong terraform.tfvars.
  region = var.aws_region
}

# Chức năng:
# Data source này không tạo resource mới.
# Nó chỉ đọc thông tin tài khoản AWS hiện tại đang chạy Terraform.
# Hữu ích khi cần kiểm tra xem bạn có đang deploy đúng account hay không.
# Đọc thông tin tài khoản AWS hiện tại.
# Hữu ích khi debug xem Terraform đang chạy bằng account nào.
data "aws_caller_identity" "current" {}

# Chức năng:
# Resource này tạo IAM role cho SageMaker sử dụng.
# SageMaker cần role này để có quyền gọi các dịch vụ AWS cần thiết khi chạy model.
# Nếu không có role hợp lệ, bước tạo model hoặc endpoint sẽ thất bại.
# IAM role để SageMaker có quyền chạy model trong tài khoản AWS của bạn.
resource "aws_iam_role" "sagemaker_role" {
  name = "alex-sagemaker-role"

  # Chức năng của assume_role_policy:
  # Đây là trust policy, quy định dịch vụ nào được phép "assume" role này.
  # Ở đây chỉ cho phép dịch vụ SageMaker dùng role.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

# Chức năng:
# Resource này gắn policy có sẵn của AWS vào IAM role vừa tạo.
# Mục đích là cấp đủ quyền để SageMaker có thể hoạt động trong guide này.
# Đây là cách nhanh và thực dụng cho môi trường học tập.
# Gắn policy managed của AWS vào role vừa tạo.
resource "aws_iam_role_policy_attachment" "sagemaker_full_access" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# Chức năng:
# Resource này khai báo "model" cho SageMaker.
# Thực tế, nó không chứa file model trong repo này.
# Nó chỉ nói cho SageMaker biết:
# - dùng container nào để chạy inference;
# - khi container khởi động thì tải model nào từ Hugging Face;
# - dùng role nào để thực thi.
# Khai báo SageMaker Model.
# Điểm dễ nhầm nhất nằm ở trường "image":
# - Đây là ECR image của Hugging Face inference container.
# - Region trong ECR URI phải cùng region với aws_region.
# - Nếu khác region, SageMaker sẽ báo lỗi:
#   "Cross region ECR image pulls are not allowed".
resource "aws_sagemaker_model" "embedding_model" {
  name               = "alex-embedding-model"
  execution_role_arn = aws_iam_role.sagemaker_role.arn

  primary_container {
    # Chức năng của image:
    # Đây là địa chỉ container inference trên Amazon ECR.
    # Container này sẽ nhận request, tải model từ Hugging Face và chạy suy luận.
    # Container này sẽ tự tải model từ Hugging Face Hub khi khởi động.
    image = var.sagemaker_image_uri
    environment = {
      # Chức năng của HF_MODEL_ID:
      # Chỉ định tên model cụ thể sẽ được container tải về từ Hugging Face Hub.
      # Model embedding nhẹ, phù hợp cho bài học và chi phí thấp.
      HF_MODEL_ID = var.embedding_model_name
      # Chức năng của HF_TASK:
      # Chỉ định loại tác vụ mà container cần thực hiện.
      # Với "feature-extraction", đầu ra sẽ là vector embedding.
      # feature-extraction = trả về vector embeddings từ text đầu vào.
      HF_TASK     = "feature-extraction"
    }
  }

  # Chức năng của depends_on:
  # Ép Terraform chỉ tạo model sau khi policy đã được gắn xong vào IAM role.
  # Điều này giúp tránh lỗi do thứ tự tạo resource chưa đúng.
  depends_on = [aws_iam_role_policy_attachment.sagemaker_full_access]
}

# Chức năng:
# Resource này định nghĩa cách endpoint sẽ chạy.
# Nó không phải endpoint thực tế, mà là "bản cấu hình" cho endpoint.
# Ở guide này, ta chọn serverless để giảm chi phí khi không có traffic.
# Cấu hình endpoint serverless.
# Ưu điểm: có thể scale-to-zero khi không có request, giúp tiết kiệm chi phí.
resource "aws_sagemaker_endpoint_configuration" "serverless_config" {
  name = "alex-embedding-serverless-config"

  production_variants {
    # Chức năng của model_name:
    # Nói cho endpoint configuration biết sẽ dùng model nào đã khai báo ở trên.
    model_name = aws_sagemaker_model.embedding_model.name
    
    serverless_config {
      # Chức năng của memory_size_in_mb:
      # Quy định lượng RAM cấp cho serverless endpoint.
      # Trên SageMaker serverless, RAM cũng ảnh hưởng tới tài nguyên CPU.
      # 3072 MB giúp container có đủ RAM/CPU để khởi động và suy luận ổn định.
      memory_size_in_mb = 3072
      # Chức năng của max_concurrency:
      # Giới hạn số request có thể xử lý đồng thời.
      # Đặt thấp giúp giảm nguy cơ chạm quota của tài khoản học viên.
      # Để thấp để tránh vượt quota của tài khoản học viên.
      max_concurrency   = 2
    }
  }
}

# Chức năng:
# Resource này không thuộc hạ tầng nghiệp vụ.
# Nó chỉ tạo một khoảng chờ cố ý trước khi tạo endpoint.
# Lý do là IAM trên AWS đôi khi cần vài giây để propagate sau khi vừa tạo/gắn policy.
# IAM trên AWS thường cần vài giây để propagate.
# Nếu tạo endpoint quá sớm, SageMaker có thể báo role chưa hợp lệ.
# time_sleep này là workaround đơn giản để giảm lỗi ngẫu nhiên lúc create endpoint.
resource "time_sleep" "wait_for_iam_propagation" {
  depends_on = [
    aws_iam_role_policy_attachment.sagemaker_full_access
  ]
  
  create_duration = "15s"
}

# Chức năng:
# Đây là endpoint thực tế mà ứng dụng sẽ gọi tới.
# Sau khi resource này tạo xong và vào trạng thái InService,
# bạn có thể dùng AWS CLI hoặc code backend để gửi text và nhận embedding.
# Endpoint thực tế sẽ được gọi bởi backend/CLI để sinh embeddings.
resource "aws_sagemaker_endpoint" "embedding_endpoint" {
  name                 = "alex-embedding-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.serverless_config.name
  
  # Chức năng của depends_on:
  # Ép Terraform chờ xong time_sleep rồi mới tạo endpoint.
  # Điều này giảm khả năng lỗi do IAM propagation chưa hoàn tất.
  depends_on = [
    time_sleep.wait_for_iam_propagation
  ]
  
}
