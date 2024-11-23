/* S3 resources */

resource "aws_s3_bucket" "documents" {
  bucket = "${var.project_name}-documents"

  tags = {
    Name        = "${var.project_name}-documents",
    Environment = var.environment
  }
}

resource "aws_s3_bucket_acl" "documents" {
  bucket = aws_s3_bucket.documents.id
  acl    = "private"

}

resource "aws_s3_bucket_versioning" "documents-versioning" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.documents.id
  policy = templatefile("${path.module}/bucket-policy.json", {
    bucket_arn = aws_s3_bucket.documents.arn
  })
}
