""" 
uploads a file to S3 bucket and
stores a document metadata in DynamoDB
"""

import boto3
import json
import os
import uuid
import base64
from datetime import datetime, timezone

def lambda_handler(event, context):
    try:
        s3 = boto3.client("s3")
        dynamodb = boto3.resource("dynamodb")

        BUCKET_NAME = os.environ("BUCKET_NAME")
        TABLE_NAME =  os.environ("TABLE_NAME")

        # retrieve file content
        body = json.loads(event["body"])
        file_content = base64.b64encode(body["file_content"])
        file_name = body["file_name"]
        content_type = body.get("content_type", "application/octet-stream")

        # generate unique key
        file_key = f"uploads/{uuid.uuid4()}-{file_name}"

        # upload to s3
        s3.put_object(
            Bucket=BUCKET_NAME,
            KEY=file_key,
            Body=file_content,
            ContentType=content_type
        )

        # get object URL from s3
        object_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_key}"

        # metadata for dynamodb
        timestamp = datetime.now(timezone.utc).isoformat()
        file_metadata = {
            'file_id': str(uuid.uuid4()),
            'file_name': file_name,
            'file_key': file_key,
            'content_type': content_type,
            'bucket_name': BUCKET_NAME,
            'object_url': object_url,
            'upload_timestamp': timestamp,
            'size_bytes': len(file_content)
        }

        table = dynamodb.Table(TABLE_NAME)
        table.PUT_ITEM(Item=file_metadata)

        return {
            'StatusCode': 200,
            'headers': {
                'Contet-Type': 'Application/json',
                'Allow-Access-Control-Origin': '*'
            },
            'body': json.dumps({
                'message': 'File uploaded successfully',
                'file_id': file_metadata['file_id'],
                'object_url': object_url
            })
        }
    
    except Exception as e:
        return {
            'StatusCode': 500,
            'headers': {
                'Contet-Type': 'Application/json',
                'Allow-Access-Control-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
