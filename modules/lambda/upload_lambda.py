""" 
uploads a file to S3 bucket
stores a file's metadata in a DynamoDB table
"""

import boto3
import json
import os
import uuid
import logging
from datetime import datetime, timezone

logger = logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
TABLE_NAME =  os.environ["DYNAMODB_TABLE_NAME"]

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        if isinstance(event["body"], str):
            body = json.loads(event["body"])
        else:
            body = event["body"]

        logger.info(f"Parsed body: {json.dumps("body")}")

        # retrieve file content
        file_content = body["file_content"]
        file_name = body["file_name"]
        content_type = body.get("content_type", "application/octet-stream")

        # generate unique key
        file_key = f"uploads/{uuid.uuid4()}-{file_name}"

        # upload to s3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=file_content,
            ContentType=content_type
        )

        # metadata for dynamodb
        timestamp = datetime.now(timezone.utc).isoformat()
        file_metadata = {
            'DocumentId': str(uuid.uuid4()),
            'file_name': file_name,
            'file_key': file_key,
            'content_type': content_type,
            'object_url': f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_key}",
            'upload_timestamp': timestamp,
            'size_bytes': len(file_content)
        }

        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item=file_metadata)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'message': 'File uploaded successfully',
                'DocumentId': file_metadata['DocumentId'],
                'object_url': file_metadata['object_url']
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
