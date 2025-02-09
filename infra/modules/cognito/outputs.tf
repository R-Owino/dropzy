output "userpool_id" {
  description = "ID of the Cognito user pool"
  value       = aws_cognito_user_pool.userpool.id
}

output "userpool_arn" {
  description = "ARN of the Cognito user pool"
  value       = aws_cognito_user_pool.userpool.arn
}

output "userpool_client_id" {
  description = "ID of the Cognito user pool client"
  value       = aws_cognito_user_pool_client.userpool_client.id
}
