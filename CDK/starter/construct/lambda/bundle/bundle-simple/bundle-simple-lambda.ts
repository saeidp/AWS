import { Duration } from 'aws-cdk-lib';
import { Function, Code, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

import path = require('path');

export class BundleSimpleLambda extends Construct {

    constructor(scope: Construct, id: string) {
        super(scope, id);

        const bundleLambda = new Function(this, 'bundle-lambda', {
            code: Code.fromAsset(path.join(__dirname, '../../../../applications/bundle-simple-lambda'), {
                bundling: {
                    image: Runtime.PYTHON_3_10.bundlingImage,
                    command: [
                        'bash',
                        '-c',
                        'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output',
                    ],
                },
            }),
            runtime: Runtime.PYTHON_3_10,
            memorySize: 1024,
            handler: 'bundle_simple_lambda.handler',
            timeout: Duration.minutes(5),
        });
    }
}