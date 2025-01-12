# defines outputs that will be displayed after terraform apply

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

output "api_gateway_upload_url" {
  description = "Invoke URL for uploading files"
  value       = module.api_gateway.upload_url
}

output "api_gateway_fetch_metadata_url" {
  description = "Invoke URL for fetching file metadata"
  value       = module.api_gateway.fetch_metadata_url
}

output "api_gateway_delete_url" {
  description = "Invoke URL for deleting files"
  value       = module.api_gateway.delete_url
}
