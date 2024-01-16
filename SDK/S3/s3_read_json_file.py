from logging import exception
import boto3
import json

s3 = boto3.resource('s3')
try:

    content_object = s3.Object('student-management-configuration-369025142683', 'student-selection_criteria.json')
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    print(json_content)

except Exception as error:
    print("Error while connecting to S3 bucket", error)



