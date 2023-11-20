import boto3
from botocore.exceptions import NoCredentialsError, ClientError

session = boto3.Session(profile_name="default", region_name="ap-southeast-2")
# dynamodb = session.client("dynamodb")
dynamodb = session.resource('dynamodb')

table = dynamodb.Table('Person')
primary_key = {'id': '1', 'name': 'John'}

update_expression = "SET course = :new_course"

# Define the values to be used in the update expression
expression_attribute_values = {
    ":new_course": "Data Science"
}

try:
    response = table.update_item(
        Key=primary_key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
    )
    print("Update item succeeded:", response)
except ClientError as e:
    print("Update item failed:", e.response['Error']['Message'])