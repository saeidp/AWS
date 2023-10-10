import { readFileSync } from 'fs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';
import path = require('path');
import { readVpcConfig } from './utils/vpc-config-io';

export interface IVPCCidrProps {
    readonly cidrBlockPath?: string,
}

export class VPCConfig extends Construct {
    constructor(scope: Construct, id: string, { cidrBlockPath = path.join(__dirname, '../config/vpc-config.json') }: IVPCCidrProps) {
        super(scope, id);
        console.log(cidrBlockPath);

        const config = readVpcConfig(cidrBlockPath);
        const { cidrBlock } = config

        console.log(cidrBlock)

        const vpc = new ec2.Vpc(this, 'my-construct-vpc', {
            ipAddresses: ec2.IpAddresses.cidr(cidrBlock),
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