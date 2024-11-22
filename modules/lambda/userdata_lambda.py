""" saves user data to a DynamoDB table on successful signups """

import json
import boto3
import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # get the user data from the event
    username = event['request']['userAttributes']['username']
    email = event['request']['userAttributes']['email']

    # connect to dynamodb
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('userdata')

    try:
        # save the user data to the table
        response = table.put_item(
            Item={
                'userId': username,
                'username': username,
                'email': email,
                'createdAt': str(datetime.now())
            },
            ConditionExpression='attribute_not_exists(userId)'
        )
        print(f"User data saved: {response}")
        return event
    except ClientError as e:
        # if the user already exists, return an error
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 400,
                'body': json.dumps('User already exists')
            }
        else:
            print(f"Error saving user data: {e}")
            raise e
