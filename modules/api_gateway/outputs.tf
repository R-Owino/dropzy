/* API gateway module outputs */

output "api_gateway_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.files.id
}

output "api_gateway_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_api_gateway_rest_api.files.execution_arn
}

output "api_gateway_invoke_url" {
  description = "Invoke URL of the API Gateway"
  value       = aws_api_gateway_stage.files.invoke_url
}

output "upload_url" {
  description = "Invoke URL for uploading files"
  value       = "${aws_api_gateway_stage.files.invoke_url}/files/upload"
}

output "fetch_metadata_url" {
  description = "Invoke URL for fetching file metadata"
  value       = "${aws_api_gateway_stage.files.invoke_url}/files/metadata"
}

output "delete_url" {
  description = "Invoke URL for deleting files"
  value       = "${aws_api_gateway_stage.files.invoke_url}/files/delete"
}
