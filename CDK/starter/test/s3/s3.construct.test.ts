import { App, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { S3 } from '../../construct/s3/s3'

const app = new App();
const stack = new Stack(app, 'my-cdk-stack', {
    env: { account: 'fakeaccount', region: 'fakeregion' }
});
const bucketName = 'saeid-test-bucket-1258'
new S3(stack, 'my-s3-construct', {
    bucketName: bucketName
});

test('S3 buckets == 1', () => {
    const template = Template.fromStack(stack);
    template.resourceCountIs('AWS::S3::Bucket', 1);
});

test('S3 Construct with expected resources', () => {
    const template = Template.fromStack(stack);
    template.hasResourceProperties('AWS::S3::Bucket', {
        BucketName: bucketName,
    });
});

