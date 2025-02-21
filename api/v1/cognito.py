import boto3
import logging
import re
from botocore.exceptions import ClientError
from v1.config import Config
from typing import Dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# initialize cognito client
cognito_client = boto3.client("cognito-idp",
                              region_name=Config.AWS_REGION)


def register_user(
    email: str,
    username: str,
    password: str
) -> Dict[str, bool | str]:
    """
    Registers a new user in the AWS Cognito user pool

    Args:
        email (str): user's email address
        username (str): preffered username for the user
        password (str): password for the user account

    Returns:
        dict: dictionary with 'Success' (bool) and
                optional 'message' (str) if an error occurs
    """
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return {"Success": False, "message": "Invalid email format"}

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


def confirm_user(email: str, code: str) -> Dict[str, bool | str]:
    """
    Confirms a user's email address using the verification code
    from AWS Cognito

    Args:
        email (str): user's email address
        code (str): confirmation code sent to the user's email

    Returns:
        dict: dictionary with 'Success' (bool) and
                optional 'message' (str) if an error occurs
    """
    if not code:
        return {"Success": False, "message": "Confirmation code is required"}

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


def resend_verification_code(email: str) -> Dict[str, bool | str]:
    """
    Resends the verification code to a user who has not confirmed their email

    Args:
        email (str): user's email address

    Returns:
        dict: dictionary with 'Success' (bool) and
                optional 'message' (str) if an error occurs
    """
    if not email:
        return {"Success": False, "message": "Email is required"}

    try:
        cognito_client.resend_confirmation_code(
            ClientId=Config.AWS_COGNITO_CLIENT_ID,
            Username=email
        )
        return {"Success": True}
    except ClientError as e:
        return {"Success": False, "message": e.response["Error"]["Message"]}


def login_user(
    email: str,
    password: str
) -> Dict[str, bool | str | Dict[str, str]]:
    """
    Authenticates a user and retrieves authentication tokens from AWS Cognito

    Args:
        email (str): user's email address
        password (str): user's password

    Returns:
        dict: dictionary with 'Success' (bool) and
                either 'tokens' (dict) or 'message' (str) if an error occurs
    """
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


def email_exists(email: str) -> bool:
    """
    Checks if an email address is already registered in Cognito

    Args:
        email (str): the email address to check

        Returns:
            bool: True if the email address is already registered,
                False otherwise
    """
    try:
        response = cognito_client.list_users(
            UserPoolId=Config.AWS_COGNITO_USER_POOL_ID,
            Filter=f'email = "{email}"'
        )
        return len(response['Users']) > 0
    except ClientError as e:
        logger.error(f"Error checking email existence: {e}")
        return False
