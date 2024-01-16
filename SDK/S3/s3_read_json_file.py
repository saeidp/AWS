# --------------------------- Read A json file from a bucket ----------------------------
# Read a file called person.json that has name and age as key value
import boto3
import json

# Initialize a boto3 S3 client
s3 = boto3.client('s3')

# Specify the bucket name and object key
bucket_name = 'mybucket'
object_key = 'myfolder/person.json'

# Retrieve the file from S3
try:
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    
    # Read the content of the file
    content = response['Body'].read().decode('utf-8')
    data = json.loads(content)
    
    # Display the content
    print("Name:", data['name'])
    print("Age:", data['age'])

except Exception as e:
    print("Error occurred while reading the file:", e)


# ----------------------------------------------- A similar way ---------------------------------------
# import boto3
# import json

# s3 = boto3.resource('s3')
# try:

#     content_object = s3.Object('student-management-configuration-369025142683', 'student-selection_criteria.json')
#     file_content = content_object.get()['Body'].read().decode('utf-8')
#     json_content = json.loads(file_content)

#     print(json_content)

# except Exception as error:
#     print("Error while connecting to S3 bucket", error)


