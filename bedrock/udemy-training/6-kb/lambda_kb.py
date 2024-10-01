# This lambda needs to have knowledge base created first.
# Create a s3 bucket
# copy the pdf files to s3
# Create Knowledge Base in Bedrock
# select an embedding model while generating the knowledge base such as cohere embed english v3
# select above s3 bucket name
# for vector database use Open Search serverless
# for foundation model use anthropic.claude-3-haiku-20240307-v1:0
# KB creates its role to make it able to invoke model (embed) and opensearch and S3 access
# for lambda role you need to add bedrock access (full access)

import json
import boto3

client_bedrock_kb = boto3.client('bedrock-agent-runtime')


def lambda_handler(event, context):
    print(event['prompt'])
    user_prompt=event['prompt']
    # 4. Use retrieve and generate API
    response_kb = client_bedrock_kb.retrieve_and_generate(
    input={
        'text': user_prompt
    },
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'MO8QZQR9NF',
            'modelArn': 'arn:aws:bedrock:ap-southeast-2::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
                }
            })
   
    print(response_kb)
    response_kb_final=response_kb['output']['text']
    return {
        'statusCode': 200,
        'body': response_kb_final
        }
