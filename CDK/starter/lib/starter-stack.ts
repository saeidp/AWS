import * as cdk from 'aws-cdk-lib';
import { VPC } from '../construct/vpc/vpc';
import { EC2 } from '../construct/ec2/ec2'

export class StarterStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // const vpc = new VPC(this, 'my-cdk-vpc');
    const ec2 = new EC2(this, 'my-cdk-ec2');

  }
}
