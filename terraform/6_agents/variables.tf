variable "aws_region" {
  description = "AWS region for resources"
  type        = string
}

variable "aurora_cluster_arn" {
  description = "ARN of the Aurora cluster from Part 5"
  type        = string
}

variable "aurora_secret_arn" {
  description = "ARN of the Secrets Manager secret from Part 5"
  type        = string
}

variable "vector_bucket" {
  description = "S3 Vectors bucket name from Part 3"
  type        = string
}

# Per-agent OpenAI model configuration
# Each agent can use a different model optimized for its task

variable "model_id_tagger" {
  description = "OpenAI model for Tagger agent (instrument classification)"
  type        = string
  default     = "openai/gpt-5.4-nano"
}

variable "model_id_retirement" {
  description = "OpenAI model for Retirement agent (retirement projections)"
  type        = string
  default     = "openai/gpt-5.4-nano"
}

variable "model_id_charter" {
  description = "OpenAI model for Charter agent (chart JSON generation)"
  type        = string
  default     = "openai/gpt-5.4-nano"
}

variable "model_id_reporter" {
  description = "OpenAI model for Reporter agent (portfolio analysis report)"
  type        = string
  default     = "openai/gpt-5.4-nano"
}

variable "model_id_planner" {
  description = "OpenAI model for Planner agent (orchestration)"
  type        = string
  default     = "openai/gpt-5.4-mini"
}

variable "sagemaker_endpoint" {
  description = "SageMaker endpoint name from Part 2"
  type        = string
  default     = "alex-embedding-endpoint"
}

variable "polygon_api_key" {
  description = "Polygon.io API key for market data"
  type        = string
}

variable "polygon_plan" {
  description = "Polygon.io plan type (free or paid)"
  type        = string
  default     = "free"
}

# LangFuse observability variables (optional)
variable "langfuse_public_key" {
  description = "LangFuse public key for observability (optional)"
  type        = string
  default     = ""
  sensitive   = false
}

variable "langfuse_secret_key" {
  description = "LangFuse secret key for observability (optional)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "langfuse_host" {
  description = "LangFuse host URL (optional)"
  type        = string
  default     = "https://us.cloud.langfuse.com"
}

# OpenAI API key (REQUIRED — all agents use OpenAI models via LiteLLM)
variable "openai_api_key" {
  description = "OpenAI API key for model access (required for all agents)"
  type        = string
  sensitive   = true
}