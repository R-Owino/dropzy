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
TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]


def lambda_handler(event, context):
    logger.info(f"Lambda function version: {context.function_version}")
    logger.info(f"Event source: {event.get('eventSource')}")

    try:
        for record in event["Records"]:
            if record["eventName"].startswith("ObjectCreated:"):
                bucket_name = record["s3"]["bucket"]["name"]
                file_key = record["s3"]["object"]["key"]
                size_bytes = record["s3"]["object"]["size"]

                # get the filename
                file_name = file_key.split('/')[1]

                # query existing entries with the same filename
                table = dynamodb.Table(TABLE_NAME)
                response = table.scan(
                    FilterExpression='file_name = :filename',
                    ExpressionAttributeValues={':filename': file_name}
                )

                # if it exists, update the existing entry
                existing_items = response.get('Items', [])
                if existing_items:
                    existing_item = existing_items[0]
                    table.update_item(
                        Key={'DocumentId': existing_item['DocumentId']},
                        UpdateExpression=(
                            'SET file_key = :new_key, '
                            'object_url = :new_url, '
                            'upload_timestamp = :new_timestamp, '
                            'size_bytes = :new_size'
                        ),
                        ExpressionAttributeValues={
                            ':new_key': file_key,
                            ':new_url': (
                                f"https://{bucket_name}.s3.amazonaws.com/"
                                f"{file_key}"
                            ),
                            ':new_timestamp': (
                                datetime.now(timezone.utc).isoformat()
                            ),
                            ':new_size': size_bytes
                        }
                    )
                    logger.info(f"Updated metadata for {file_name}")
                else:
                    # create a new entry if no existing entry
                    file_metadata = {
                        'DocumentId': str(uuid.uuid4()),
                        'file_name': file_name,
                        'file_key': file_key,
                        'object_url': (
                            f"https://{bucket_name}.s3.amazonaws.com/"
                            f"{file_key}"
                        ),
                        'upload_timestamp': (
                            datetime.now(timezone.utc).isoformat()
                        ),
                        'size_bytes': size_bytes
                    }

                    table.put_item(Item=file_metadata)
                    logger.info(
                        f"Metadata for {file_name} stored successfully"
                    )

        return {
            'statusCode': 200,
            'body': json.dumps("File metadata stored successfully")
        }
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        logger.error(f"Event structure: {json.dumps(event)}")
        raise
