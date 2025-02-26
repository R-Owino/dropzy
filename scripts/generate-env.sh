#!/usr/bin/env bash

# capture Terraform outputs and write them directly to Flask's .env file

TERRAFORM_DIR="infra"
ENV_FILE="api/v1/.env"
TEMP_ENV_FILE="${ENV_FILE}.tmp"
PROJECT_ROOT=$(pwd)

# ensure the terraform directory exists
if [ ! -d "$TERRAFORM_DIR" ]; then
    echo "Error: Terraform directory '$TERRAFORM_DIR' does not exist"
    exit 1
fi

# ensure the API directory exists
API_DIR=$(dirname "$ENV_FILE")
if [ ! -d "$API_DIR" ]; then
    echo "Error: API directory '$API_DIR' does not exist"
    exit 1
fi

# ensure the .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "# Auto-generated .env file" > "$ENV_FILE"
fi

# generate terraform outputs
cd "$TERRAFORM_DIR" || exit
terraform output -json > "$PROJECT_ROOT/terraform_output.json"
cd "$PROJECT_ROOT" || exit

# check if secret key already exists, otherwise create one
if grep -q "^SECRET_KEY=" "$ENV_FILE"; then
    SECRET_KEY_VALUE=$(grep "^SECRET_KEY=" "$ENV_FILE" | head -n1)
else
    SECRET_KEY_VALUE="SECRET_KEY=$(openssl rand -hex 32)"
fi

# check if Redis variables already exist, otherwise set defaults
if grep -q "^REDIS_HOST=" "$ENV_FILE"; then
    REDIS_HOST_VALUE=$(grep "^REDIS_HOST=" "$ENV_FILE" | head -n1)
else
    REDIS_HOST_VALUE="REDIS_HOST=some-redis"
fi

if grep -q "^REDIS_PORT=" "$ENV_FILE"; then
    REDIS_PORT_VALUE=$(grep "^REDIS_PORT=" "$ENV_FILE" | head -n1)
else
    REDIS_PORT_VALUE="REDIS_PORT=6379"
fi

if grep -q "^REDIS_PASSWORD=" "$ENV_FILE"; then
    REDIS_PASSWORD_VALUE=$(grep "^REDIS_PASSWORD=" "$ENV_FILE" | head -n1)
else
    REDIS_PASSWORD_VALUE="REDIS_PASSWORD=$(openssl rand -hex 32)"
fi

{
    echo "# Auto-generated .env file"
    echo "$SECRET_KEY_VALUE"
    echo "$REDIS_HOST_VALUE"
    echo "$REDIS_PORT_VALUE"
    echo "$REDIS_PASSWORD_VALUE"
} >> "$TEMP_ENV_FILE"

# get terraform outputs and append them to the temporary .env file
{
    echo ""
    echo "AWS_REGION=$(jq -r '.aws_region.value' "terraform_output.json")"
    echo "AWS_COGNITO_USER_POOL_ID=$(jq -r '.cognito_user_pool_id.value' "terraform_output.json")"
    echo "AWS_COGNITO_CLIENT_ID=$(jq -r '.cognito_user_pool_client_id.value' "terraform_output.json")"
    echo ""

    echo "AWS_API_GATEWAY_INVOKE_URL=$(jq -r '.api_gateway_invoke_url.value' "terraform_output.json")"
    echo "AWS_API_GATEWAY_FETCH_METADATA_URL=$(jq -r '.api_gateway_fetch_metadata_url.value' "terraform_output.json")"
    echo "AWS_API_GATEWAY_DELETE_URL=$(jq -r '.api_gateway_delete_url.value' "terraform_output.json")"
    echo ""

    echo "S3_BUCKET_NAME=$(jq -r '.s3_bucket_name.value' "terraform_output.json")"
    echo "DOCUMENTS_DYNAMODB_TABLE_NAME=$(jq -r '.documents_dynamodb_table_name.value' "terraform_output.json")"
    echo "USERDATA_DYNAMODB_TABLE_NAME=$(jq -r '.userdata_dynamodb_table_name.value' "terraform_output.json")"
} >> "$TEMP_ENV_FILE"

# replace the temporary .env file with the new one
mv "$TEMP_ENV_FILE" "$ENV_FILE"

rm "terraform_output.json"

echo ".env file has been updated successfully!"
