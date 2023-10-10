import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export interface IVPCCidrProps {
    cidrBlock: string
}

export class VPCSimple extends Construct {
    constructor(scope: Construct, id: string, cidrProps?: IVPCCidrProps) {
        super(scope, id);

        let cidr = '10.0.0.0 / 16';
        if (cidrProps) {
            cidr = cidrProps.cidrBlock
        }

        const vpc = new ec2.Vpc(this, 'my-construct-vpc', {
            // nap instance
            // natGatewayProvider: ec2.NatProvider.instance({
            //     instanceType: new ec2.InstanceType('t2.micro'),
            // }),
            ipAddresses: ec2.IpAddresses.cidr(cidr),
            natGateways: 1,
            maxAzs: 3,
            subnetConfiguration: [
                {
                    name: 'starter-private-subnet',
                    subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidrMask: 24
                },
                {
                    name: 'starter-public-subnet',
                    subnetType: ec2.SubnetType.PUBLIC,
                    cidrMask: 24,
                },
                {
                    name: 'starter-isolated-subnet',
                    subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
                    cidrMask: 28,
                },

            ]
        })

    }
}