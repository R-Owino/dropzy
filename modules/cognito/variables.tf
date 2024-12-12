variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "userdata_function_arn" {
  description = "ARN of the userdata lambda function"
  type        = string
}

variable "userdata_function_name" {
  description = "Name of the userdata lambda function"
  type        = string
}
variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for user data"
  type        = string
}
