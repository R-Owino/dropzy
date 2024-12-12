# define and configure terraform variables

variable "aws_region" {
  description = "The AWS region in which resources will be created."
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "The project name, which will be used as a prefix for all resources."
  type        = string
  default     = "fileshare"
}

variable "userdata_table_name" {
  description = "Name of the DynamoDB table holding user information"
  type        = string
  default     = "userdata"
}

variable "documents_metadata_table_name" {
  description = "Name of the DynamoDB table holding file metadata"
  type        = string
  default     = "documents-metadata"
}
