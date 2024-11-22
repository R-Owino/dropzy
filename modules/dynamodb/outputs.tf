output "table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.userdata.name
}

output "table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.userdata.arn
}

output "doc_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.documents_metadata.name
}

output "doc_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.documents_metadata.arn
}
