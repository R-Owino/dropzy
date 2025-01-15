variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "upload_lambda_arn" {
  description = "Invoke ARN of the upload lambda function"
  type        = string
}

variable "upload_lambda_function_name" {
  description = "Name of the upload lambda function"
  type        = string
}
