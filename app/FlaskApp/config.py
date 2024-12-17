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
    AWS_API_GATEWAY_UPLOAD_URL = os.getenv("AWS_API_GATEWAY_UPLOAD_URL")
    AWS_API_GATEWAY_DOWNLOAD_URL = os.getenv("AWS_API_GATEWAY_DOWNLOAD_URL")
    AWS_API_GATEWAY_FETCH_METADATA_URL = os.getenv("AWS_API_GATEWAY_FETCH_METADATA_URL")
    AWS_API_GATEWAY_DELETE_URL = os.getenv("AWS_API_GATEWAY_DELETE_URL")
