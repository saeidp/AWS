import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import path = require("path");
import { NodejsFunction, NodejsFunctionProps } from "aws-cdk-lib/aws-lambda-nodejs";

export class LambdaWithLayer extends Construct {
    constructor(scope: Construct, id: string,) {
        super(scope, id);
        const logicLayer = new lambda.LayerVersion(this, 'logic-layer', {
            compatibleRuntimes: [
                lambda.Runtime.NODEJS_18_X,
                lambda.Runtime.NODEJS_16_X,
            ],
            layerVersionName: 'business-logic-layer',
            // code: lambda.Code.fromAsset(path.join(__dirname, '/../../../applications/cloudwatch-lambda')),
            code: lambda.Code.fromAsset('applications/layer-lambda/layers/business-logic'),
            description: 'Business logic layer',
        });

        const nodeJsFnProps: NodejsFunctionProps = {
            bundling: {
                externalModules: [
                    'aws-sdk', // Use the 'aws-sdk' available in the Lambda runtime
                ],
            },
            runtime: lambda.Runtime.NODEJS_18_X,
            timeout: cdk.Duration.minutes(3),
            memorySize: 256,
        };

        const lambdaWithLayer = new NodejsFunction(this, 'lambdaWithLayer', {
            entry: path.join(__dirname, '../../../applications/layer-lambda/lambdas', 'lambda.ts'),
            ...nodeJsFnProps,
            functionName: 'lambdaWithLayer',
            handler: 'handler',
            layers: [logicLayer],
        });

    }
}