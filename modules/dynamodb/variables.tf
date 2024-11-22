variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "userdata_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "documents_metadata_table_name" {
  description = "Name of the DynamoDB table"
  type        = string

}
