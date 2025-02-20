variable "project_name" {
  description = "The project name, which will be used as a prefix for all resources."
  type        = string
  default     = "fileshare"
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
  default     = "dev"
}
