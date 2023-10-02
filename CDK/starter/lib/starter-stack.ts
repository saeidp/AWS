import * as cdk from 'aws-cdk-lib';
import { VPC } from '../construct/vpc/vpc';

export class StarterStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new VPC(this, 'my-cdk-vpc');

  }
}
