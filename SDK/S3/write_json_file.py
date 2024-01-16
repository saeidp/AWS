import boto3

# Initialize a boto3 S3 client
s3 = boto3.client('s3')

# Specify your file paths and bucket details
file_name = 'path/to/person.json'  # Update this to the path of your file on your desktop
# # You can get the directory of the scripr and upload the file from there
# import os
# # Get the directory of the script
# directory = os.path.dirname(os.path.realpath(__file__))
# # Create a new file path
# file_name = os.path.join(directory, 'person.json')

bucket_name = 'mybucket'
object_key = 'myfolder/person.json'

# Upload the file to S3
try:
    s3.upload_file(file_name, bucket_name, object_key)
    print(f"File {file_name} has been uploaded to s3://{bucket_name}/{object_key}")
except Exception as e:
    print("Error occurred while uploading the file:", e)




