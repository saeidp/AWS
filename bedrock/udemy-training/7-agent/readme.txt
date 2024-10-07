This sample agent is to illustrate how an agent is able to run lambda and kb to augment the query and get the appropriate result
You must follow the steps below:

1. Create a DynamoDB Table with the customer account details - TableName - customerAccountStatus
2. Create a AWS Lambda function to retrieve the data from DynamoDB Table – Lambda Function - newBankAccountStatus
3. Define OpenAPI schemas for Bedrock Agent Action Group and Upload on S3 Bucket- Link1
	• S3 bucket details for OpenAPI Schema file - accountstatusopenapi
4. Create the Bedrock Agent from console - bankofchicago-agent
5. Update the Lambda function Permissions with Agent Invocation Details
6. Update the Lambda Function Code to allow Bedrock Agent to send request/response in a defined format - Link2
7. Create Bedrock Knowledge Base (RAG solution) & update the details in the Action Group – S3 Bucket -bankingagentknowledgebase
8. Test the Agent
	
DynamoDB table structure
Table Name: customerAccountStatus
Columns:
AccountID (Pimary key) Number   5555, 6666, 7777
AccountName String John, Thomas, Manju
AccountStatus: String Active, Pending, Pending
Reason: String Active, InvalidIdentification, InvalidAddressProof

lambda
newBankAccountStatus
you need to add  dynamodb full access to the lambda role
you also need to edit lambda function resource policy and give bedrock full access



Link1: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-api-schema.html
Link2: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html

Lambda steps
1. Import boto3 and create client connection
with DynamoDB - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html

2. Print event value and store the event details in a variable

3. Create a request syntax to retrieve data from the DynamoDB Table using GET Item method
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/table/get_item.html

4. Store and print the response

5. Format the response as per the requirement of Bedrock Agent Action Group
- https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html

6. Print the final response

Then OpenAPI Schema

1. Refer to the AWS sample OpenAI schemas -https://docs.aws.amazon.com/bedrock/latest/userguide/agents-api-schema.html
2. Convert to YAML
3. Modify the Schema as per the requirement of the use case
4. Create an S3 bucket and store the Open API Schema in the S3 bucket
