

import { App, Stack } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { IVPCCidrProps, VPCSimple } from '../../construct/vpc/vpc-simple/vpc-simple'

// Parameterized stack
describe('Test the VPC using the createStack function', () => {
    const createStack = (props: IVPCCidrProps) => {
        const app = new App();
        const stack = new Stack(app, 'MyTestStack', {
            env: {
                account: '1234567890',
                region: 'ap-southeast-2'
            }
        });

        new VPCSimple(stack, 'test-VPC-construct', props);

        return stack;
    };
    const stack = createStack({ cidrBlock: '10.1.0.0/16' })
    test('VPC instances == 1', () => {
        const template = Template.fromStack(stack);
        template.resourceCountIs('AWS::EC2::VPC', 1);
    });

    test('Create VPC Construct with expected resources', () => {
        const template = Template.fromStack(stack);
        template.hasResourceProperties('AWS::EC2::VPC', {
            CidrBlock: '10.1.0.0/16'
        });
    });
})

// unparameterized stack
const app = new App();
const stack = new Stack(app, 'my-cdk-stack', {
    env: { account: 'fakeaccount', region: 'fakeregion' }
});
new VPCSimple(stack, 'my-vpc-construct');

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


