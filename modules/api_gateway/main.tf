# routes document upload and download requests

resource "aws_api_gateway_rest_api" "docs" {
  name        = "${var.project_name}-${var.environment}-rest-api"
  description = "Document upload and download API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_authorizer" "cognito" {
  name          = "apigw-cognito-authorizer"
  rest_api_id   = aws_api_gateway_rest_api.docs.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = [var.userpool_arn]

}

resource "aws_api_gateway_resource" "file-share" {
  rest_api_id = aws_api_gateway_rest_api.docs.id
  parent_id   = aws_api_gateway_rest_api.docs.root_resource_id
  path_part   = "files"
}

resource "aws_api_gateway_method" "upload" {
  rest_api_id   = aws_api_gateway_rest_api.docs.id
  resource_id   = aws_api_gateway_resource.file-share.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_method" "download" {
  rest_api_id   = aws_api_gateway_rest_api.docs.id
  resource_id   = aws_api_gateway_resource.file-share.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_method" "get_file_metadata" {
  rest_api_id   = aws_api_gateway_rest_api.docs.id
  resource_id   = aws_api_gateway_resource.file-share.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_method" "delete_file" {
  rest_api_id   = aws_api_gateway_rest_api.docs.id
  resource_id   = aws_api_gateway_resource.file-share.id
  http_method   = "DELETE"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "upload_lambda" {
  rest_api_id = aws_api_gateway_rest_api.docs.id
  resource_id = aws_api_gateway_resource.file-share.id
  http_method = aws_api_gateway_method.upload.http_method
  type        = "AWS_PROXY"
  uri         = var.upload_lambda_invoke_arn

}

resource "aws_api_gateway_integration" "download_lambda" {
  rest_api_id = aws_api_gateway_rest_api.docs.id
  resource_id = aws_api_gateway_resource.file-share.id
  http_method = aws_api_gateway_method.download.http_method
  type        = "AWS_PROXY"
  uri         = var.download_lambda_invoke_arn
}

resource "aws_api_gateway_integration" "fetch_file_metadata" {
  rest_api_id = aws_api_gateway_rest_api.docs.id
  resource_id = aws_api_gateway_resource.file-share.id
  http_method = aws_api_gateway_method.get_file_metadata.http_method
  type        = "AWS_PROXY"
  uri         = var.file_metadata_invoke_arn
}

resource "aws_api_gateway_integration" "delete_lambda" {
  rest_api_id = aws_api_gateway_rest_api.docs.id
  resource_id = aws_api_gateway_resource.file-share.id
  http_method = aws_api_gateway_method.get_file_metadata.http_method
  type        = "AWS_PROXY"
  uri         = var.delete_lambda_invoke_arn
}

resource "aws_api_gateway_method" "cors_options" {
  rest_api_id   = aws_api_gateway_rest_api.docs.id
  resource_id   = aws_api_gateway_resource.file-share.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cors_options" {
  rest_api_id       = aws_api_gateway_rest_api.docs.id
  resource_id       = aws_api_gateway_resource.file-share.id
  http_method       = aws_api_gateway_method.cors_options.http_method
  type              = "MOCK"
  request_templates = { "application/json" = "{\"statusCode\": 200}" }
}

resource "aws_api_gateway_method_response" "cors_options_response" {
  rest_api_id = aws_api_gateway_rest_api.docs.id
  resource_id = aws_api_gateway_resource.file-share.id
  http_method = aws_api_gateway_method.cors_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "cors_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.docs.id
  resource_id = aws_api_gateway_resource.file-share.id
  http_method = aws_api_gateway_method.cors_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type, Authorization'",
    "method.response.header.Access-Control-Allow-Methods" = "'POST, OPTIONS'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

resource "aws_api_gateway_deployment" "docs" {
  rest_api_id = aws_api_gateway_rest_api.docs.id

  depends_on = [
    aws_api_gateway_integration.upload_lambda,
    aws_api_gateway_integration.download_lambda
  ]

  lifecycle {
    create_before_destroy = true
  }

}

resource "aws_api_gateway_stage" "docs" {
  deployment_id = aws_api_gateway_deployment.docs.id
  rest_api_id   = aws_api_gateway_rest_api.docs.id
  stage_name    = var.environment
}

resource "aws_lambda_permission" "upload_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.upload_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.docs.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "download_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.download_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.docs.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "file_metadata" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.file_metadata_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.docs.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "delete_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.delete_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.docs.execution_arn}/*/*/*"
}
