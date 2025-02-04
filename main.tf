# main entry file for terraform

module "cognito" {
  source = "./modules/cognito"

  project_name           = var.project_name
  environment            = var.environment
  userdata_function_arn  = module.lambda.userdata_function_arn
  userdata_function_name = module.lambda.userdata_function_name
  dynamodb_table_name    = var.userdata_table_name
}

module "dynamodb" {
  source = "./modules/dynamodb"

  project_name                  = var.project_name
  environment                   = var.environment
  userdata_table_name           = var.userdata_table_name
  documents_metadata_table_name = var.documents_metadata_table_name
}

module "lambda" {
  source = "./modules/lambda"

  project_name                           = var.project_name
  environment                            = var.environment
  dynamodb_userdata_table_name           = module.dynamodb.userdata_table_name
  dynamodb_userdata_table_arn            = module.dynamodb.userdata_table_arn
  dynamodb_documents_metadata_table_name = module.dynamodb.documents_metadata_table_name
  dynamodb_documents_metadata_table_arn  = module.dynamodb.documents_metadata_table_arn
  s3_bucket_name                         = module.s3.bucket_name
  s3_bucket_arn                          = module.s3.bucket_arn
}

module "api_gateway" {
  source = "./modules/api_gateway"

  aws_region                         = var.aws_region
  project_name                       = var.project_name
  environment                        = var.environment
  userpool_arn                       = module.cognito.userpool_arn
  file_metadata_arn                  = module.lambda.file_metadata_function_arn
  delete_lambda_arn                  = module.lambda.delete_function_arn
  file_metadata_invoke_arn           = module.lambda.file_metadata_invoke_arn
  delete_lambda_invoke_arn           = module.lambda.delete_lambda_invoke_arn
  file_metadata_lambda_function_name = module.lambda.file_metadata_function_name
  delete_lambda_function_name        = module.lambda.delete_lambda_function_name
}

module "s3" {
  source = "./modules/s3"

  project_name                = var.project_name
  environment                 = var.environment
  upload_lambda_function_name = module.lambda.upload_function_name
  upload_lambda_arn           = module.lambda.upload_function_arn
}
