/* lambda functions outputs */

output "userdata_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.userdata.arn
}

output "upload_function_name" {
  description = "Name of the upload Lambda function"
  value       = aws_lambda_function.upload.function_name
}

output "upload_function_arn" {
  description = "ARN of the upload Lambda function"
  value       = aws_lambda_function.upload.arn
}

output "download_function_name" {
  description = "Name of the download Lambda function"
  value       = aws_lambda_function.download.function_name
}

output "file_metadata_lambda_function_name" {
  description = "Name of the file metadata fetching function"
  value = aws_lambda_function.fetch_file_metadata
}

output "download_function_arn" {
  description = "ARN of the download Lambda function"
  value       = aws_lambda_function.download.arn
}

output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}
