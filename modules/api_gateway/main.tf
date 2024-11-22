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
  path_part   = "docs"
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
