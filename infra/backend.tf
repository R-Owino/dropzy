# Export local tfstate to S3

terraform {
  backend "s3" {
    bucket = "fileshare-tfstate-7up"
    key = "terraform.state"
    region = "us-west-2"
    dynamodb_table = "terraform_lock"
    encrypt = true
  }
}
