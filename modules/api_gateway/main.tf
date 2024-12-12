# routes document upload and download requests

resource "aws_api_gateway_rest_api" "files" {
  name        = "${var.project_name}-${var.environment}-rest-api"
  description = "Document upload and download API"

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

### UPLOAD RESOURCE AND METHOD ###
resource "aws_api_gateway_resource" "upload_file" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  parent_id   = aws_api_gateway_resource.fileshare.id
  path_part   = "upload"
}

resource "aws_api_gateway_method" "upload" {
  rest_api_id   = aws_api_gateway_rest_api.files.id
  resource_id   = aws_api_gateway_resource.upload_file.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "upload_lambda" {
  depends_on              = [aws_api_gateway_method.upload]
  rest_api_id             = aws_api_gateway_rest_api.files.id
  resource_id             = aws_api_gateway_resource.upload_file.id
  http_method             = aws_api_gateway_method.upload.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.upload_lambda_arn}/invocations"

}

resource "aws_api_gateway_method_response" "upload_method_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.upload_file.id
  http_method = aws_api_gateway_method.upload.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "upload_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.upload_file.id
  http_method = aws_api_gateway_method.upload.http_method
  status_code = aws_api_gateway_method_response.upload_method_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,DELETE,GET,POST'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [
    aws_api_gateway_method.upload,
    aws_api_gateway_integration.upload_lambda
  ]
}

### DOWNLOAD RESOURCE AND METHOD ###
resource "aws_api_gateway_resource" "download_file" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  parent_id   = aws_api_gateway_resource.fileshare.id
  path_part   = "download"
}

resource "aws_api_gateway_method" "download" {
  rest_api_id   = aws_api_gateway_rest_api.files.id
  resource_id   = aws_api_gateway_resource.download_file.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "download_lambda" {
  depends_on              = [aws_api_gateway_method.download]
  rest_api_id             = aws_api_gateway_rest_api.files.id
  resource_id             = aws_api_gateway_resource.download_file.id
  http_method             = aws_api_gateway_method.download.http_method
  integration_http_method = "GET"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.download_lambda_arn}/invocations"
}

resource "aws_api_gateway_method_response" "download_method_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.download_file.id
  http_method = aws_api_gateway_method.download.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "download_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.files.id
  resource_id = aws_api_gateway_resource.download_file.id
  http_method = aws_api_gateway_method.download.http_method
  status_code = aws_api_gateway_method_response.download_method_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,DELETE,GET,POST'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [
    aws_api_gateway_method.download,
    aws_api_gateway_integration.download_lambda
  ]
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
}

resource "aws_api_gateway_integration" "file_metadata_lambda" {
  depends_on              = [aws_api_gateway_method.file_metadata]
  rest_api_id             = aws_api_gateway_rest_api.files.id
  resource_id             = aws_api_gateway_resource.file_metadata.id
  http_method             = aws_api_gateway_method.file_metadata.http_method
  integration_http_method = "GET"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.file_metadata_arn}/invocations"
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
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,DELETE,GET,POST'"
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
  integration_http_method = "DELETE"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.delete_lambda_arn}/invocations"
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
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,DELETE,GET,POST'"
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
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,DELETE,GET,POST'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [
    aws_api_gateway_method.cors_options,
    aws_api_gateway_integration.cors_options_integration
  ]
}

resource "aws_api_gateway_deployment" "files" {
  rest_api_id = aws_api_gateway_rest_api.files.id

  depends_on = [
    aws_api_gateway_integration.upload_lambda,
    aws_api_gateway_integration.download_lambda,
    aws_api_gateway_integration.file_metadata_lambda,
    aws_api_gateway_integration.delete_lambda,
    aws_api_gateway_integration.cors_options_integration
  ]

  lifecycle {
    create_before_destroy = true
  }

}

resource "aws_api_gateway_stage" "files" {
  deployment_id = aws_api_gateway_deployment.files.id
  rest_api_id   = aws_api_gateway_rest_api.files.id
  stage_name    = var.environment
}

resource "aws_lambda_permission" "upload_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.upload_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.files.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "download_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.download_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.files.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "file_metadata" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.file_metadata_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.files.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "delete_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.delete_lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.files.execution_arn}/*/*/*"
}
