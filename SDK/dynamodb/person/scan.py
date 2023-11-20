import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-2")
session = boto3.Session(profile_name="default", region_name="ap-southeast-2")
# dynamodb = session.client("dynamodb")
dynamodb = session.resource('dynamodb')

# Select the DynamoDB table
table = dynamodb.Table('Person')

response = table.scan()
items = response["Items"]

for item in items:
    print(item)