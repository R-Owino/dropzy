import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """app configurations"""
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "xyz-xyz-xyz")
    AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
    AWS_COGNITO_USER_POOL_ID = os.getenv("AWS_COGNITO_USER_POOL_ID")
    AWS_COGNITO_CLIENT_ID = os.getenv("AWS_COGNITO_CLIENT_ID")
    API_GATEWAY_INVOKE_URL = os.getenv("AWS_API_GATEWAY_INVOKE_URL")
    AWS_API_GATEWAY_FETCH_METADATA_URL = os.getenv("AWS_API_GATEWAY_FETCH_METADATA_URL")  # noqa: F401
    AWS_API_GATEWAY_DELETE_URL = os.getenv("AWS_API_GATEWAY_DELETE_URL")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    DOCUMENTS_DYNAMODB_TABLE_NAME = os.getenv("DOCUMENTS_DYNAMODB_TABLE_NAME")
    USERDATA_DYNAMODB_TABLE_NAME = os.getenv("USERDATA_DYNAMODB_TABLE_NAME")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
