/* S3 resources */

resource "random_string" "bucket_name_suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "aws_s3_bucket" "files" {
  bucket = "${var.project_name}-files-${random_string.bucket_name_suffix.result}"

  force_destroy = true

  tags = {
    Name        = "${var.project_name}-files",
    Environment = var.environment
  }
}

resource "aws_s3_bucket_ownership_controls" "files" {
  bucket = aws_s3_bucket.files.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "files" {
  bucket = aws_s3_bucket.files.id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = false
}

resource "aws_s3_bucket_versioning" "files-versioning" {
  bucket = aws_s3_bucket.files.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.files.id
  policy = templatefile("${path.module}/bucket-policy.json", {
    bucket_arn = aws_s3_bucket.files.arn
  })

  depends_on = [aws_s3_bucket_public_access_block.files]
}

resource "aws_s3_bucket_lifecycle_configuration" "files_lifecycle" {
  bucket = aws_s3_bucket.files.id

  rule {
    id     = "move-to-intelliget-tiering"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}

resource "aws_lambda_permission" "upload_metadata_lambda" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = var.upload_metadata_function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.files.arn
}

resource "aws_s3_bucket_notification" "s3_lambda_trigger" {
  depends_on = [aws_lambda_permission.upload_metadata_lambda]

  bucket = aws_s3_bucket.files.id
  lambda_function {
    lambda_function_arn = var.upload_metadata_function_arn
    events              = ["s3:ObjectCreated:*"]
  }
}

resource "aws_s3_bucket_cors_configuration" "files" {
  bucket = aws_s3_bucket.files.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
