variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "upload_metadata_function_arn" {
  description = "ARN of the file metadata uploading lambda function"
  type        = string
}

variable "upload_metadata_function_name" {
  description = "Name of the file metadata uploading lambda function"
  type        = string
}
