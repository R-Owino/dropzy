# defines outputs that will be displayed after terraform apply

output "aws_region" {
  description = "Region where the resources have been provisioned"
  value       = var.aws_region
}

output "cognito_user_pool_id" {
  description = "ID of the Cognito user pool"
  value       = module.cognito.userpool_id
}

output "cognito_user_pool_client_id" {
  description = "ID of the Cognito user pool client"
  value       = module.cognito.userpool_client_id
}

output "api_gateway_invoke_url" {
  description = "Invoke URL of the API Gateway"
  value       = module.api_gateway.api_gateway_invoke_url
}

output "api_gateway_fetch_metadata_url" {
  description = "Invoke URL for fetching file metadata"
  value       = module.api_gateway.fetch_metadata_url
}

output "api_gateway_delete_url" {
  description = "Invoke URL for deleting files"
  value       = module.api_gateway.delete_url
}

output "s3_bucket_name" {
  description = "Name of the bucket where files are stored"
  value       = module.s3.bucket_name
}

output "documents_dynamodb_table_name" {
  description = "Name of DynamoDB table holding the files metadata"
  value       = module.dynamodb.documents_metadata_table_name
}
output "userdata_dynamodb_table_name" {
  description = "Name of DynamoDB table holding user data"
  value       = module.dynamodb.userdata_table_name
}
