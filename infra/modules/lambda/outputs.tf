/* lambda module outputs */

output "userdata_function_arn" {
  description = "ARN of the userdata lambda function"
  value       = aws_lambda_function.userdata.arn
}

output "userdata_function_name" {
  description = "Name of the userdata lambda function"
  value       = aws_lambda_function.userdata.function_name
}

output "upload_metadata_function_name" {
  description = "Name of the file metadata uploading lambda function"
  value       = aws_lambda_function.upload_file_metadata.function_name
}

output "upload_metadata_function_arn" {
  description = "ARN of the file metadata uploading lambda function"
  value       = aws_lambda_function.upload_file_metadata.arn
}

output "file_metadata_function_name" {
  description = "Name of the file metadata fetching function"
  value       = aws_lambda_function.fetch_file_metadata.function_name
}

output "file_metadata_function_arn" {
  description = "ARN of the file metadata lambda function"
  value       = aws_lambda_function.fetch_file_metadata.arn
}

output "file_metadata_invoke_arn" {
  description = "Invoke ARN of the file metadata lambda function"
  value       = aws_lambda_function.fetch_file_metadata.invoke_arn
}

output "delete_lambda_function_name" {
  description = "Name of the delete lambda function"
  value       = aws_lambda_function.delete_file.function_name
}

output "delete_function_arn" {
  description = "ARN of the delete file lambda function"
  value       = aws_lambda_function.delete_file.arn
}

output "delete_lambda_invoke_arn" {
  description = "Invoke ARN of the delete lambda function"
  value       = aws_lambda_function.delete_file.invoke_arn
}

output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}
