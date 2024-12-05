/* API Gateway module variables */

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "userpool_arn" {
  description = "ARN of the Cognito user pool"
  type        = string
}

variable "upload_lambda_invoke_arn" {
  description = "Invoke ARN of the upload Lambda function"
  type        = string
}

variable "download_lambda_invoke_arn" {
  description = "Invoke ARN of the download Lambda function"
  type        = string
}

variable "file_metadata_invoke_arn" {
  description = "Invoke ARN of the fetch file metadata lambda function"
  type = string
}

variable "upload_lambda_function_name" {
  description = "Name of the upload Lambda function"
  type        = string
}

variable "download_lambda_function_name" {
  description = "Name of the download Lambda function"
  type        = string
}

variable "file_metadata_lambda_function_name" {
  description = "Name of the fetch file metadata lambda function"
  type = string
}
