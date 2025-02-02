
resource "aws_api_gateway_rest_api" "files" {
  name        = "${var.project_name}-${var.environment}-rest-api"
  description = "File metadata upload and file delete API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_authorizer" "cognito" {
  name          = "apigw-cognito-authorizer"
  rest_api_id   = aws_api_gateway_rest_api.files.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = [var.userpool_arn]

}

resource "aws_api_gateway_resource" "fileshare" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  parent_id   = aws_api_gateway_rest_api.files.root_resource_id
  path_part   = "files"
}

### FETCH FILE METADATA RESOURCE AND METHOD ###
resource "aws_api_gateway_resource" "file_metadata" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  parent_id   = aws_api_gateway_resource.fileshare.id
  path_part   = "metadata"
}

resource "aws_api_gateway_method" "file_metadata" {
  rest_api_id   = aws_api_gateway_rest_api.files.id
  resource_id   = aws_api_gateway_resource.file_metadata.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id

  request_parameters = {
    "method.request.querystring.search" = false
    "method.request.querystring.limit"  = false
  }
}

resource "aws_api_gateway_integration" "file_metadata_lambda" {
  depends_on              = [aws_api_gateway_method.file_metadata]
  rest_api_id             = aws_api_gateway_rest_api.files.id
  resource_id             = aws_api_gateway_resource.file_metadata.id
  http_method             = aws_api_gateway_method.file_metadata.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.file_metadata_invoke_arn
  request_templates = {
    "application/json" = jsonencode({
      queryStringParameters = {
        search = "$input.params('search')"
        limit  = "$input.params('limit')"
      }
    })
  }

  passthrough_behavior = "WHEN_NO_TEMPLATES"

}

resource "aws_api_gateway_method_response" "metadata_method_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.file_metadata.id
  http_method = aws_api_gateway_method.file_metadata.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "metadata_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.file_metadata.id
  http_method = aws_api_gateway_method.file_metadata.http_method
  status_code = aws_api_gateway_method_response.metadata_method_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,GET'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [
    aws_api_gateway_method.file_metadata,
    aws_api_gateway_integration.file_metadata_lambda
  ]
}

### DELETE RESOURCE AND METHOD ###
resource "aws_api_gateway_resource" "delete_file" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  parent_id   = aws_api_gateway_resource.fileshare.id
  path_part   = "delete"
}

resource "aws_api_gateway_method" "delete" {
  rest_api_id   = aws_api_gateway_rest_api.files.id
  resource_id   = aws_api_gateway_resource.delete_file.id
  http_method   = "DELETE"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "delete_lambda" {
  depends_on              = [aws_api_gateway_method.delete]
  rest_api_id             = aws_api_gateway_rest_api.files.id
  resource_id             = aws_api_gateway_resource.delete_file.id
  http_method             = aws_api_gateway_method.delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.delete_lambda_invoke_arn
}

resource "aws_api_gateway_method_response" "delete_method_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.delete_file.id
  http_method = aws_api_gateway_method.delete.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "delete_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.delete_file.id
  http_method = aws_api_gateway_method.delete.http_method
  status_code = aws_api_gateway_method_response.delete_method_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,DELETE'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [
    aws_api_gateway_method.delete,
    aws_api_gateway_integration.delete_lambda
  ]
}

# CORS OPTIONS METHOD ###
resource "aws_api_gateway_method" "cors_options" {
  rest_api_id   = aws_api_gateway_rest_api.files.id
  resource_id   = aws_api_gateway_resource.fileshare.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cors_options_integration" {
  rest_api_id             = aws_api_gateway_rest_api.files.id
  resource_id             = aws_api_gateway_resource.fileshare.id
  http_method             = aws_api_gateway_method.cors_options.http_method
  integration_http_method = aws_api_gateway_method.cors_options.http_method
  type                    = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "cors_options_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.fileshare.id
  http_method = aws_api_gateway_method.cors_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "cors_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.fileshare.id
  http_method = aws_api_gateway_method.cors_options.http_method
  status_code = aws_api_gateway_method_response.cors_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,DELETE,GET'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [
    aws_api_gateway_method.cors_options,
    aws_api_gateway_integration.cors_options_integration
  ]
}

### DEPLOY THE API ###
resource "aws_api_gateway_deployment" "files" {
  rest_api_id = aws_api_gateway_rest_api.files.id

  depends_on = [
    aws_api_gateway_integration.file_metadata_lambda,
    aws_api_gateway_integration.delete_lambda,
    aws_api_gateway_integration.cors_options_integration
  ]

  lifecycle {
    create_before_destroy = true
  }

}

### STAGE THE API AND SET UP CLOUDWATCH LOGGING ###
resource "aws_iam_role" "apilogs" {
  name               = "api-gateway-logs-role"
  assume_role_policy = file("${path.module}/api-gateway-policy.json")
}

resource "aws_iam_role_policy_attachment" "apilogs" {
  role       = aws_iam_role.apilogs.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

resource "aws_api_gateway_account" "apilogs" {
  cloudwatch_role_arn = aws_iam_role.apilogs.arn

  depends_on = [aws_iam_role_policy_attachment.apilogs]
}

resource "aws_cloudwatch_log_group" "apilogs" {
  name              = "/aws/apigateway/${aws_api_gateway_rest_api.files.id}/${var.environment}"
  retention_in_days = 7

  tags = {
    environment = var.environment
    Name        = "${var.project_name}-API-logs"
  }
}
resource "aws_api_gateway_stage" "files" {
  deployment_id = aws_api_gateway_deployment.files.id
  rest_api_id   = aws_api_gateway_rest_api.files.id
  stage_name    = var.environment

  depends_on = [aws_api_gateway_account.apilogs]

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apilogs.arn
    format = jsonencode({
      requestId               = "$context.requestId"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
    })
  }
}

resource "aws_api_gateway_method_settings" "apilogs" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  stage_name  = aws_api_gateway_stage.files.stage_name
  method_path = "*/*"

  settings {
    logging_level      = "INFO"
    data_trace_enabled = true
    metrics_enabled    = true
  }

  depends_on = [aws_api_gateway_stage.files]
}

### GRANT API GATEWAY PERMISSION TO INVOKE LAMBDA FUNCTIONS ###
resource "aws_lambda_permission" "file_metadata" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.file_metadata_lambda_function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.files.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "delete_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.delete_lambda_function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.files.execution_arn}/*/*/*"
}
