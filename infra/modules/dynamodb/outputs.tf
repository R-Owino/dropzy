output "userdata_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.userdata.name
}

output "userdata_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.userdata.arn
}

output "documents_metadata_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.documents_metadata.name
}

output "documents_metadata_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.documents_metadata.arn
}
