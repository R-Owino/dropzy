# create cognito user pool and client

resource "aws_cognito_user_pool" "userpool" {
  name = "${var.project_name}-${var.environment}"

  schema {
    attribute_data_type      = "String"
    name                     = "email"
    required                 = true
    mutable                  = true
    developer_only_attribute = false
  }

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  username_attributes = ["email"]
  username_configuration {
    case_sensitive = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  lambda_config {
    post_confirmation = var.lambda_function_arn
  }

  tags = {
    Name = "paper-trail-user-pool"
  }
}

resource "aws_cognito_user_pool_client" "userpool_client" {
  name                          = "${var.project_name}-client-${var.environment}"
  user_pool_id                  = aws_cognito_user_pool.userpool.id
  generate_secret               = false
  supported_identity_providers  = ["COGNITO"]
  explicit_auth_flows           = ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH"]
  prevent_user_existence_errors = "LEGACY"
  refresh_token_validity        = 1
  access_token_validity         = 1
  id_token_validity             = 1
  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "hours"
  }
}

data "aws_region" "current" {}

resource "aws_cognito_user_pool_domain" "cognito_domain" {
  domain       = var.project_name
  user_pool_id = aws_cognito_user_pool.userpool.id
}
