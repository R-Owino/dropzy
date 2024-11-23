# main entry file for terraform

module "cognito" {
  source = "./modules/cognito"

  project_name        = var.project_name
  environment         = var.environment
  lambda_function_arn = module.lambda.userdata_function_arn
  dynamodb_table_name = "userdata"
}

module "dynamodb" {
  source = "./modules/dynamodb"

  project_name                  = var.project_name
  environment                   = var.environment
  userdata_table_name           = "userdata"
  documents_metadata_table_name = "documents-metadata"
}

module "lambda" {
  source = "./modules/lambda"

  project_name                           = var.project_name
  environment                            = var.environment
  dynamodb_userdata_table_name           = module.dynamodb.table_name
  dynamodb_userdata_table_arn            = module.dynamodb.table_arn
  dynamodb_documents_metadata_table_name = module.dynamodb.documents_metadata_table_name
  dynamodb_documents_metadata_table_arn  = module.dynamodb.documents_metadata_table_arn
  s3_bucket_name                         = module.s3.bucket_name
  s3_bucket_arn                          = module.s3.bucket_arn
}

module "api_gateway" {
  source = "./modules/api_gateway"

  project_name                  = var.project_name
  environment                   = var.environment
  userpool_arn                  = module.cognito.userpool_arn
  upload_lambda_invoke_arn      = module.lambda.upload_function_arn
  download_lambda_invoke_arn    = module.lambda.download_function_arn
  upload_lambda_function_name   = module.lambda.upload_function_name
  download_lambda_function_name = module.lambda.download_function_name
}

module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
}
