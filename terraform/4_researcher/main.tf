# File Terraform này là trung tâm của Part 4 trong implementation hiện tại của repo.
# Nó tạo ECR, Lambda researcher dùng container image, Function URL public, và scheduler tùy chọn.
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.28.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data source này đọc account hiện tại để dựng ARN/policy chính xác.
data "aws_caller_identity" "current" {}

# locals này quyết định Terraform có thật sự tạo researcher Lambda hay không.
# Nếu chưa có image URI thì chỉ tạo phần ECR/role cần thiết cho bước deploy đầu.
locals {
  researcher_deployed = var.researcher_image_uri != ""
  scheduler_active    = var.scheduler_enabled && local.researcher_deployed
}

# Repository này lưu Docker image của researcher trước khi Lambda pull về.
resource "aws_ecr_repository" "researcher" {
  name                 = "alex-researcher"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }

  tags = {
    Project = "alex"
    Part    = "4"
  }
}

# Policy này cho phép Lambda lấy image layers từ ECR.
resource "aws_ecr_repository_policy" "researcher_lambda_access" {
  repository = aws_ecr_repository.researcher.name

  policy = jsonencode({
    Version = "2008-10-17"
    Statement = [
      {
        Sid    = "LambdaEcrImageRetrievalPolicy"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]
        Condition = {
          ArnLike = {
            "aws:sourceArn" = "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:*"
          }
        }
      }
    ]
  })
}

# Role này là danh tính AWS của researcher Lambda khi function chạy.
resource "aws_iam_role" "researcher_lambda_role" {
  name = "alex-researcher-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = "alex"
    Part    = "4"
  }
}

# Policy managed này cấp quyền ghi log CloudWatch cơ bản cho Lambda.
resource "aws_iam_role_policy_attachment" "researcher_lambda_basic" {
  role       = aws_iam_role.researcher_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline policy này giữ quyền Bedrock cho researcher runtime cũ hoặc khi cần debug AWS model access.
resource "aws_iam_role_policy" "researcher_lambda_bedrock_access" {
  name = "alex-researcher-lambda-bedrock-policy"
  role = aws_iam_role.researcher_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ListFoundationModels"
        ]
        Resource = "*"
      }
    ]
  })
}

# Đây là Lambda researcher thật sự.
# Nó chỉ được tạo khi Terraform đã biết image URI cần deploy.
resource "aws_lambda_function" "researcher" {
  count         = local.researcher_deployed ? 1 : 0
  function_name = "alex-researcher"
  package_type  = "Image"
  image_uri     = var.researcher_image_uri
  role          = aws_iam_role.researcher_lambda_role.arn
  timeout       = 300
  memory_size   = 2048
  architectures = ["x86_64"]

  ephemeral_storage {
    size = 2048
  }

  # Các biến môi trường này truyền cấu hình model, ingest API, và logging vào runtime.
  environment {
    variables = {
      OPENAI_API_KEY    = var.openai_api_key
      OPENROUTER_API_KEY = var.openrouter_api_key
      ALEX_API_ENDPOINT = var.alex_api_endpoint
      ALEX_API_KEY      = var.alex_api_key
      BEDROCK_REGION    = var.bedrock_region
      RESEARCHER_MODEL  = var.researcher_model
      MCP_LOGGING       = var.mcp_logging
    }
  }

  tags = {
    Project = "alex"
    Part    = "4"
  }
}

# Function URL public là endpoint HTTPS bên ngoài dùng để gọi /health và /research.
resource "aws_lambda_function_url" "researcher" {
  count              = local.researcher_deployed ? 1 : 0
  function_name      = aws_lambda_function.researcher[0].function_name
  authorization_type = "NONE"
}

# Permission này cho phép public invoke qua Function URL.
resource "aws_lambda_permission" "allow_public_function_url_invoke" {
  count                    = local.researcher_deployed ? 1 : 0
  statement_id             = "AllowPublicFunctionInvokeViaUrl"
  action                   = "lambda:InvokeFunction"
  function_name            = aws_lambda_function.researcher[0].function_name
  principal                = "*"
  invoked_via_function_url = true
}

# Role này chỉ tồn tại khi scheduler được bật.
# Nó cho phép EventBridge Scheduler invoke scheduler Lambda.
resource "aws_iam_role" "eventbridge_role" {
  count = local.scheduler_active ? 1 : 0
  name  = "alex-eventbridge-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = "alex"
    Part    = "4"
  }
}

# Lambda scheduler là lớp trung gian gọi researcher theo lịch.
# Nó cần thiết vì Function URL research có thể chạy lâu hơn timeout của một số integration trực tiếp.
resource "aws_lambda_function" "scheduler_lambda" {
  count         = local.scheduler_active ? 1 : 0
  function_name = "alex-researcher-scheduler"
  role          = aws_iam_role.lambda_scheduler_role[0].arn
  filename      = "${path.module}/../../backend/scheduler/lambda_function.zip"
  source_code_hash = fileexists("${path.module}/../../backend/scheduler/lambda_function.zip") ? filebase64sha256("${path.module}/../../backend/scheduler/lambda_function.zip") : null
  handler       = "lambda_function.handler"
  runtime       = "python3.12"
  timeout       = 180
  memory_size   = 256

  environment {
    variables = {
      APP_RUNNER_URL = trimsuffix(aws_lambda_function_url.researcher[0].function_url, "/")
    }
  }

  tags = {
    Project = "alex"
    Part    = "4"
  }
}

# Role này là danh tính AWS của scheduler Lambda.
resource "aws_iam_role" "lambda_scheduler_role" {
  count = local.scheduler_active ? 1 : 0
  name  = "alex-scheduler-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = "alex"
    Part    = "4"
  }
}

# Gắn policy log cơ bản cho scheduler Lambda.
resource "aws_iam_role_policy_attachment" "lambda_scheduler_basic" {
  count      = local.scheduler_active ? 1 : 0
  role       = aws_iam_role.lambda_scheduler_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Schedule này chạy mỗi 2 giờ khi scheduler_enabled=true.
resource "aws_scheduler_schedule" "research_schedule" {
  count = local.scheduler_active ? 1 : 0
  name  = "alex-research-schedule"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(12 hours)"

  target {
    arn      = aws_lambda_function.scheduler_lambda[0].arn
    role_arn = aws_iam_role.eventbridge_role[0].arn
  }
}

# Permission này cho phép EventBridge Scheduler invoke scheduler Lambda.
resource "aws_lambda_permission" "allow_eventbridge" {
  count         = local.scheduler_active ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scheduler_lambda[0].function_name
  principal     = "scheduler.amazonaws.com"
  source_arn    = aws_scheduler_schedule.research_schedule[0].arn
}

# Policy này trao cho role của EventBridge quyền gọi scheduler Lambda.
resource "aws_iam_role_policy" "eventbridge_invoke_lambda" {
  count = local.scheduler_active ? 1 : 0
  name  = "InvokeLambdaPolicy"
  role  = aws_iam_role.eventbridge_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = aws_lambda_function.scheduler_lambda[0].arn
      }
    ]
  })
}
