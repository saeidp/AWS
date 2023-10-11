import { App, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { KmsSimple } from '../../construct/kms/kms-simple/kms-simple';

const app = new App();
const stack = new Stack(app, 'my-cdk-stack', {
    env: { account: 'fakeaccount', region: 'fakeregion' }
});
const bucketName = 'saeid-test-bucket-1258'
new KmsSimple(stack, 'my-kms-construct');

test('S3 buckets == 1', () => {
    const template = Template.fromStack(stack);
    template.resourceCountIs('AWS::S3::Bucket', 1);
});

test('kms key == 1', () => {
    const template = Template.fromStack(stack);
    template.resourceCountIs('AWS::KMS::Key', 1);
});

test('S3 Construct with expected resources', () => {
    const template = Template.fromStack(stack);
    template.hasResourceProperties('AWS::KMS::Key', {
        EnableKeyRotation: false,
    });
});

test('S3 Construct with expected resources', () => {
    const template = Template.fromStack(stack);
    template.hasResourceProperties('AWS::KMS::Alias', {
        AliasName: 'alias/kms-simple',
    });
});
