# File Terraform này là trung tâm của Part 3.
# Nó dựng toàn bộ ingestion pipeline cơ bản:
# - bucket dữ liệu cho phần vector storage trong implementation hiện tại của repo,
# - IAM role/policy cho Lambda ingest,
# - Lambda function alex-ingest,
# - API Gateway public có API key,
# - usage plan để chống lạm dụng và kiểm soát chi phí.
# Nói ngắn gọn: file này biến mã Python trong backend/ingest thành một dịch vụ AWS hoàn chỉnh.
terraform {
  # Bắt đầu khối cấu hình gốc của Terraform cho module này.
  required_version = ">= 1.5"
  # Yêu cầu Terraform CLI phải có version từ 1.5 trở lên mới chạy được file này.
  
  required_providers {
    # Khai báo danh sách provider mà module này phụ thuộc.
    aws = {
      # Định nghĩa provider AWS là provider chính của toàn bộ module.
      source  = "hashicorp/aws"
      # Chỉ rõ provider aws được lấy từ namespace chính thức của HashiCorp.
      version = "~> 5.0"
      # Khóa provider quanh major version 5 để tránh thay đổi breaking bất ngờ.
    }
  }
  
  # Using local backend - state will be stored in terraform.tfstate in this directory
  # Điều này phù hợp với cách học của khóa, mỗi part có state độc lập.
  # This is automatically gitignored for security
  # Nhờ gitignore, file state local sẽ không bị đẩy nhầm lên repo.
}

# Provider này quyết định tất cả resource trong file sẽ được tạo ở region nào.
# Nếu region này lệch với SageMaker endpoint hoặc cấu hình local của bạn,
# các ARN và lời gọi cross-service có thể lỗi.
provider "aws" {
  # Bắt đầu cấu hình provider AWS cụ thể cho module này.
  region = var.aws_region
  # Lấy region từ biến đầu vào để cùng một module dùng được trên nhiều vùng AWS.
}

# Data source này không tạo resource mới.
# Nó chỉ đọc account ID hiện tại để dùng cho:
# - đặt tên bucket duy nhất,
# - dựng ARN IAM chính xác theo tài khoản đang deploy.
# Data source for current caller identity
data "aws_caller_identity" "current" {}
# Gọi AWS STS ngầm để lấy thông tin account hiện hành, đặc biệt là account_id.

# ========================================
# S3 Vectors Bucket
# ========================================

# Bucket này là nơi implementation Terraform hiện tại tạo bucket dữ liệu tên alex-vectors-<account_id>.
# Repo hiện tại dùng aws_s3_bucket cho phần lưu trữ này,
# dù guide có mô tả thêm góc nhìn S3 Vectors ở mức sản phẩm/khái niệm.
resource "aws_s3_bucket" "vectors" {
  # Tạo bucket S3 với logical name là vectors trong module Terraform.
  bucket = "alex-vectors-${data.aws_caller_identity.current.account_id}"
  # Ghép account_id vào tên bucket để bảo đảm tính duy nhất toàn cục của bucket name.
  
  tags = {
    # Gán tag cho resource để dễ lọc trong AWS Console và cost explorer.
    Project = "alex"
    # Tag Project cho biết bucket này thuộc project Alex.
    Part    = "3"
    # Tag Part cho biết bucket này được tạo trong guide/phần số 3.
  }
}

# Bật versioning để object thay đổi vẫn có lịch sử phiên bản.
# Đây là một lớp an toàn bổ sung nếu sau này bucket có thêm object cần truy vết/phục hồi.
resource "aws_s3_bucket_versioning" "vectors" {
  # Tạo resource cấu hình versioning cho chính bucket vừa tạo.
  bucket = aws_s3_bucket.vectors.id
  # Liên kết cấu hình versioning với bucket vectors.
  
  versioning_configuration {
    # Mở khối cấu hình versioning chi tiết.
    status = "Enabled"
    # Bật versioning ở trạng thái hoạt động hoàn toàn.
  }
}

# Mã hóa server-side bằng AES256 để dữ liệu lưu trong bucket luôn được mã hóa at rest.
resource "aws_s3_bucket_server_side_encryption_configuration" "vectors" {
  # Tạo resource cấu hình mã hóa mặc định cho bucket.
  bucket = aws_s3_bucket.vectors.id
  # Áp cấu hình mã hóa này lên bucket vectors.
  
  rule {
    # Mỗi bucket có thể có một hoặc nhiều rule mã hóa mặc định.
    apply_server_side_encryption_by_default {
      # Khai báo cách mã hóa mặc định khi object được ghi vào bucket.
      sse_algorithm = "AES256"
      # Dùng SSE-S3 với thuật toán AES256 do AWS quản lý.
    }
  }
}

# Khối này chặn toàn bộ khả năng public access ở cấp bucket.
# Đây là mặc định an toàn để dữ liệu ingest không bị lộ ra internet công khai.
resource "aws_s3_bucket_public_access_block" "vectors" {
  # Tạo cấu hình block public access cho bucket.
  bucket = aws_s3_bucket.vectors.id
  # Áp cấu hình này lên bucket vectors.
  
  block_public_acls       = true
  # Chặn việc gắn ACL public mới lên bucket hoặc object.
  block_public_policy     = true
  # Chặn việc áp bucket policy mang tính public.
  ignore_public_acls      = true
  # Bỏ qua mọi ACL public nếu ai đó cố tình hoặc vô ý gắn vào.
  restrict_public_buckets = true
  # Hạn chế bucket khỏi các public policy hiện hữu có thể làm nó lộ ra ngoài.
}

# ========================================
# Lambda Function for Ingestion
# ========================================

# Role này cho phép dịch vụ Lambda assume để chạy function alex-ingest.
# Không có role này thì Lambda không có danh tính AWS để gọi service khác.
# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  # Tạo IAM role dành riêng cho Lambda ingest.
  name = "alex-ingest-lambda-role"
  # Đặt tên role rõ ràng để dễ nhận diện trong IAM Console.
  
  assume_role_policy = jsonencode({
    # Dùng jsonencode để viết trust policy ngay trong Terraform HCL.
    Version = "2012-10-17"
    # Version chuẩn của policy document AWS IAM.
    Statement = [
      # Danh sách các statement cho trust relationship.
      {
        Action = "sts:AssumeRole"
        # Cho phép hành động assume role.
        Effect = "Allow"
        # Statement này mang tính cho phép.
        Principal = {
          # Chỉ rõ service principal nào được dùng role này.
          Service = "lambda.amazonaws.com"
          # Chỉ dịch vụ Lambda mới được assume role.
        }
      }
    ]
  })
  
  tags = {
    # Gắn tag phục vụ quản trị và cost tracking.
    Project = "alex"
    # Đánh dấu thuộc project Alex.
    Part    = "3"
    # Đánh dấu thuộc Part 3.
  }
}

# Policy này là trái tim của phân quyền Part 3.
# Nó gom các quyền tối thiểu mà Lambda ingest cần:
# - ghi log CloudWatch,
# - thao tác bucket dữ liệu,
# - invoke SageMaker endpoint,
# - put/query/get/delete vector trên namespace s3vectors.
# Lambda policy for S3 Vectors and SageMaker
resource "aws_iam_role_policy" "lambda_policy" {
  # Tạo inline policy gắn trực tiếp vào role Lambda.
  name = "alex-ingest-lambda-policy"
  # Đặt tên policy theo chức năng để dễ hiểu.
  role = aws_iam_role.lambda_role.id
  # Gắn policy này vào role vừa tạo ở trên.
  
  policy = jsonencode({
    # Chuyển object HCL bên dưới thành JSON policy document hợp lệ cho IAM.
    Version = "2012-10-17"
    # Version chuẩn của IAM policy.
    Statement = [
      # Statement 1: quyền ghi log CloudWatch.
      {
        Effect = "Allow"
        # Cho phép các hành động logging.
        Action = [
          "logs:CreateLogGroup",
          # Cho phép Lambda tạo log group nếu chưa có.
          "logs:CreateLogStream",
          # Cho phép Lambda tạo log stream cho mỗi execution context.
          "logs:PutLogEvents"
          # Cho phép Lambda ghi log event vào CloudWatch Logs.
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
        # Giới hạn quyền logs trong đúng region và account hiện hành.
      },
      {
        # Statement 2: quyền thao tác bucket/object S3 liên quan.
        Effect = "Allow"
        # Cho phép các hành động liệt kê và thao tác object.
        Action = [
          "s3:GetObject",
          # Cho phép đọc object trong bucket.
          "s3:PutObject",
          # Cho phép ghi object vào bucket.
          "s3:DeleteObject",
          # Cho phép xóa object nếu cần.
          "s3:ListBucket"
          # Cho phép liệt kê nội dung bucket.
        ]
        Resource = [
          aws_s3_bucket.vectors.arn,
          # ARN cấp bucket cho hành động ListBucket.
          "${aws_s3_bucket.vectors.arn}/*"
          # ARN cấp object cho các hành động Get/Put/DeleteObject.
        ]
      },
      {
        # Statement 3: quyền invoke endpoint embedding ở SageMaker.
        Effect = "Allow"
        # Cho phép gọi endpoint embedding.
        Action = [
          "sagemaker:InvokeEndpoint"
          # Đây là quyền tối thiểu để Lambda gọi model inference.
        ]
        Resource = "arn:aws:sagemaker:${var.aws_region}:${data.aws_caller_identity.current.account_id}:endpoint/${var.sagemaker_endpoint_name}"
        # Giới hạn quyền đúng vào endpoint được truyền từ Part 2.
      },
      {
        # Statement 4: quyền thao tác vector trong namespace s3vectors.
        Effect = "Allow"
        # Cho phép các thao tác vector cơ bản phục vụ ingest và test/search.
        Action = [
          "s3vectors:PutVectors",
          # Cho phép ghi vector mới vào index.
          "s3vectors:QueryVectors",
          # Cho phép truy vấn vector gần nhất.
          "s3vectors:GetVectors",
          # Cho phép đọc vector theo key nếu cần.
          "s3vectors:DeleteVectors"
          # Cho phép xóa vector khỏi index.
        ]
        Resource = "arn:aws:s3vectors:${var.aws_region}:${data.aws_caller_identity.current.account_id}:bucket/${aws_s3_bucket.vectors.id}/index/*"
        # Giới hạn quyền vào mọi index nằm trong bucket vectors của account hiện tại.
      }
    ]
  })
}

# Resource này khai báo chính function alex-ingest.
# Nó tham chiếu trực tiếp tới file zip được package ở backend/ingest,
# cấu hình runtime Python 3.12, memory, timeout, handler,
# và inject environment variables để code Python biết phải gọi bucket/endpoint nào.
# Lambda function
resource "aws_lambda_function" "ingest" {
  # Tạo function Lambda thực thi logic ingest.
  function_name = "alex-ingest"
  # Đặt tên function rõ ràng để đúng với guide và dễ tìm trong Lambda Console.
  role          = aws_iam_role.lambda_role.arn
  # Gắn IAM role vừa tạo để function có đủ quyền gọi các dịch vụ AWS.
  
  # Note: The deployment package will be created by the guide instructions
  # File zip này không do Terraform build mà do script package.py tạo ra trước đó.
  filename         = "${path.module}/../../backend/ingest/lambda_function.zip"
  # Trỏ đến deployment package đã được build trong backend/ingest.
  source_code_hash = fileexists("${path.module}/../../backend/ingest/lambda_function.zip") ? filebase64sha256("${path.module}/../../backend/ingest/lambda_function.zip") : null
  # Nếu zip tồn tại thì tính hash để Terraform biết lúc nào code thay đổi và cần redeploy.
  
  handler = "ingest_s3vectors.lambda_handler"
  # Chỉ rõ file Python và hàm entry point mà Lambda sẽ gọi khi có request.
  runtime = "python3.12"
  # Dùng runtime Python 3.12 để khớp với môi trường local và code trong guide.
  timeout = 60
  # Cho phép function chạy tối đa 60 giây trước khi bị AWS cắt.
  memory_size = 512
  # Cấp 512 MB RAM cho Lambda, đủ cho tác vụ gọi SageMaker và ghi vector nhẹ.
  
  environment {
    # Bắt đầu khối biến môi trường sẽ được inject vào runtime của Lambda.
    variables = {
      # Khai báo map các biến môi trường key-value.
      VECTOR_BUCKET      = aws_s3_bucket.vectors.id
      # Truyền tên bucket vào code Python để handler biết nơi lưu vector.
      SAGEMAKER_ENDPOINT = var.sagemaker_endpoint_name
      # Truyền tên endpoint embedding vào code Python để handler biết nơi gọi inference.
    }
  }
  
  tags = {
    # Gắn tag để dễ quản trị và tracking chi phí.
    Project = "alex"
    # Tag project.
    Part    = "3"
    # Tag part.
  }
}

# Log group giữ log thực thi của Lambda trong 7 ngày.
# Việc khai báo rõ log group trong Terraform giúp chủ động retention thay vì để AWS tạo mặc định.
# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  # Tạo log group tương ứng với function alex-ingest.
  name              = "/aws/lambda/alex-ingest"
  # Dùng đúng naming convention mặc định của Lambda trên CloudWatch Logs.
  retention_in_days = 7
  # Giữ log 7 ngày rồi tự động xoá để hạn chế chi phí lưu trữ log.
  
  tags = {
    # Gắn tag giống các resource khác để đồng nhất quản trị.
    Project = "alex"
    # Tag project.
    Part    = "3"
    # Tag part.
  }
}

# ========================================
# API Gateway
# ========================================

# REST API này là cổng public để client bên ngoài gọi vào ingestion service.
# Nó không chứa logic nghiệp vụ; logic thật nằm trong Lambda phía sau.
# REST API
resource "aws_api_gateway_rest_api" "api" {
  # Tạo REST API Gateway kiểu cũ/phổ biến để expose endpoint ingest.
  name        = "alex-api"
  # Đặt tên API để dễ tìm trong console.
  description = "Alex Financial Planner API"
  # Mô tả ngắn gọn mục đích của API.
  
  endpoint_configuration {
    # Cấu hình loại endpoint của API Gateway.
    types = ["REGIONAL"]
    # Chọn REGIONAL để API chạy theo region hiện hành thay vì edge-optimized.
  }
  
  tags = {
    # Gắn tag phục vụ quản trị và billing.
    Project = "alex"
    # Tag project.
    Part    = "3"
    # Tag part.
  }
}

# Resource này tạo path /ingest bên dưới root của REST API.
# API Resource
resource "aws_api_gateway_resource" "ingest" {
  # Tạo resource con dưới REST API.
  rest_api_id = aws_api_gateway_rest_api.api.id
  # Gắn resource này vào API vừa tạo.
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  # Chọn parent là root của API, tức path sẽ nằm ngay sau domain/stage.
  path_part   = "ingest"
  # Tạo segment đường dẫn là /ingest.
}

# Method này định nghĩa rằng path /ingest chấp nhận HTTP POST
# và bắt buộc client phải gửi API key hợp lệ.
# API Method
resource "aws_api_gateway_method" "ingest_post" {
  # Tạo method cho resource /ingest.
  rest_api_id   = aws_api_gateway_rest_api.api.id
  # Chỉ rõ method thuộc API nào.
  resource_id   = aws_api_gateway_resource.ingest.id
  # Chỉ rõ method thuộc path resource nào.
  http_method   = "POST"
  # Chỉ cho phép HTTP POST vì ingest là thao tác ghi dữ liệu.
  authorization = "NONE"
  # Không dùng IAM/Cognito/JWT ở tầng này; xác thực chính bằng API key.
  api_key_required = true
  # Buộc client phải gửi x-api-key hợp lệ thì mới được gọi endpoint.
}

# Integration nối method POST /ingest với Lambda theo kiểu AWS_PROXY.
# AWS_PROXY nghĩa là API Gateway chuyển event gần như nguyên bản cho Lambda handler tự xử lý.
# Lambda Integration
resource "aws_api_gateway_integration" "lambda" {
  # Tạo integration giữa API Gateway và backend compute.
  rest_api_id = aws_api_gateway_rest_api.api.id
  # Chỉ rõ integration nằm trong API nào.
  resource_id = aws_api_gateway_resource.ingest.id
  # Chỉ rõ integration gắn với path /ingest.
  http_method = aws_api_gateway_method.ingest_post.http_method
  # Chỉ rõ integration này phục vụ method POST.
  
  integration_http_method = "POST"
  # Khi gọi Lambda qua API Gateway, integration method thường là POST.
  type                   = "AWS_PROXY"
  # Chọn proxy integration để Lambda tự nhận toàn bộ event.
  uri                    = aws_lambda_function.ingest.invoke_arn
  # Trỏ integration tới invoke ARN của Lambda alex-ingest.
}

# Dù API Gateway đã cấu hình integration, Lambda vẫn cần permission riêng
# để chấp nhận bị invoke bởi principal apigateway.amazonaws.com.
# Nếu thiếu resource này, API có thể trả 500/403 khi gọi thật.
# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  # Tạo permission resource để API Gateway được phép invoke Lambda.
  statement_id  = "AllowAPIGatewayInvoke"
  # Đặt tên statement trong policy của Lambda.
  action        = "lambda:InvokeFunction"
  # Cấp đúng quyền invoke function.
  function_name = aws_lambda_function.ingest.function_name
  # Áp permission này cho function alex-ingest.
  principal     = "apigateway.amazonaws.com"
  # Chỉ service API Gateway mới được hưởng quyền này.
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
  # Giới hạn lời gọi đến từ execution ARN của API này trên mọi method/path.
}

# Deployment đóng băng cấu hình API tại một thời điểm để stage có thể dùng.
# Trigger redeployment dùng sha1 của các thành phần quan trọng
# để Terraform tự biết lúc nào phải rollout lại API khi cấu hình thay đổi.
# API Deployment
resource "aws_api_gateway_deployment" "api" {
  # Tạo một deployment snapshot cho REST API.
  rest_api_id = aws_api_gateway_rest_api.api.id
  # Chỉ rõ API nào đang được deploy.
  
  triggers = {
    # Dùng triggers để ép Terraform tạo deployment mới khi cấu hình API đổi.
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.ingest.id,
      # Theo dõi thay đổi ở resource path /ingest.
      aws_api_gateway_method.ingest_post.id,
      # Theo dõi thay đổi ở method POST /ingest.
      aws_api_gateway_integration.lambda.id,
      # Theo dõi thay đổi ở integration sang Lambda.
    ]))
    # Băm tập giá trị quan trọng để Terraform nhận diện sự thay đổi cấu hình API.
  }
  
  lifecycle {
    # Điều khiển cách Terraform tạo/hủy deployment khi có thay đổi.
    create_before_destroy = true
    # Tạo deployment mới trước rồi mới hủy deployment cũ để giảm downtime.
  }
}

# Stage prod là URL môi trường thật mà guide dùng trong .env.
# API Stage
resource "aws_api_gateway_stage" "api" {
  # Tạo stage prod để public API deployment ra URL gọi được.
  deployment_id = aws_api_gateway_deployment.api.id
  # Gắn stage vào deployment snapshot mới nhất.
  rest_api_id   = aws_api_gateway_rest_api.api.id
  # Gắn stage vào API tương ứng.
  stage_name    = "prod"
  # Đặt tên stage là prod theo đúng URL trong guide.
  
  tags = {
    # Gắn tag quản trị như các resource khác.
    Project = "alex"
    # Tag project.
    Part    = "3"
    # Tag part.
  }
}

# API key là lớp xác thực đơn giản nhưng rất thực dụng cho ingestion endpoint public.
# Nó giúp tránh việc ai biết URL cũng có thể spam request làm tăng chi phí Lambda/SageMaker.
# API Key
resource "aws_api_gateway_api_key" "api_key" {
  # Tạo API key trong API Gateway.
  name = "alex-api-key"
  # Đặt tên key để dễ nhận diện trong console và output.
  
  tags = {
    # Gắn tag cho API key.
    Project = "alex"
    # Tag project.
    Part    = "3"
    # Tag part.
  }
}

# Usage plan gắn quota và throttle lên API key.
# Đây là lớp bảo vệ quan trọng để giới hạn tốc độ gọi và tổng lượng request theo tháng.
# Usage Plan
resource "aws_api_gateway_usage_plan" "plan" {
  # Tạo usage plan dùng để điều tiết lưu lượng cho API key.
  name = "alex-usage-plan"
  # Đặt tên usage plan.
  
  api_stages {
    # Liên kết usage plan với một API và stage cụ thể.
    api_id = aws_api_gateway_rest_api.api.id
    # Chỉ rõ API áp chính sách usage plan này.
    stage  = aws_api_gateway_stage.api.stage_name
    # Chỉ rõ stage prod là nơi plan này có hiệu lực.
  }
  
  quota_settings {
    # Thiết lập quota tổng theo chu kỳ.
    limit  = 10000
    # Giới hạn tối đa 10,000 request trong mỗi chu kỳ.
    period = "MONTH"
    # Chu kỳ quota là theo tháng.
  }
  
  throttle_settings {
    # Thiết lập giới hạn tốc độ tức thời để chống spam/chi phí bùng nổ.
    rate_limit  = 100
    # Tốc độ xử lý ổn định là 100 request/giây.
    burst_limit = 200
    # Cho phép burst tạm thời lên đến 200 request.
  }
}

# Resource này liên kết API key vừa tạo với usage plan ở trên.
# Nếu không có bước gắn này, API key tồn tại nhưng không được áp chính sách sử dụng.
# Usage Plan Key
resource "aws_api_gateway_usage_plan_key" "plan_key" {
  # Tạo liên kết giữa usage plan và API key.
  key_id        = aws_api_gateway_api_key.api_key.id
  # Chỉ rõ key nào sẽ được gắn vào usage plan.
  key_type      = "API_KEY"
  # Xác nhận đây là loại API key thông thường của API Gateway.
  usage_plan_id = aws_api_gateway_usage_plan.plan.id
  # Chỉ rõ usage plan nào sẽ quản lý key này.
}
