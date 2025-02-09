""" saves user data to a DynamoDB table on successful signups """

import os
import json
import boto3
import datetime
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function to handle post-confirmation user signup
    Stores user information in DynamoDB
    """
    # get the user data from the event
    username = event['request']['userAttributes']['preferred_username']
    email = event['request']['userAttributes']['email']

    # connect to dynamodb
    dynamodb = boto3.resource("dynamodb")
    TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]

    curr_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        # save the user data to the table
        table = dynamodb.Table(TABLE_NAME)
        response = table.put_item(
            Item={
                'UserId': email,
                'Username': username,
                'CreatedAt': curr_time,
                'LastLogin': curr_time
            },
            ConditionExpression='attribute_not_exists(UserId)'
        )
        logger.info(f"User data saved: {response}")
        return event
    except ClientError as e:
        # if the user already exists, return an error
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 400,
                'body': json.dumps('User already exists')
            }
        else:
            logger.error(f"Error saving user data: {e}")
            raise e
