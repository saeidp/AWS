

import { App, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { IVPCCidrProps, VPCConfig } from '../../construct/vpc/vpc-config/vpc-config'

const app = new App();
const stack = new Stack(app, 'my-cdk-stack', {
    env: { account: 'fakeaccount', region: 'fakeregion' }
});
new VPCConfig(stack, 'my-vpc-construct', { cidrBlockPath: 'test/vpc/config/vpc-config.json' });

test('VPC instances == 1', () => {
    const template = Template.fromStack(stack);
    template.resourceCountIs('AWS::EC2::VPC', 1);
});

test('Create VPC Construct with expected resources', () => {
    const template = Template.fromStack(stack);
    template.hasResourceProperties('AWS::EC2::VPC', {
        CidrBlock: '10.0.0.0/16'
    });
});


