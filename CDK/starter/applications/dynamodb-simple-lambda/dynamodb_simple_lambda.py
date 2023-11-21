import json
import boto3
from botocore.exceptions import ClientError

def handler(event, context):
    # Initialize a boto3 DynamoDB client
    dynamodb = boto3.resource('dynamodb')

    # Select the DynamoDB table
    table = dynamodb.Table('Person')

    try:
        # Perform the scan operation
        response = table.scan()

        # Get the items from the response
        items = response['Items']

        # Return the scan result
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
    except ClientError as e:
        # Handle the exception
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }