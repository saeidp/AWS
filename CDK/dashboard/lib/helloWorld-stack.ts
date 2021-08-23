import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda-nodejs';
import { Runtime } from '@aws-cdk/aws-lambda';
import * as path from 'path';

export class HelloWorldStack extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const helloWorld = new lambda.NodejsFunction(this, 'HelloWorldLambda', {
            runtime: Runtime.NODEJS_14_X,
            entry: path.join(__dirname, '..', 'api', 'hello-world', 'index.ts'),
            functionName: 'HelloWorld',
            handler: 'helloWorld',
        });

    }
}
