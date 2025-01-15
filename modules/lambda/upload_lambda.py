""" 
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

dynamodb = boto3.resource("dynamodb")

TABLE_NAME =  os.environ["DYNAMODB_TABLE_NAME"]

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        for record in event["Records"]:
            if record["eventName"] == "ObjectCreated:Put":
                bucket_name = record["s3"]["bucket"]["name"]
                file_key = record["s3"]["object"]["key"]
                size_bytes = record["s3"]["object"]["size"]

                # get the filename
                base_name = os.path.basename(file_key)
                file_name = '-'.join(base_name.split('-')[5:])

                # metadata for dynamodb
                timestamp = datetime.now(timezone.utc).isoformat()
                file_metadata = {
                    'DocumentId': str(uuid.uuid4()),
                    'file_name': file_name,
                    'file_key': file_key,
                    'object_url': f"https://{bucket_name}.s3.amazonaws.com/{file_key}",
                    'upload_timestamp': timestamp,
                    'size_bytes': size_bytes
                }

                table = dynamodb.Table(TABLE_NAME)
                table.put_item(Item=file_metadata)

                logger.info(f"Metadata for {file_name} stored successfully")  

        return {
            'statusCode': 200,
            'body': json.dumps("File metadata stored successfully")
        }
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        logger.error(f"Event structure: {json.dumps(event)}")
        raise
