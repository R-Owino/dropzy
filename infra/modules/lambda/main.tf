/* lambda functions defined in the module */

data "archive_file" "userdata_lambda_zip_file" {
  type        = "zip"
  source_file = "${path.module}/userdata_lambda.py"
  output_path = "${path.module}/userdata_lambda.zip"
}

data "archive_file" "upload_lambda_zip_file" {
  type        = "zip"
  source_file = "${path.module}/upload_file_metadata_lambda.py"
  output_path = "${path.module}/upload_file_metadata_lambda.zip"
}

data "archive_file" "fetch_file_metadata_zip_file" {
  type        = "zip"
  source_file = "${path.module}/file_metadata_lambda.py"
  output_path = "${path.module}/file_metadata_lambda.zip"
}

data "archive_file" "delete_file_lambda_zip_file" {
  type        = "zip"
  source_file = "${path.module}/delete_file_lambda.py"
  output_path = "${path.module}/delete_file_lambda.zip"
}

resource "aws_lambda_function" "userdata" {
  filename      = "${path.module}/userdata_lambda.zip"
  function_name = "${var.project_name}-userdata-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "userdata_lambda.lambda_handler"
  runtime       = "python3.12"
  timeout       = 35

  source_code_hash = data.archive_file.userdata_lambda_zip_file.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_userdata_table_name
    }
  }
}

resource "aws_lambda_function" "upload_file_metadata" {
  filename      = "${path.module}/upload_file_metadata_lambda.zip"
  function_name = "${var.project_name}-upload-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "upload_file_metadata_lambda.lambda_handler"
  runtime       = "python3.12"
  timeout       = 35

  source_code_hash = data.archive_file.upload_lambda_zip_file.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_NAME      = var.s3_bucket_name
      DYNAMODB_TABLE_NAME = var.dynamodb_documents_metadata_table_name
    }
  }
}

resource "aws_lambda_function" "fetch_file_metadata" {
  filename      = "${path.module}/file_metadata_lambda.zip"
  function_name = "${var.project_name}-fetch-file-metadata-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "file_metadata_lambda.lambda_handler"
  runtime       = "python3.12"
  timeout       = 35

  source_code_hash = data.archive_file.fetch_file_metadata_zip_file.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_documents_metadata_table_name
    }
  }
}

resource "aws_lambda_function" "delete_file" {
  filename      = "${path.module}/delete_file_lambda.zip"
  function_name = "${var.project_name}-delete-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "delete_file_lambda.lambda_handler"
  runtime       = "python3.12"
  timeout       = 30

  source_code_hash = data.archive_file.delete_file_lambda_zip_file.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_NAME      = var.s3_bucket_name
      DYNAMODB_TABLE_NAME = var.dynamodb_documents_metadata_table_name
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.project_name}-lambda-role"
  assume_role_policy = file("${path.module}/lambda-policy.json")
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy" "userdata_lambda_dynamodb" {
  name = "${var.project_name}-userdata-lambda-dynamodb-policy-${var.environment}"
  role = aws_iam_role.lambda_role.name

  policy = templatefile("${path.module}/userdata-lambda-dynamodb-policy.json", {
    dynamodb_userdata_table_arn = var.dynamodb_userdata_table_arn
  })
}

resource "aws_iam_role_policy" "upload_file_dynamodb" {
  name = "${var.project_name}-upload-dynamodb-policy-${var.environment}"
  role = aws_iam_role.lambda_role.name

  policy = templatefile("${path.module}/upload-lambda-dynamodb-policy.json", {
    dynamodb_documents_metadata_table_arn = var.dynamodb_documents_metadata_table_arn
  })
}

resource "aws_iam_role_policy" "file_metadata_lambda_dynamodb" {
  name = "${var.project_name}-file-metadata-lambda-dynamodb-policy-${var.environment}"
  role = aws_iam_role.lambda_role.name

  policy = templatefile("${path.module}/file-metadata-lambda-dynamodb-policy.json", {
    dynamodb_documents_metadata_table_arn = var.dynamodb_documents_metadata_table_arn
  })
}

resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "${var.project_name}-lambda-s3-policy-${var.environment}"
  role = aws_iam_role.lambda_role.name

  policy = templatefile("${path.module}/lambda-s3-policy.json", {
    s3_bucket_arn = var.s3_bucket_arn
  })
}

resource "aws_iam_role_policy" "delete_file_policy" {
  name = "${var.project_name}-s3-dynamodb-delete-policy-${var.environment}"
  role = aws_iam_role.lambda_role.name

  policy = templatefile("${path.module}/lambda-delete-file-policy.json", {
    s3_bucket_arn                         = var.s3_bucket_arn,
    dynamodb_documents_metadata_table_arn = var.dynamodb_documents_metadata_table_arn
  })
}

resource "aws_iam_role_policy" "lambda_logs" {
  name = "${var.project_name}-lambda-logs-policy-${var.environment}"
  role = aws_iam_role.lambda_role.name

  policy = file("${path.module}/lambda-logs-policy.json")

}
