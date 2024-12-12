/* lambda functions outputs */

output "userdata_function_arn" {
  description = "ARN of the userdata lambda function"
  value       = aws_lambda_function.userdata.arn
}

output "userdata_function_name" {
  description = "Name of the userdata lambda function"
  value       = aws_lambda_function.userdata.function_name
}

output "upload_function_name" {
  description = "Name of the upload Lambda function"
  value       = aws_lambda_function.upload.function_name
}

output "upload_function_arn" {
  description = "ARN of the upload lambda function"
  value       = aws_lambda_function.upload.arn
}

output "download_function_name" {
  description = "Name of the download lambda function"
  value       = aws_lambda_function.download.function_name
}

output "download_function_arn" {
  description = "ARN of the download lambda function"
  value       = aws_lambda_function.download.arn
}

output "file_metadata_function_name" {
  description = "Name of the file metadata fetching function"
  value       = aws_lambda_function.fetch_file_metadata.function_name
}

output "file_metadata_arn" {
  description = "ARN of the file metadata lambda function"
  value       = aws_lambda_function.fetch_file_metadata.arn
}

output "delete_lambda_function_name" {
  description = "Name of the delete lambda function"
  value       = aws_lambda_function.delete_file.function_name
}

output "delete_function_arn" {
  description = "ARN of the delete file lambda function"
  value       = aws_lambda_function.delete_file.arn
}

output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}
