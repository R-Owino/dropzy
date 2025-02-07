#!/usr/bin/python3

import pytest
import boto3
from moto import mock_aws
from botocore.exceptions import ClientError
from v1.cognito import (register_user,
                        confirm_user,
                        resend_verification_code,
                        login_user)
from v1.config import Config
from unittest.mock import patch


@pytest.fixture
def cognito_client():
    """Mock AWS Cognito client"""
    with mock_aws():
        client = boto3.client("cognito-idp", region_name=Config.AWS_REGION)
        client.create_user_pool(PoolName="test_pool")
        user_pool_id = (
            client.list_user_pools(MaxResults=1)
            ["UserPools"][0]["Id"]
        )
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
    response = register_user("test@example.com", "testuser", "SecurePass123!")
    assert response["Success"] is True


@mock_aws
def test_register_user_existing(cognito_client):
    """Test registering a user that already exists"""
    cognito_client.sign_up(
        ClientId=Config.AWS_COGNITO_CLIENT_ID,
        Username="test@example.com",
        Password="SecurePass123!",
        UserAttributes=[{"Name": "email", "Value": "test@example.com"}]
    )
    response = register_user("test@example.com", "testuser", "SecurePass123!")
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
        Username="test@example.com"
    )
    response = confirm_user("test@example.com", "123456")
    assert response["Success"] is True


@mock_aws
def test_confirm_user_invalid_code(cognito_client):
    """Test confirming a user with an invalid code"""
    response = confirm_user("test@example.com", "000000")
    assert response["Success"] is False
    assert "message" in response


@mock_aws
def test_resend_verification_code(cognito_client):
    """Test resending verification code"""
    # resgister user without confirming
    register_user("test@example.com", "testuser", "SecurePass123!")

    # mock successful response
    with patch(
        "v1.cognito.cognito_client.resend_confirmation_code"
    ) as mock_resend:
        mock_resend.return_value = {}

        response = resend_verification_code("test@example.com")

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
def test_login_user(cognito_client):
    """Test user login"""
    # register a user
    register_user("test@example.com", "testuser", "SecurePass123!")

    # Confirm user's email
    user_pool_id = (
        cognito_client.list_user_pools(MaxResults=1)
        ["UserPools"][0]["Id"]
    )
    cognito_client.admin_confirm_sign_up(
        UserPoolId=user_pool_id,
        Username="test@example.com"
    )

    response = login_user("test@example.com", "SecurePass123!")
    assert response["Success"] is True
    assert "tokens" in response


@mock_aws
def test_login_user_unconfirmed(cognito_client):
    """Test that an unconfirmed user cannot log in"""
    # Register but don't confirm the user
    register_user("test@example.com", "testuser", "SecurePass123!")

    # Attempt to login without confirming email
    response = login_user("test@example.com", "SecurePass123!")
    assert response["Success"] is False
    assert "message" in response


@mock_aws
def test_login_user_invalid_credentials(cognito_client):
    """Test user login with incorrect password"""
    response = login_user("test@example.com", "WrongPass!")
    assert response["Success"] is False
    assert "message" in response
