import { App, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { EC2 } from '../construct/ec2/ec2'

const app = new App();
const stack = new Stack(app, 'my-cdk-stack', {
    env: { account: 'fakeaccount', region: 'fakeregion' }
});
new EC2(stack, 'my-ec2-construct');

test('EC2 instances == 1', () => {
    const template = Template.fromStack(stack);
    template.resourceCountIs('AWS::EC2::Instance', 1);
});

test('Create Dataset Construct with expected resources', () => {
    const template = Template.fromStack(stack);
    template.hasResourceProperties('AWS::EC2::Instance', {
        InstanceType: 't2.micro'
    });
});

