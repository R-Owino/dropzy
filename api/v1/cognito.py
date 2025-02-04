import boto3
import logging
from botocore.exceptions import ClientError
from config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cognito_client = boto3.client("cognito-idp",
                              region_name=Config.AWS_REGION)


def register_user(email, username, password):
    """adds a user to cognito userpool"""
    try:
        cognito_client.sign_up(
            ClientId=Config.AWS_COGNITO_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "preferred_username", "Value": username}
            ]
        )
        return {"Success": True}
    except ClientError as e:
        return {
            "Success": False,
            "message": e.response["Error"]["Message"]
        }


def confirm_user(email, code):
    """verifies a user's email address"""
    try:
        cognito_client.confirm_sign_up(
            ClientId=Config.AWS_COGNITO_CLIENT_ID,
            Username=email,
            ConfirmationCode=code
        )
        logger.info("User confirmation successful")
        return {"Success": True}
    except ClientError as e:
        error_message = e.response["Error"]["Message"]
        logger.error(f"Failed to confirm user {email}: {error_message}")
        return {"Success": False, "message": error_message}


def resend_verification_code(email):
    """resends the verification code upon request"""
    try:
        cognito_client.resend_confirmation_code(
            ClientId=Config.AWS_COGNITO_CLIENT_ID,
            Username=email
        )
        return {"Success": True}
    except ClientError as e:
        return {"Success": False, "message": e.response["Error"]["Message"]}


def login_user(email, password):
    """logs in a user"""
    try:
        response = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password
            },
            ClientId=Config.AWS_COGNITO_CLIENT_ID
        )
        return {"Success": True, "tokens": response["AuthenticationResult"]}
    except ClientError as e:
        return {"Success": False, "message": e.response["Error"]["Message"]}
