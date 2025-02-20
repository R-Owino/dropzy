
output "tfstate_bucket" {
  description = "Storage for remote backend"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "tfstate_dynamodb_table" {
  description = "State locking"
  value       = aws_dynamodb_table.terraform_lock.name
}
