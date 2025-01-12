/* API Gateway module variables */

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "aws_region" {
  description = "AWS region in which the API will be created"
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

variable "upload_lambda_arn" {
  description = "Invoke ARN of the upload lambda function"
  type        = string
}

variable "file_metadata_arn" {
  description = "Invoke ARN of the fetch file metadata lambda function"
  type        = string
}

variable "delete_lambda_arn" {
  description = "Invoke ARN of the delete lambda function"
  type        = string
}

variable "upload_lambda_function_name" {
  description = "Name of the upload lambda function"
  type        = string
}

variable "file_metadata_lambda_function_name" {
  description = "Name of the fetch file metadata lambda function"
  type        = string
}

variable "delete_lambda_function_name" {
  description = "Name of the delete lambda function"
  type        = string
}
