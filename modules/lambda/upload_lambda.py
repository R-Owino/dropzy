""" 
uploads a file to S3 bucket,
triggers Macie to scan the document and
store the document metadata in DynamoDB
"""

import boto3
