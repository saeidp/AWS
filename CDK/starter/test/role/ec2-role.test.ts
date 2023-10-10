import { App, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { Ec2Role } from '../../construct/role/Ec2Role';

const app = new App();
const stack = new Stack(app, 'my-cdk-stack', {
    env: { account: 'fakeaccount', region: 'fakeregion' }
});

new Ec2Role(stack, 'my-ec2Role-construct');

test('Roles == 1', () => {
    const template = Template.fromStack(stack);
    template.resourceCountIs('AWS::IAM::Role', 1);
});

test('S3 Construct with expected resources', () => {
    const template = Template.fromStack(stack);
    template.hasResourceProperties('AWS::IAM::Role', {
        RoleName: 'ec2Role'
    });
});
