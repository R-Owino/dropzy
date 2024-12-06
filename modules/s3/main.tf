/* S3 resources */

resource "aws_s3_bucket" "files" {
  bucket = "${var.project_name}-files"

  tags = {
    Name        = "${var.project_name}-files",
    Environment = var.environment
  }
}

resource "aws_s3_bucket_acl" "files" {
  bucket = aws_s3_bucket.files.id
  acl    = "private"

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
    id = "move-to-intelliget-tiering"
    status = "Enabled"

    transition {
      days = 90
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}
