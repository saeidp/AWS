import { App, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { S3TagObject } from '../../construct/lambda/tag/s3-tag-object'
const app = new App();
const stack = new Stack(app, 'my-cdk-stack', {
    env: { account: 'fakeaccount', region: 'fakeregion' }
});
new S3TagObject(stack, 'my-s3-tag-object-construct');

test('S3 buckets == 1', () => {
    const template = Template.fromStack(stack);
    template.resourceCountIs('AWS::S3::Bucket', 1);
});

test('lambda function with expected resources', () => {
    const template = Template.fromStack(stack);
    template.hasResourceProperties('AWS::Lambda::Function', {
        Environment: {
            Variables: {
                TAG_KEY: 'my-key',
                TAG_VALUE: 'my-value'
            }
        }
    });
});

