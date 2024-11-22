variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "lambda_function_arn" {
  description = "ARN of the Lambda function for user data handling"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for user data"
  type        = string
}
