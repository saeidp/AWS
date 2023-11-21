import { App, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { DynamodbSimpleLambda } from '../../construct/lambda/dynamodb/dynamodb-simple/dynamodb-simple-lambda'

const app = new App();
const stack = new Stack(app, 'my-cdk-stack', {
    env: { account: 'fakeaccount', region: 'fakeregion' }
});
new DynamodbSimpleLambda(stack, 'my-dynamodb-simple-lambda-construct');

test('EC2 instances == 1', () => {
    const template = Template.fromStack(stack);
    template.resourceCountIs('AWS::DynamoDB::Table', 1);
});

