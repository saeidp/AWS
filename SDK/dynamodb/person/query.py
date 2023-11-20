import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-2")
session = boto3.Session(profile_name="default", region_name="ap-southeast-2")
# dynamodb = session.client("dynamodb")
dynamodb = session.resource('dynamodb')

# Select the DynamoDB table
table = dynamodb.Table('Person')

query_parameters = {
    'KeyConditionExpression': 'id = :id_value',
    'ExpressionAttributeValues': {
        ':id_value': '1'  # Replace with the actual 'id' you're querying for
    }
}

# Perform the query
response = table.query(**query_parameters)

# Print out the items returned from the query
for item in response['Items']:
    print(item)