
import * as cdk from 'aws-cdk-lib';
import * as ec2 from "aws-cdk-lib/aws-ec2"
import { Construct } from 'constructs';

export class VPCLookup extends Construct {
    constructor(scope: Construct, id: string) {
        super(scope, id);
        const subnetIds = ["subnet-0f77c9e4d868396e7", "subnet-09d3bd26e5be49dfa"]
        const selectedDestinationServicePrivateSubnets: ec2.ISubnet[] = [];
        const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
          vpcId: 'vpc-0959d6b9075075d4e'
        });
    
        subnetIds.forEach((subnetId) => {
          const validSubnet = vpc.privateSubnets.find((subnet: ec2.ISubnet) => subnet.subnetId === subnetId);
          if (validSubnet) {
            selectedDestinationServicePrivateSubnets.push(validSubnet);
          }
        });
    
        console.log("vpc: ", vpc.vpcId);
        console.log("found subnets length: ", selectedDestinationServicePrivateSubnets.length)
        console.log("foundsubnets: ", selectedDestinationServicePrivateSubnets);        

    }
}