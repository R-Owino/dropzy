/* S3 resources */

resource "aws_s3_bucket" "files" {
  bucket = "${var.project_name}-files"

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
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
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
