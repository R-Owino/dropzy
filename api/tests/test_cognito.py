#!/usr/bin/python3

import pytest
import boto3
from moto import mock_aws
from botocore.exceptions import ClientError
from v1.cognito import (register_user,
                        confirm_user,
                        resend_verification_code,
                        login_user,
                        email_exists)
from v1.config import Config
from unittest.mock import patch


@pytest.fixture
def cognito_client():
    """Mock AWS Cognito client"""
    with mock_aws():
        client = boto3.client("cognito-idp", region_name=Config.AWS_REGION)

        # create a user pool
        user_pool = client.create_user_pool(PoolName="test_pool")
        user_pool_id = user_pool["UserPool"]["Id"]
        Config.AWS_COGNITO_USER_POOL_ID = user_pool_id

        # create a userpool client
        client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName="test_client",
            GenerateSecret=False
        )
        client_id = client.list_user_pool_clients(
            UserPoolId=user_pool_id,
            MaxResults=1)["UserPoolClients"][0]["ClientId"]
        Config.AWS_COGNITO_CLIENT_ID = client_id
        yield client


@mock_aws
def test_register_user(cognito_client):
    """Test user registration in Cognito"""
    response = register_user(
        "testuser@example.com",
        "testuser",
        "SecurePass123!"
    )
    assert response["Success"] is True


@mock_aws
def test_register_user_existing(cognito_client):
    """Test registering a user that already exists"""
    cognito_client.sign_up(
        ClientId=Config.AWS_COGNITO_CLIENT_ID,
        Username="testuser@example.com",
        Password="SecurePass123!",
        UserAttributes=[{"Name": "email", "Value": "testuser@example.com"}]
    )
    response = register_user(
        "testuser@example.com",
        "testuser",
        "SecurePass123!"
    )
    assert response["Success"] is False
    assert "message" in response


@mock_aws
def test_register_user_invalid_email(cognito_client):
    """Test registering a user with an invalid email format"""
    response = register_user("invalid-email", "testuser", "SecurePass123!")

    assert response["Success"] is False
    assert response["message"] == "Invalid email format"


@mock_aws
def test_register_user_missing_fields(cognito_client):
    """Test registering a user with missing fields"""
    response = register_user("", "testuser", "SecurePass123!")

    assert response["Success"] is False
    assert "message" in response


@mock_aws
def test_confirm_user(cognito_client):
    """Test successful user confirmation"""
    cognito_client.admin_create_user(
        UserPoolId=(
            cognito_client.list_user_pools(MaxResults=1)
            ["UserPools"][0]["Id"]
        ),
        Username="testuser@example.com"
    )
    response = confirm_user("testuser@example.com", "123456")
    assert response["Success"] is True


@mock_aws
def test_confirm_user_invalid_code(cognito_client):
    """Test confirming a user with an invalid code"""
    response = confirm_user("testuser@example.com", "000000")
    assert response["Success"] is False
    assert "message" in response


@mock_aws
def test_confirm_user_missing_code(cognito_client):
    """Test confirming a user with missing confirmation code"""
    response = confirm_user("testuser@example.com", "")

    assert response["Success"] is False
    assert response["message"] == "Confirmation code is required"


@mock_aws
def test_confirm_user_expired_code(cognito_client):
    """Test confirming a user with an expired confirmation code"""
    with patch("v1.cognito.cognito_client.confirm_sign_up") as mock_confirm:
        mock_confirm.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ExpiredCodeException",
                    "Message": "Confirmation code has expired"
                }
            },
            "confirm_sign_up"
        )

        response = confirm_user("testuser@example.com", "123456")
        assert response["Success"] is False
        assert "message" in response


@mock_aws
def test_resend_verification_code(cognito_client):
    """Test resending verification code"""
    # resgister user without confirming
    register_user("testuser@example.com", "testuser", "SecurePass123!")

    # mock successful response
    with patch(
        "v1.cognito.cognito_client.resend_confirmation_code"
    ) as mock_resend:
        mock_resend.return_value = {}

        response = resend_verification_code("testuser@example.com")

    assert response["Success"] is True


@mock_aws
@patch("v1.cognito.cognito_client.resend_confirmation_code")
def test_resend_verification_code_invalid_user(cognito_client):
    """Test resending verification code for a non-existent user"""

    with patch(
        "v1.cognito.cognito_client.resend_confirmation_code"
    ) as mock_resend:
        mock_resend.side_effect = ClientError(
            {
                "Error": {
                    "Code": "UserNotFoundException",
                    "Message": "User does not exist"
                }
            },
            "resend_verification_code"
        )

        # try resending code to a non-existent user
        response = resend_verification_code("fakeuser@example.com")

    assert response["Success"] is False
    assert "message" in response


@mock_aws
def test_resend_verification_code_missing_email(cognito_client):
    """Test resending verification code with a missing email."""
    response = resend_verification_code("")
    assert response["Success"] is False
    assert response["message"] == "Email is required"


@mock_aws
def test_login_user(cognito_client):
    """Test user login"""
    # register a user
    register_user("testuser@example.com", "testuser", "SecurePass123!")

    # Confirm user's email
    user_pool_id = (
        cognito_client.list_user_pools(MaxResults=1)
        ["UserPools"][0]["Id"]
    )
    cognito_client.admin_confirm_sign_up(
        UserPoolId=user_pool_id,
        Username="testuser@example.com"
    )

    response = login_user("testuser@example.com", "SecurePass123!")
    assert response["Success"] is True
    assert "tokens" in response


@mock_aws
def test_login_user_unconfirmed(cognito_client):
    """Test that an unconfirmed user cannot log in"""
    # Register but don't confirm the user
    register_user("testuser@example.com", "testuser", "SecurePass123!")

    # Attempt to login without confirming email
    response = login_user("testuser@example.com", "SecurePass123!")
    assert response["Success"] is False
    assert "message" in response


@mock_aws
def test_login_user_invalid_credentials(cognito_client):
    """Test user login with incorrect password"""
    response = login_user("testuser@example.com", "WrongPass!")
    assert response["Success"] is False
    assert "message" in response


def test_login_user_expired_tokens(cognito_client):
    """Test logging in with expired tokens"""
    with patch("v1.cognito.cognito_client.initiate_auth") as mock_auth:
        mock_auth.side_effect = ClientError(
            {
                "Error": {
                    "Code": "NotAuthorizedException",
                    "Message": "Tokens have expired"
                }
            },
            "initiate_auth"
        )

        response = login_user("testuser@example.com", "SecurePass123!")
        assert response["Success"] is False
        assert "message" in response


@mock_aws
def test_login_user_missing_credentials(cognito_client):
    """Test logging in with missing email or password"""
    response = login_user("", "SecurePass123!")
    assert response["Success"] is False
    assert "message" in response


@mock_aws
def test_email_exists_true(cognito_client):
    """Test email_exists returns True when the email is registered"""
    cognito_client.sign_up(
        ClientId=Config.AWS_COGNITO_CLIENT_ID,
        Username="testuser@example.com",
        Password="SecurePass123!",
        UserAttributes=[{"Name": "email", "Value": "testuser@example.com"}]
    )
    assert email_exists("testuser@example.com") is True


@mock_aws
def test_email_exists_false(cognito_client):
    """Test email_exists returns False when the email is not registered"""
    assert email_exists("nonexistent@example.com") is False


@mock_aws
@patch("v1.cognito.cognito_client.list_users")
def test_email_exists_error(mock_list_users, cognito_client):
    """Test email_exists handles Cognito API errors gracefully"""
    mock_list_users.side_effect = ClientError(
        {
            "Error": {
                "Code": "InternalError",
                "Message": "Internal server error"
            }
        },
        "list_users"
    )

    assert email_exists("testuser@example.com") is False
