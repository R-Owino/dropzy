/* dynamodb table resources */

# userdata table
resource "aws_dynamodb_table" "userdata" {
  name         = var.userdata_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UserId"

  attribute {
    name = "UserId"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "userdata"
  }
}

# documents metadata table
resource "aws_dynamodb_table" "documents_metadata" {
  name         = var.documents_metadata_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "DocumentId"

  attribute {
    name = "UserId"
    type = "S"
  }

  attribute {
    name = "DocumentId"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "documents-metadata"
  }

}
