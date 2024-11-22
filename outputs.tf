# defines outputs that will be displayed after terraform apply

output "cognito_user_pool_id" {
  description = "ID of the Cognito user pool"
  value       = module.cognito.userpool_id
}

output "cognito_user_pool_arn" {
  description = "ARN of the Cognito user pool"
  value       = module.cognito.userpool_arn
}

output "cognito_user_pool_client_id" {
  description = "ID of the Cognito user pool client"
  value       = module.cognito.userpool_client_id
}

output "cognito_userpool_domain" {
  description = "The Amazon Cognito domain for the user pool"
  value       = module.cognito.cognito_domain
}


output "dynamodb_userdata_table_name" {
  description = "Name of the DynamoDB table"
  value       = module.dynamodb.table_name
}

output "dynamodb_userdata_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = module.dynamodb.table_arn
}

output "lambda_userdata_arn" {
  description = "ARN of the user data Lambda function"
  value       = module.lambda.userdata_function_arn
}
