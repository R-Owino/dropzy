""" fetches a file metadata from the documents table """

import boto3
import json
import os
from boto3.dynamodb.conditions import key

def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource("dynamodb")
        TABLE_NAME = os.environ["TABLE_NAME"]
        table = dynamodb.Table(TABLE_NAME)

        response = table.scan()
        files = response.get("Items", [])

        sorted_files = sorted(files, key=lambda x: x["upload_timestamp"], reverse=True)

        recent_files = sorted_files[:15]

        return {
            'statusCode': 200,
            'body': json.dumps({'files': recent_files})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
